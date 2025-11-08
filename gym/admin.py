from django.contrib import admin
from . import models

@admin.register(models.Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "email", "is_active", "date_joined")
    search_fields = ("last_name", "first_name", "email")

@admin.register(models.MembershipType)
class MembershipTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_days", "price", "allows_classes", "max_classes_per_week")

@admin.register(models.Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("member", "type", "start_date", "end_date", "status", "esta_vigente")
    list_filter = ("status", "type")

@admin.register(models.Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(models.Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "email")

@admin.register(models.ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ("activity", "trainer", "start", "end", "capacity")

@admin.register(models.Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("member", "scope", "timestamp", "class_session")
    list_filter = ("scope",)

@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("member", "date", "amount", "method", "status")
    list_filter = ("method", "status")
