from django.contrib import admin
from django.urls import path, include
from gym.views import HomeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    path("g/", include("gym.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
]

# auth urls provee:
# /accounts/login/  /accounts/logout/  /accounts/password_change/ ...
