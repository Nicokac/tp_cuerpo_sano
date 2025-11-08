from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea los grupos base del gimnasio y asigna los permisos mínimos"

    def handle(self, *args, **options):
        admin_group, _ = Group.objects.get_or_create(name="ADMIN")
        admin_perms = Permission.objects.all()
        admin_group.permissions.set(admin_perms)
        self.stdout.write(self.style.SUCCESS("Grupo ADMIN configurado."))

        recepcion_group, _ = Group.objects.get_or_create(name="RECEPCION")
        recepcion_codenames = [
            "view_member",
            "add_member",
            "change_member",
            "view_attendance",
            "add_attendance",
            "view_payment",
            "add_payment",
        ]
        recepcion_perms = Permission.objects.filter(codename__in=recepcion_codenames)
        recepcion_group.permissions.set(recepcion_perms)
        self.stdout.write(self.style.SUCCESS("Grupo RECEPCION configurado."))

        entrenador_group, _ = Group.objects.get_or_create(name="ENTRENADOR")
        entrenador_codenames = [
            "view_classsession",
            "view_attendance",
            "add_attendance",
        ]
        entrenador_perms = Permission.objects.filter(codename__in=entrenador_codenames)
        entrenador_group.permissions.set(entrenador_perms)
        self.stdout.write(self.style.SUCCESS("Grupo ENTRENADOR configurado."))

        self.stdout.write(self.style.SUCCESS("Roles iniciales listos."))
