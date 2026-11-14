from django.contrib import admin
from django.contrib.auth import get_user_model


admin.site.unregister(get_user_model())
