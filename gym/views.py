from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from . import services
from .forms import ClassAttendanceForm, GymAttendanceForm, PaymentForm
from .models import Attendance, ClassSession, Member, Payment, Trainer


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "gym/home.html"


class MemberListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Member
    permission_required = "gym.view_member"
    template_name = "gym/member_list.html"
    context_object_name = "members"


class MemberCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Member
    permission_required = "gym.add_member"
    fields = [
        "first_name",
        "last_name",
        "email",
        "dni",
        "phone",
        "date_joined",
        "is_active",
    ]
    template_name = "gym/member_form.html"
    success_url = reverse_lazy("gym:member_list")


class MemberUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Member
    permission_required = "gym.change_member"
    fields = [
        "first_name",
        "last_name",
        "email",
        "dni",
        "phone",
        "date_joined",
        "is_active",
    ]
    template_name = "gym/member_form.html"
    success_url = reverse_lazy("gym:member_list")


class MemberDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Member
    permission_required = "gym.delete_member"
    template_name = "gym/member_confirm_delete.html"
    success_url = reverse_lazy("gym:member_list")


class ClassSessionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = ClassSession
    permission_required = "gym.view_classsession"
    template_name = "gym/classsession_list.html"
    context_object_name = "class_sessions"

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("activity", "trainer", "trainer__user")
            .order_by("start")
        )
        user = self.request.user
        if user.groups.filter(name="ENTRENADOR").exists():
            try:
                trainer = Trainer.objects.get(user=user)
            except Trainer.DoesNotExist:
                return qs.none()
            qs = qs.filter(trainer=trainer)
        return qs


class ClassSessionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = ClassSession
    permission_required = "gym.add_classsession"
    fields = ["activity", "trainer", "start", "end", "capacity"]
    template_name = "gym/classsession_form.html"
    success_url = reverse_lazy("gym:classsession_list")


class ClassSessionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = ClassSession
    permission_required = "gym.change_classsession"
    fields = ["activity", "trainer", "start", "end", "capacity"]
    template_name = "gym/classsession_form.html"
    success_url = reverse_lazy("gym:classsession_list")


class ClassSessionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = ClassSession
    permission_required = "gym.delete_classsession"
    template_name = "gym/classsession_confirm_delete.html"
    success_url = reverse_lazy("gym:classsession_list")


class AttendanceListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Attendance
    permission_required = "gym.view_attendance"
    template_name = "gym/attendance_list.html"
    context_object_name = "attendances"
    paginate_by = 50

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("member", "class_session", "class_session__activity")
            .order_by("-timestamp")
        )


class GymAttendanceView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = "gym/attendance_gym_form.html"
    form_class = GymAttendanceForm
    permission_required = "gym.add_attendance"
    success_url = reverse_lazy("gym:attendance_list")

    def form_valid(self, form):
        member = form.cleaned_data["member"]
        try:
            services.registrar_asistencia_gym(member)
        except ValidationError as exc:
            form.add_error(None, exc.message)
            return self.form_invalid(form)
        messages.success(self.request, "Asistencia al gimnasio registrada correctamente.")
        return super().form_valid(form)


class ClassAttendanceView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = "gym/attendance_class_form.html"
    form_class = ClassAttendanceForm
    permission_required = "gym.add_attendance"
    success_url = reverse_lazy("gym:attendance_list")

    def form_valid(self, form):
        class_session = form.cleaned_data["class_session"]
        member = form.cleaned_data["member"]
        try:
            services.registrar_asistencia_clase(member, class_session)
        except ValidationError as exc:
            form.add_error(None, exc.message)
            return self.form_invalid(form)
        messages.success(self.request, "Asistencia a la clase registrada correctamente.")
        return super().form_valid(form)


class PaymentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Payment
    permission_required = "gym.view_payment"
    template_name = "gym/payment_list.html"
    context_object_name = "payments"
    paginate_by = 50
    ordering = ["-date", "-id"]


class PaymentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    permission_required = "gym.add_payment"
    template_name = "gym/payment_form.html"
    success_url = reverse_lazy("gym:payment_list")

    def get_initial(self):
        initial = super().get_initial()
        member_id = self.request.GET.get("member")
        if member_id:
            initial["member"] = member_id
        return initial

    def form_valid(self, form):
        try:
            self.object = form.save()
        except ValidationError as exc:
            form.add_error(None, exc.message)
            return self.form_invalid(form)
        messages.success(self.request, "Pago registrado correctamente.")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Revisá los datos del pago.")
        return super().form_invalid(form)


@login_required
@permission_required("gym.add_attendance", raise_exception=True)
@require_POST
def registrar_asistencia_gym(request: HttpRequest, member_id: int) -> HttpResponse:
    member = get_object_or_404(Member, pk=member_id)
    try:
        services.registrar_asistencia_gym(member)
        messages.success(request, "Asistencia al gimnasio registrada.")
    except ValidationError as exc:
        messages.error(request, exc.message)
    return redirect("gym:attendance_list")


@login_required
@permission_required("gym.add_attendance", raise_exception=True)
@require_POST
def registrar_asistencia_clase(
    request: HttpRequest, class_id: int, member_id: int
) -> HttpResponse:
    class_session = get_object_or_404(ClassSession, pk=class_id)
    member = get_object_or_404(Member, pk=member_id)
    try:
        services.registrar_asistencia_clase(member, class_session)
        messages.success(request, "Asistencia a la clase registrada.")
    except ValidationError as exc:
        messages.error(request, exc.message)
    return redirect("gym:attendance_list")
