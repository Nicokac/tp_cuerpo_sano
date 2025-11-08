from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class SignupViewTests(TestCase):
    def test_register_crea_usuario_y_redirige_al_login(self):
        datos = {
            "first_name": "Empleado",
            "last_name": "Demo",
            "email": "empleado@example.com",
            "password1": "ClaveSegura123",
            "password2": "ClaveSegura123",
        }

        response = self.client.post(reverse("register"), datos)

        self.assertRedirects(response, reverse("login"))
        usuario = User.objects.get(email="empleado@example.com")
        self.assertEqual(usuario.username, "empleado@example.com")
        self.assertEqual(usuario.first_name, "Empleado")
        self.assertEqual(usuario.last_name, "Demo")

    def test_register_email_duplicado_muestra_error(self):
        User.objects.create_user(
            username="empleado@example.com",
            email="empleado@example.com",
            password="ClaveSegura123",
        )

        datos = {
            "first_name": "Empleado",
            "last_name": "Demo",
            "email": "EMPLEADO@EXAMPLE.COM",
            "password1": "ClaveSegura123",
            "password2": "ClaveSegura123",
        }

        response = self.client.post(reverse("register"), datos)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "email",
            "Ya existe un usuario con ese email.",
        )
