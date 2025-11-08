from __future__ import annotations
from django.db import models
from django.utils import timezone

# --- Dominio mínimo del TP ---

class Member(models.Model):
    first_name = models.CharField("Nombre", max_length=80)
    last_name = models.CharField("Apellido", max_length=80)
    email = models.EmailField("Email", unique=True)
    dni = models.CharField("DNI", max_length=32, blank=True)
    phone = models.CharField("Teléfono", max_length=32, blank=True)
    date_joined = models.DateField("Fecha de alta", default=timezone.now)
    is_active = models.BooleanField("Activo", default=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return f"{self.last_name}, {self.first_name}"


class MembershipType(models.Model):
    name = models.CharField("Nombre", max_length=80)
    duration_days = models.PositiveIntegerField("Duración (días)")
    price = models.DecimalField("Precio", max_digits=12, decimal_places=2)
    allows_classes = models.BooleanField("Permite clases", default=True)
    max_classes_per_week = models.PositiveIntegerField(
        "Máx. clases/semana", null=True, blank=True
    )

    def __str__(self) -> str:
        return self.name


class Membership(models.Model):
    class Status(models.TextChoices):
        VIGENTE = "vigente", "Vigente"
        VENCIDA = "vencida", "Vencida"
        BLOQUEADA = "bloqueada", "Bloqueada"

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    type = models.ForeignKey(MembershipType, on_delete=models.PROTECT)
    start_date = models.DateField("Inicio")
    end_date = models.DateField("Fin")
    status = models.CharField(
        "Estado", max_length=16, choices=Status.choices, default=Status.VIGENTE
    )

    def esta_vigente(self) -> bool:
        today = timezone.localdate()
        return self.status == self.Status.VIGENTE and self.start_date <= today <= self.end_date

    def __str__(self) -> str:
        return f"{self.member} — {self.type} ({self.start_date}→{self.end_date})"


class Activity(models.Model):
    name = models.CharField("Nombre", max_length=120)
    description = models.TextField("Descripción", blank=True)

    def __str__(self) -> str:
        return self.name


class Trainer(models.Model):
    first_name = models.CharField("Nombre", max_length=80)
    last_name = models.CharField("Apellido", max_length=80)
    email = models.EmailField("Email")

    def __str__(self) -> str:
        return f"{self.last_name}, {self.first_name}"


class ClassSession(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.PROTECT)
    trainer = models.ForeignKey(Trainer, on_delete=models.PROTECT)
    start = models.DateTimeField("Inicio")
    end = models.DateTimeField("Fin")
    capacity = models.PositiveIntegerField("Capacidad", default=20)

    def __str__(self) -> str:
        return f"{self.activity} — {self.start:%Y-%m-%d %H:%M}"

    @property
    def seats_taken(self) -> int:
        return Attendance.objects.filter(scope=Attendance.Scope.CLASS, class_session=self).count()

    def cupo_disponible(self) -> bool:
        return self.seats_taken < self.capacity


class Attendance(models.Model):
    class Scope(models.TextChoices):
        GYM = "GYM", "Gimnasio"
        CLASS = "CLASS", "Clase"

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    timestamp = models.DateTimeField("Fecha/hora", default=timezone.now)
    scope = models.CharField(max_length=8, choices=Scope.choices)
    class_session = models.ForeignKey(
        ClassSession, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self) -> str:
        base = f"{self.member} — {self.scope}"
        if self.class_session_id:
            base += f" — {self.class_session}"
        return base


class Payment(models.Model):
    class Method(models.TextChoices):
        EFECTIVO = "EFECTIVO", "Efectivo"
        TARJETA = "TARJETA", "Tarjeta"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"

    class Status(models.TextChoices):
        APROBADO = "APROBADO", "Aprobado"
        RECHAZADO = "RECHAZADO", "Rechazado"

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateField("Fecha", default=timezone.localdate)
    amount = models.DecimalField("Monto", max_digits=12, decimal_places=2)
    method = models.CharField("Método", max_length=16, choices=Method.choices)
    reference = models.CharField("Referencia", max_length=120, blank=True)
    status = models.CharField("Estado", max_length=16, choices=Status.choices)

    def __str__(self) -> str:
        return f"{self.member} — ${self.amount} ({self.status})"
