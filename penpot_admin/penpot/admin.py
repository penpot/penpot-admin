import json
import uuid
from datetime import datetime, timezone

from django.contrib import admin
from django.db.models import Count

from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from penpot_admin import api
from penpot_admin.penpot import models

## --- ADMIN

class PenpotAdminSite(admin.AdminSite):
    site_header = "Penpot Admin"
    site_title = "Penpot Admin Panel"

admin_site = PenpotAdminSite(name="penpot")
admin_site.disable_action("delete_selected")


## --- HELPERS

class PrettyJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=4, sort_keys=True, **kwargs)

## --- MODELS

## PROFILE

class ProfileCreationForm(forms.ModelForm):
    email = forms.EmailField(label="Email")
    fullname = forms.CharField(label="Fullname")
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = models.Profile
        fields = ("email", "fullname")

    def clean_password(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.set_password(self.cleaned_data["password1"])
        if commit:
            profile.save()
        return profile

class ProfileChangeForm(forms.ModelForm):
    email = forms.EmailField(label="Email")
    fullname = forms.CharField(label="Fullname")
    lang = forms.CharField(label="Default Language", required=False)
    password = forms.CharField(label="Password")

    class Meta:
        model = models.Profile
        fields = ("email", "password", "fullname", "is_active")

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.set_password(self.cleaned_data["password"])
        profile.modified_at = datetime.now(tz=timezone.utc)
        if commit:
            profile.save()
        return profile


@admin.action(description="Delete (Soft)")
def mark_deleted(madmin, request, queryset):
    queryset.update(deleted_at=datetime.now(tz=timezone.utc))

@admin.action(description="Restore")
def mark_restored(madmin, request, queryset):
    queryset.update(deleted_at=None)

class ProfileAdmin(BaseUserAdmin):
    form = ProfileChangeForm
    add_form = ProfileCreationForm
    list_display = ("email", "fullname", "is_active", "is_admin", "created_at", "deleted_at",)
    list_filter = ("is_admin", "is_muted", "is_blocked", "deleted_at")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("fullname","lang", )}),
        ("Metadata", {"fields": ("created_at",
                                 "modified_at",
                                 "deleted_at",
                                 "props",
                                 )}),
        ("Permissions", {"fields": ("is_admin",
                                    "is_active",
                                    "is_blocked",
                                    "is_muted",
                                    "is_demo",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "fullname", "password1", "password2"),
        }),
    )
    search_fields = ("email", "id")

    ordering = ("-created_at",)
    filter_horizontal = ()
    date_hierarchy = "created_at"
    actions_on_top = True
    actions_on_bottom = False

    list_per_page = 20
    actions = [mark_deleted, mark_restored]

    readonly_fields = ("created_at",
                       "modified_at",
                       "deleted_at",
                       "props")

    # def delete_model(self, request, obj):
    #     obj.deleted_at = datetime.now(tz=timezone.utc)
    #     obj.save()

    # def has_delete_permission(self, request, obj=None):
    #     return False

admin_site.register(models.Profile, ProfileAdmin)

## TEAM

class TeamForm(forms.ModelForm):
    class Meta:
        model = models.Team
        fields = "__all__"
        widgets = {
            "name": forms.TextInput()
        }


class TeamMemberForm(forms.ModelForm):
    id = forms.UUIDField(required=False, widget=forms.HiddenInput)
    is_owner = forms.BooleanField(required=False, initial=False)
    is_admin = forms.BooleanField(required=False, initial=True)
    can_edit = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = models.TeamProfileRel
        fields = ("profile",)

    def save(self, commit=True):
        obj = super().save(commit=False)

        if obj.id is None:
            obj.id = uuid.uuid4()

        if obj.created_at is None:
            obj.created_at = datetime.now(tz=timezone.utc)
            obj.modified_at = obj.created_at
        else:
            obj.modified_at = datetime.now(tz=timezone.utc)

        if commit:
            obj.save()

        return obj

class TeamMemberInline(admin.TabularInline):
    model = models.TeamProfileRel
    form = TeamMemberForm
    raw_id_fields = ("profile",)
    show_change_link = True
    extra = 0

class TeamAdmin(admin.ModelAdmin):
    form = TeamForm
    list_display = ("name",
                    "total_members",
                    "total_projects",
                    "is_default",
                    "created_at",
                    "deleted_at",)
    list_filter = ("created_at", "deleted_at", "is_default")
    search_fields = ("name", "id")
    ordering = ("-created_at",)
    readonly_fields = ("is_default",
                       "photo",
                       "created_at",
                       "modified_at",
                       "deleted_at",
                       "id",
                       )
    raw_id_fields = ("photo",)
    actions = [mark_deleted, mark_restored]
    list_per_page = 20

    fieldsets = (
        ("Main", {"fields": ("id", "name", "is_default", "photo")}),
        ("Meta", {"fields": ("created_at", "modified_at", "deleted_at")})
    )

    date_hierarchy = "created_at"
    actions_on_top = True

    inlines = [TeamMemberInline]

    delete_confirmation_template = "penpot/delete_confirmation.html"

    def get_deleted_objects(self, objs, request):
        return [], {}, set(), []

    @admin.display(description="Members")
    def total_members(self, obj):
        return obj.total_members

    @admin.display(description="Projects")
    def total_projects(self, obj):
        return obj.total_projects

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(total_members=Count("members"),
                         total_projects=Count("projects"))
        return qs

    def has_delete_permission(self, request, obj=None):
        if obj:
            return not obj.is_default
        return False

admin_site.register(models.Team, TeamAdmin)

class TeamProfileRelAdmin(admin.ModelAdmin):
    list_display = ("team",
                    "profile",
                    "is_admin",
                    "is_owner",
                    "can_edit",)
    list_filter = ("is_admin",
                   "is_owner",
                   "can_edit",)
    raw_id_fields = ("team", "profile")
    list_per_page = 20
    search_fields = ("team__id", "profile__id", "profile__email")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(team__is_default=True)


admin_site.register(models.TeamProfileRel, TeamProfileRelAdmin)

# class TeamFontVariantAdmin(admin.ModelAdmin):
#     list_display = ("font_id",
#                     "font_family",
#                     "font_weight",
#                     "font_style",
#                     "team",
#                     "profile",
#                     "created_at",
#                     "deleted_at",)
#     list_filter = ("font_weight",
#                    "font_style",
#                    "created_at",
#                    "deleted_at")
#     raw_id_fields = ("team",
#                      "profile")

#     readonly_fields = ("created_at",
#                        "modified_at",
#                        "deleted_at")

#     list_per_page = 20
#     search_fields = ("name", "font_family")
#     date_hierarchy = "created_at"
#     actions = [mark_deleted, mark_restored]

#     def delete_model(self, request, obj):
#         obj.deleted_at = datetime.now(tz=timezone.utc)
#         obj.save()

# admin_site.register(models.TeamFontVariant, TeamFontVariantAdmin)

class TeamInvitationForm(forms.ModelForm):
    class Meta:
        model = models.TeamInvitation
        fields = "__all__"
        widgets = {
            "email_to": forms.TextInput(),
            "role": forms.TextInput,
        }

class TeamInvitationAdmin(admin.ModelAdmin):
    list_display = ("team",
                    "email_to",
                    "role",
                    "created_at",
                    "valid_until",)
    list_filter = ("role",
                   "created_at",
                   "valid_until")
    # raw_id_fields = ("team",)
    readonly_fields = ("created_at",
                       "updated_at",
                       "valid_until",
                       "email_to",
                       "team",
                       "id",
                       "role",)
    list_per_page = 20
    search_fields = ("email_to", "id")
    date_hierarchy = "created_at"

    form = TeamInvitationForm


    fieldsets = (
        ("Main", {"fields": ("id", "team", "email_to", "role")}),
        ("Meta", {"fields": ("valid_until", "created_at", "updated_at")})
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin_site.register(models.TeamInvitation, TeamInvitationAdmin)

## PROJECT

class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = "__all__"
        widgets = {
            "name": forms.TextInput()
        }

    def save(self, commit=True):
        obj = super().save(commit=False)

        if obj.id is None:
            obj.id = uuid.uuid4()

        if obj.created_at is None:
            obj.created_at = datetime.now(tz=timezone.utc)
            obj.modified_at = obj.created_at
        else:
            obj.modified_at = datetime.now(tz=timezone.utc)

        if obj.is_default is None:
            obj.is_default = False

        if commit:
            obj.save()

        return obj

class ProjectMemberForm(forms.ModelForm):
    id = forms.UUIDField(required=False, widget=forms.HiddenInput)
    is_owner = forms.BooleanField(required=False, initial=False)
    is_admin = forms.BooleanField(required=False, initial=True)
    can_edit = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = models.ProjectProfileRel
        fields = ("profile",)

    def save(self, commit=True):
        obj = super().save(commit=False)

        if obj.id is None:
            obj.id = uuid.uuid4()

        if obj.created_at is None:
            obj.created_at = datetime.now(tz=timezone.utc)
            obj.modified_at = obj.created_at
        else:
            obj.modified_at = datetime.now(tz=timezone.utc)

        if commit:
            obj.save()

        return obj

class ProjectMemberInline(admin.TabularInline):
    model = models.ProjectProfileRel
    form = ProjectMemberForm

    raw_id_fields = ("profile",)
    show_change_link = True
    extra = 0


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name",
                    "total_members",
                    "total_files",
                    "is_default",
                    "created_at",
                    "deleted_at")
    list_filter = ("deleted_at", "is_default")
    search_fields = ("name", "id")
    ordering = ("-created_at",)
    actions = [mark_deleted, mark_restored]
    readonly_fields = ("is_default",)
    raw_id_fields = ("team",)
    list_per_page = 20
    date_hierarchy = "created_at"
    actions_on_top = True

    readonly_fields = ("id",
                       "is_default",
                       "created_at",
                       "modified_at",
                       "deleted_at",)

    fieldsets = (
        ("Main", {"fields": ("id", "name", "is_default")}),
        ("Meta", {"fields": ("created_at",
                             "modified_at",
                             "deleted_at")})
    )


    form = ProjectForm
    inlines = [ProjectMemberInline]

    delete_confirmation_template = "penpot/delete_confirmation.html"

    def get_deleted_objects(self, objs, request):
        return [], {}, set(), []

    @admin.display(description="Members")
    def total_members(self, obj):
        return obj.total_members

    @admin.display(description="Files")
    def total_files(self, obj):
        return obj.total_files

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(total_members=Count("members"),
                         total_files=Count("files"))
        return qs

admin_site.register(models.Project, ProjectAdmin)

class ProjectProfileRelAdmin(admin.ModelAdmin):
    list_display = ("project",
                    "profile",
                    "is_admin",
                    "is_owner",
                    "can_edit",)
    list_filter = ("is_admin",
                   "is_owner",
                   "can_edit",
                   "created_at")
    raw_id_fields = ("project", "profile")
    list_per_page = 20
    search_fields = ("team__id", "profile__id", "profile__email")
    list_display_links = ("project", "profile")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(project__is_default=True)

admin_site.register(models.ProjectProfileRel, ProjectProfileRelAdmin)


## FILE

class FileForm(forms.ModelForm):
    class Meta:
        model = models.File
        fields = "__all__"
        widgets = {
            "name": forms.TextInput()
        }

class FileAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "revn", "is_shared", "created_at", "modified_at", "deleted_at",)
    list_filter = ("created_at",
                   "deleted_at",
                   "is_shared",
                   "has_media_trimmed",)
    raw_id_fields = ("project",)
    exclude = ("features", "data_backend")
    readonly_fields = ("id",
                       "created_at",
                       "modified_at",
                       "deleted_at",
                       "revn",
                       "has_media_trimmed",
                       "comment_thread_seqn",
                       "ignore_sync_until")

    search_fields = ("name", "id")

    form = FileForm

    fieldsets = (
        ("Main", {"fields": ("id", "revn", "name", "project")}),
        ("Meta", {"fields": ("is_shared",
                             "created_at",
                             "modified_at",
                             "deleted_at",
                             "ignore_sync_until",
                             "comment_thread_seqn",)})
    )


    list_per_page = 20

    delete_confirmation_template = "penpot/delete_confirmation.html"

    def get_deleted_objects(self, objs, request):
        return [], {}, set(), []

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.defer("data")

admin_site.register(models.File, FileAdmin)

# class FileChangeAdmin(admin.ModelAdmin):
#     pass

# admin_site.register(models.FileChange, FileChangeAdmin)


# class FileMediaObjectAdmin(admin.ModelAdmin):
#     list_display = ("name",
#                     "size",
#                     "mtype",
#                     "file",
#                     "is_local",
#                     "created_at",
#                     "deleted_at",)
#     list_filter = ("mtype",
#                    "created_at",
#                    "deleted_at")
#     raw_id_fields = ("file",)
#     readonly_fields = ("created_at",
#                        "deleted_at",)
#     list_per_page = 20
#     search_fields = ("id",)
#     date_hierarchy = "created_at"

#     @admin.display(description="Size")
#     def size(self, obj):
#         return f"{obj.width}x{obj.height}"

# admin_site.register(models.FileMediaObject, FileMediaObjectAdmin)



## STORAGE OBJECT

# class StorageObjectAdmin(admin.ModelAdmin):
#     list_display = ("id", "backend", "size", "created_at", "touched_at", "deleted_at")
#     list_filter = ("backend", "created_at", "deleted_at",)
#     search_fields = ("name", "id")
#     list_per_page = 20
#     readonly_fields = ("id",
#                        "created_at",
#                        "size",
#                        "backend",
#                        "metadata",)

# admin_site.register(models.StorageObject, StorageObjectAdmin)


class TaskForm(forms.ModelForm):
    props = forms.JSONField(encoder=PrettyJSONEncoder,
                            widget=forms.Textarea(attrs={"cols": 100, "rows": 15}))
    class Meta:
        model = models.Task
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(),
            "queue": forms.TextInput(),
            "status": forms.TextInput(),
            "label": forms.TextInput(),
            "error": forms.Textarea(attrs={"cols": 100}),
        }

class TaskAdmin(admin.ModelAdmin):
    list_display = ("name",
                    "queue",
                    "status",
                    "created_at",
                    "scheduled_at",)
    list_filter = ("queue",
                   "status",
                   "created_at",
                   "scheduled_at",)

    form = TaskForm

    search_fields = ("id", "name")
    ordering = ("scheduled_at",)
    filter_horizontal = ()
    date_hierarchy = "created_at"
    list_per_page = 20

    readonly_fields = ("created_at",
                       "modified_at",
                       "completed_at",
                       "retry_num",
                       "max_retries",
                       "status",
                       "id",
                       "queue",
                       "label",
                       "name")

    fieldsets = (
        ("Main", {"fields": ("id",
                             "name",
                             "queue",
                             "status",
                             "label")}),
        ("Meta", {"fields": ("created_at",
                             "modified_at",
                             "completed_at",
                             "retry_num",
                             "max_retries")})
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin_site.register(models.Task, TaskAdmin)
