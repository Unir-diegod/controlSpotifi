from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Member, Payment
from .views import month_summary


class FamilyControlTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="admin",
            password="test-password",
        )
        self.client.force_login(user)
        self.member = Member.objects.create(name="Carlos", monthly_fee=10000)

    def test_dashboard_uses_template_and_database_data(self):
        Payment.objects.create(
            member=self.member,
            amount=4000,
            paid_at=date.today().replace(day=1),
            method=Payment.Method.NEQUI,
        )

        response = self.client.get(reverse("control:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "control/dashboard.html")
        self.assertContains(response, "Carlos")
        self.assertContains(response, "$ 4.000")
        self.assertContains(response, "40%")

    def test_payment_form_persists_payment(self):
        response = self.client.post(
            reverse("control:payments"),
            {
                "member": self.member.pk,
                "amount": 10000,
                "paid_at": date.today().isoformat(),
                "method": Payment.Method.NEQUI,
            },
        )

        self.assertRedirects(response, reverse("control:payments"))
        self.assertEqual(Payment.objects.count(), 1)

    def test_members_form_creates_member(self):
        response = self.client.post(
            reverse("control:members"),
            {"name": "María", "monthly_fee": 10000},
        )

        self.assertRedirects(response, reverse("control:members"))
        self.assertTrue(Member.objects.filter(name="María").exists())

    def test_members_and_reports_use_django_templates(self):
        members_response = self.client.get(reverse("control:members"))
        reports_response = self.client.get(reverse("control:reports"))
        payments_response = self.client.get(reverse("control:payments"))

        self.assertTemplateUsed(members_response, "control/members.html")
        self.assertTemplateUsed(reports_response, "control/reports.html")
        self.assertTemplateUsed(payments_response, "control/payments.html")
        self.assertContains(members_response, "Nuevo integrante")
        self.assertContains(members_response, 'data-bs-target="#memberModal"')
        self.assertContains(reports_response, "Estado de los pagos")
        self.assertContains(
            payments_response,
            f'value="{date.today().isoformat()}"',
        )

    def test_invalid_member_submission_returns_modal_with_validation_error(self):
        response = self.client.post(
            reverse("control:members"),
            {"name": "", "monthly_fee": 10000},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-open-modal")
        self.assertContains(response, "Este campo es obligatorio.")

    def test_month_summary_counts_partial_and_missing_payments(self):
        second_member = Member.objects.create(name="Laura", monthly_fee=10000)
        Payment.objects.create(
            member=self.member,
            amount=6000,
            paid_at=date.today().replace(day=1),
            method=Payment.Method.TRANSFER,
        )

        summary = month_summary(date.today())
        by_name = {member.name: member for member in summary["members"]}

        self.assertEqual(summary["total_expected"], 20000)
        self.assertEqual(summary["total_received"], 6000)
        self.assertEqual(summary["total_pending"], 14000)
        self.assertEqual(by_name["Carlos"].payment_status, "partial")
        self.assertEqual(by_name[second_member.name].payment_status, "pending")

    def test_dashboard_progress_is_capped_when_overpaid(self):
        Payment.objects.create(
            member=self.member,
            amount=15000,
            paid_at=date.today(),
            method=Payment.Method.NEQUI,
        )

        summary = month_summary(date.today())

        self.assertEqual(summary["progress"], 100)
        self.assertEqual(summary["total_received"], 15000)

    def test_dashboard_redirects_anonymous_users_to_login(self):
        self.client.logout()

        response = self.client.get(reverse("control:dashboard"))

        self.assertRedirects(
            response,
            f"{reverse('control:login')}?next={reverse('control:dashboard')}",
        )
