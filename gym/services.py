"""Servicios de dominio para el TP Cuerpo Sano."""
from __future__ import annotations

import datetime as dt

from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Attendance, ClassSession, Member, Membership, Payment


def membresia_vigente(member: Member) -> Membership | None:
    """Devuelve la membresía vigente del socio (si existe)."""
    today = timezone.localdate()
    return (
        Membership.objects.filter(
            member=member,
            status=Membership.Status.VIGENTE,
            start_date__lte=today,
            end_date__gte=today,
        )
        .order_by("-end_date")
        .first()
    )


def registrar_asistencia_gym(member: Member) -> Attendance:
    membership = membresia_vigente(member)
    if not membership:
        raise ValidationError("El socio no tiene una membresía vigente.")
    return Attendance.objects.create(member=member, scope=Attendance.Scope.GYM)


def registrar_asistencia_clase(member: Member, class_session: ClassSession) -> Attendance:
    membership = membresia_vigente(member)
    if not membership:
        raise ValidationError("El socio no tiene una membresía vigente.")

    if not membership.type.allows_classes:
        raise ValidationError("La membresía del socio no permite asistir a clases.")

    if not class_session.cupo_disponible():
        raise ValidationError("La clase ya no tiene cupos disponibles.")

    return Attendance.objects.create(
        member=member,
        scope=Attendance.Scope.CLASS,
        class_session=class_session,
    )


def aplicar_pago(payment: Payment) -> Membership:
    """Crea una membresía vigente según un pago aprobado."""
    if payment.status != Payment.Status.APROBADO:
        raise ValidationError("Solo los pagos aprobados generan membresías.")

    membership_type = payment.membership_type
    if membership_type.duration_days <= 0:
        raise ValidationError("El tipo de membresía debe tener duración positiva.")

    today = timezone.localdate()
    ultima = (
        Membership.objects.filter(member=payment.member, type=membership_type)
        .order_by("-end_date")
        .first()
    )

    if ultima and ultima.end_date >= today:
        start_date = ultima.end_date + dt.timedelta(days=1)
    else:
        start_date = today

    end_date = start_date + dt.timedelta(days=membership_type.duration_days - 1)

    return Membership.objects.create(
        member=payment.member,
        type=membership_type,
        start_date=start_date,
        end_date=end_date,
        status=Membership.Status.VIGENTE,
    )
