from django.urls import path

from . import views

app_name = "gym"

urlpatterns = [
    path("home/", views.HomeView.as_view(), name="home"),
    path("miembros/", views.MemberListView.as_view(), name="member_list"),
    path("miembros/nuevo/", views.MemberCreateView.as_view(), name="member_create"),
    path("miembros/<int:pk>/editar/", views.MemberUpdateView.as_view(), name="member_update"),
    path(
        "miembros/<int:pk>/eliminar/",
        views.MemberDeleteView.as_view(),
        name="member_delete",
    ),
    path("clases/", views.ClassSessionListView.as_view(), name="classsession_list"),
    path("clases/nueva/", views.ClassSessionCreateView.as_view(), name="classsession_create"),
    path(
        "clases/<int:pk>/editar/",
        views.ClassSessionUpdateView.as_view(),
        name="classsession_update",
    ),
    path(
        "clases/<int:pk>/eliminar/",
        views.ClassSessionDeleteView.as_view(),
        name="classsession_delete",
    ),
    path("asistencias/", views.AttendanceListView.as_view(), name="attendance_list"),
    path("asistencias/gimnasio/", views.GymAttendanceView.as_view(), name="attendance_gym"),
    path("asistencias/clases/", views.ClassAttendanceView.as_view(), name="attendance_class"),
    path(
        "asistencias/gimnasio/<int:member_id>/",
        views.registrar_asistencia_gym,
        name="registrar_asistencia_gym",
    ),
    path(
        "asistencias/clases/<int:class_id>/<int:member_id>/",
        views.registrar_asistencia_clase,
        name="registrar_asistencia_clase",
    ),
    path("pagos/", views.PaymentListView.as_view(), name="payment_list"),
    path("pagos/nuevo/", views.PaymentCreateView.as_view(), name="payment_create"),
]
