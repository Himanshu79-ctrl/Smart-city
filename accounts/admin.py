from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department, Worker


class CustomUserAdmin(UserAdmin):

    model = CustomUser

    list_display = (
        "username",
        "email",
        "user_type",
        "is_staff",
        "is_superuser",
    )

    list_filter = (
        "user_type",
        "is_staff",
        "is_superuser",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Extra Info",
            {
                "fields": (
                    "user_type",
                    "phone",
                    "address",
                    "profile_pic",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Extra Info",
            {
                "fields": (
                    "user_type",
                    "phone",
                    "address",
                    "profile_pic",
                )
            },
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Department)
admin.site.register(Worker)