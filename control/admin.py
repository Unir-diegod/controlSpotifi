from django.contrib import admin

from .models import Member, Payment


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "monthly_fee", "is_active", "joined_at")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("member", "amount", "paid_at", "method")
    list_filter = ("method", "paid_at")
    search_fields = ("member__name",)
