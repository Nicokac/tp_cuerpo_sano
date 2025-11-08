from django.urls import path
from .views import HomeView

app_name = "gym"

urlpatterns = [
    # Placeholder para futuras vistas (CRUDs del TP)
    path("home/", HomeView.as_view(), name="home"),
]
