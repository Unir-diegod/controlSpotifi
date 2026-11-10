from calendar import monthrange
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import MemberForm, PaymentForm
from .models import Member, Payment


def month_summary(month: date):
    payment_period = Q(
        payments__paid_at__year=month.year,
        payments__paid_at__month=month.month,
    )
    members = list(
        Member.objects.filter(is_active=True).annotate(
            month_received=Coalesce(
                Sum("payments__amount", filter=payment_period),
                0,
            ),
            last_payment=Max("payments__paid_at", filter=payment_period),
        )
    )

    for member in members:
        member.pending_amount = max(member.monthly_fee - member.month_received, 0)
        if member.pending_amount == 0:
            member.payment_status = "paid"
        elif member.month_received:
            member.payment_status = "partial"
        else:
            member.payment_status = "pending"

    expected = sum(member.monthly_fee for member in members)
    received = sum(member.month_received for member in members)
    pending = sum(member.pending_amount for member in members)
    progress = min(round(received * 100 / expected), 100) if expected else 0
    paid_count = sum(member.payment_status == "paid" for member in members)
    pending_count = len(members) - paid_count
    paid_percent = round(paid_count * 100 / len(members)) if members else 0

    return {
        "members": members,
        "total_expected": expected,
        "total_received": received,
        "total_pending": pending,
        "paid_count": paid_count,
        "pending_count": pending_count,
        "paid_percent": paid_percent,
        "pending_percent": 100 - paid_percent if members else 0,
        "progress": progress,
    }


def shared_context():
    month = timezone.localdate().replace(day=1)
    summary = month_summary(month)
    summary.update(
        {
            "month": month,
            "member_form": MemberForm(),
            "payment_form": PaymentForm(),
        }
    )
    return summary


@login_required
def dashboard(request):
    context = shared_context()
    context["active_page"] = "dashboard"
    context["recent_payments"] = Payment.objects.filter(
        paid_at__year=context["month"].year,
        paid_at__month=context["month"].month,
    ).select_related("member")[:5]
    context["days_in_month"] = monthrange(
        context["month"].year,
        context["month"].month,
    )[1]
    return render(request, "control/dashboard.html", context)


@login_required
def members(request):
    form = MemberForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "El integrante se agregó correctamente.")
        return redirect("control:members")

    context = shared_context()
    context.update(
        {
            "form": form,
            "member_form": form,
            "active_page": "members",
        }
    )
    return render(request, "control/members.html", context)


@login_required
def payments(request):
    form = PaymentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        payment = form.save()
        messages.success(
            request,
            f"Pago de {payment.member} registrado correctamente.",
        )
        return redirect("control:payments")

    context = shared_context()
    context.update(
        {
            "form": form,
            "payment_form": form,
            "active_page": "payments",
            "payments": Payment.objects.filter(
                paid_at__year=context["month"].year,
                paid_at__month=context["month"].month,
            ).select_related("member"),
        }
    )
    return render(request, "control/payments.html", context)


@login_required
def reports(request):
    context = shared_context()
    context["active_page"] = "reports"
    context["days_in_month"] = monthrange(
        context["month"].year,
        context["month"].month,
    )[1]
    return render(request, "control/reports.html", context)
