from django.contrib import admin

from .models import FavoriteCalendarEvent, FavoriteExam, Notification, SavedMaterial, UserPreferences, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "city", "state", "target_course")
    search_fields = ("user__username", "full_name", "user__email", "city")
    list_filter = ("state",)


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ("user", "study_reminders", "deadline_reminders", "email_notifications")
    search_fields = ("user__username", "user__email")


admin.site.register(FavoriteExam)
admin.site.register(FavoriteCalendarEvent)
admin.site.register(SavedMaterial)
admin.site.register(Notification)
