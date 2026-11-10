from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Member(models.Model):
    name = models.CharField("nombre", max_length=100)
    monthly_fee = models.PositiveIntegerField(
        "cuota mensual",
        default=10000,
        validators=[MinValueValidator(1)],
    )
    is_active = models.BooleanField("activo", default=True)
    joined_at = models.DateField("fecha de registro", default=timezone.localdate)

    class Meta:
        ordering = ["name"]
        verbose_name = "integrante"
        verbose_name_plural = "integrantes"

    def __str__(self):
        return self.name


class Payment(models.Model):
    class Method(models.TextChoices):
        NEQUI = "nequi", "Nequi"
        DAVIPLATA = "daviplata", "Daviplata"
        TRANSFER = "transferencia", "Transferencia"
        CASH = "efectivo", "Efectivo"

    member = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="integrante",
    )
    amount = models.PositiveIntegerField(
        "valor recibido",
        validators=[MinValueValidator(1)],
    )
    paid_at = models.DateField("fecha del pago", default=timezone.localdate)
    method = models.CharField(
        "método de pago",
        max_length=20,
        choices=Method.choices,
    )
    created_at = models.DateTimeField("registrado el", auto_now_add=True)

    class Meta:
        ordering = ["-paid_at", "-created_at"]
        verbose_name = "pago"
        verbose_name_plural = "pagos"

    def __str__(self):
        return f"{self.member} - ${self.amount} ({self.paid_at})"
