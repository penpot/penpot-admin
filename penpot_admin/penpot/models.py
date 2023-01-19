import uuid

from datetime import datetime, timezone
from django.db import models
from django.contrib.auth.hashers import is_password_usable

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

class AuditLog(models.Model):
    id = models.UUIDField()
    name = models.TextField()
    type = models.TextField()
    created_at = models.DateTimeField(primary_key=True)
    archived_at = models.DateTimeField(blank=True, null=True)
    profile_id = models.UUIDField()
    props = models.JSONField(blank=True, null=True)
    ip_addr = models.GenericIPAddressField(blank=True, null=True)
    tracked_at = models.DateTimeField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    context = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'audit_log'
        unique_together = (('created_at', 'profile_id'),)


class Comment(models.Model):
    id = models.UUIDField(primary_key=True)
    thread = models.ForeignKey('CommentThread', models.DO_NOTHING)
    owner = models.ForeignKey('Profile', models.DO_NOTHING)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    content = models.TextField()

    class Meta:
        managed = False
        db_table = 'comment'

        verbose_name = "Comment"
        verbose_name_plural = "Comments"

class CommentThread(models.Model):
    id = models.UUIDField(primary_key=True)
    file = models.ForeignKey('File', models.DO_NOTHING)
    owner = models.ForeignKey('Profile', models.DO_NOTHING)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    page_id = models.UUIDField()
    participants = models.JSONField()
    seqn = models.IntegerField()
    position = models.TextField()  # This field type is a guess.
    is_resolved = models.BooleanField()
    page_name = models.TextField(blank=True, null=True)
    frame_id = models.UUIDField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comment_thread'
        unique_together = (('file', 'seqn'),)

        verbose_name = "Comment Thread"
        verbose_name_plural = "Comment Threads"


# class CommentThreadStatus(models.Model):
#     thread = models.OneToOneField(CommentThread, models.DO_NOTHING, primary_key=True)
#     profile = models.ForeignKey('Profile', models.DO_NOTHING)
#     created_at = models.DateTimeField()
#     modified_at = models.DateTimeField()

#     class Meta:
#         managed = False
#         db_table = 'comment_thread_status'
#         unique_together = (('thread', 'profile'),)


class File(models.Model):
    id = models.UUIDField(primary_key=True)
    project = models.ForeignKey('Project', models.CASCADE, related_name="files")
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    name = models.TextField()
    is_shared = models.BooleanField()
    has_media_trimmed = models.BooleanField(blank=True, null=True)
    revn = models.BigIntegerField()
    data = models.BinaryField(blank=True, null=True)
    ignore_sync_until = models.DateTimeField(blank=True, null=True)
    comment_thread_seqn = models.IntegerField(blank=True, null=True)
    data_backend = models.TextField(blank=True, null=True)
    features = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'file'

        verbose_name = "file"
        verbose_name_plural = "files"


    def __str__(self):
        return f"File: '{self.name}'"

class FileChange(models.Model):
    id = models.UUIDField(primary_key=True)
    file = models.ForeignKey(File, models.DO_NOTHING)
    created_at = models.DateTimeField()
    session_id = models.UUIDField(blank=True, null=True)
    revn = models.BigIntegerField()
    data = models.BinaryField(blank=True, null=True)
    changes = models.BinaryField(blank=True, null=True)
    profile = models.ForeignKey('Profile', models.DO_NOTHING, blank=True, null=True)
    features = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'file_change'

        verbose_name = "File Change"
        verbose_name_plural = "File Changes"

# class FileDataFragment(models.Model):
#     id = models.UUIDField()
#     file = models.OneToOneField(File, models.DO_NOTHING, primary_key=True)
#     created_at = models.DateTimeField()
#     metadata = models.JSONField(blank=True, null=True)
#     content = models.BinaryField()

#     class Meta:
#         managed = False
#         db_table = 'file_data_fragment'
#         unique_together = (('file', 'id'),)


# class FileLibraryRel(models.Model):
#     file = models.OneToOneField(File, models.DO_NOTHING, primary_key=True)
#     library_file = models.ForeignKey(File, models.DO_NOTHING)
#     created_at = models.DateTimeField()
#     synced_at = models.DateTimeField()

#     class Meta:
#         managed = False
#         db_table = 'file_library_rel'
#         unique_together = (('file', 'library_file'),)


class FileMediaObject(models.Model):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    name = models.TextField()
    width = models.IntegerField()
    height = models.IntegerField()
    mtype = models.TextField()
    file = models.ForeignKey(File, models.CASCADE, related_name="media_objects")
    is_local = models.BooleanField()
    media = models.ForeignKey('StorageObject', models.CASCADE, related_name="+")
    thumbnail = models.ForeignKey('StorageObject', models.CASCADE, blank=True, null=True,
                                  related_name="+")

    class Meta:
        managed = False
        db_table = 'file_media_object'

        verbose_name = "File Media Object"
        verbose_name_plural = "File Media Objects"

    def __str__(self):
        return self.name


# class FileObjectThumbnail(models.Model):
#     file = models.OneToOneField(File, models.DO_NOTHING, primary_key=True)
#     object_id = models.TextField()
#     created_at = models.DateTimeField()
#     data = models.TextField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'file_object_thumbnail'
#         unique_together = (('file', 'object_id'),)


# class FileProfileRel(models.Model):
#     file = models.OneToOneField(File, models.DO_NOTHING, primary_key=True)
#     profile = models.ForeignKey('Profile', models.DO_NOTHING)
#     created_at = models.DateTimeField()
#     modified_at = models.DateTimeField()
#     is_owner = models.BooleanField(blank=True, null=True)
#     is_admin = models.BooleanField(blank=True, null=True)
#     can_edit = models.BooleanField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'file_profile_rel'
#         unique_together = (('file', 'profile'),)


# class FileThumbnail(models.Model):
#     file = models.OneToOneField(File, models.DO_NOTHING, primary_key=True)
#     revn = models.BigIntegerField()
#     created_at = models.DateTimeField()
#     updated_at = models.DateTimeField()
#     deleted_at = models.DateTimeField(blank=True, null=True)
#     data = models.TextField(blank=True, null=True)
#     props = models.JSONField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'file_thumbnail'
#         unique_together = (('file', 'revn'),)


# class GlobalComplaintReport(models.Model):
#     email = models.TextField(primary_key=True)
#     created_at = models.DateTimeField()
#     type = models.TextField()
#     content = models.JSONField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'global_complaint_report'
#         unique_together = (('email', 'created_at'),)


class HttpSession(models.Model):
    id = models.TextField(primary_key=True)
    created_at = models.DateTimeField()
    profile = models.ForeignKey('Profile', models.DO_NOTHING)
    user_agent = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'http_session'
        unique_together = (('id', 'profile'),)


# class Migrations(models.Model):
#     module = models.TextField(blank=True, null=True)
#     step = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'migrations'
#         unique_together = (('module', 'step'),)


class ProfileManager(BaseUserManager):
    def create_user(self, email, fullname, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        ts = datetime.now(tz=timezone.utc)

        user = self.model(
            email=self.normalize_email(email),
            fullname=fullname,
        )

        user.set_password(password)
        user.created_at = ts
        user.modified_at = ts
        user.save(using=self._db)
        return user

    def create_superuser(self, email, fullname, password=None):
        user = self.create_user(
            email,
            password=password,
            fullname=fullname,
        )
        # user.is_admin = True
        user.save(using=self._db)
        return user

class Profile(models.Model):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    fullname = models.TextField()
    email = models.TextField(unique=True)
    password = models.TextField()
    lang = models.TextField(blank=True, null=True)
    theme = models.TextField(blank=True, null=True)
    is_demo = models.BooleanField()
    is_active = models.BooleanField()
    props = models.JSONField(blank=True, null=True)
    photo = models.ForeignKey('StorageObject', models.DO_NOTHING, blank=True, null=True)
    is_muted = models.BooleanField(blank=True, null=True)
    auth_backend = models.TextField(blank=True, null=True)
    is_blocked = models.BooleanField(blank=True, null=True)

    objects = ProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname']

    class Meta:
        managed = False
        db_table = 'profile'
        verbose_name = "profile"
        verbose_name_plural = "profiles"

    def __str__(self):
        return self.email

    def get_username(self):
        return self.email

    def natural_key(self):
        return (self.get_username(),)

    def set_password(self, raw_password):
        from penpot_admin import api
        print("raw password:", raw_password)

        password = api.derive_password_hash(raw_password)
        print("derive_password:", password)
        self.password = password


# class ProfileComplaintReport(models.Model):
#     profile = models.OneToOneField(Profile, models.DO_NOTHING, primary_key=True)
#     created_at = models.DateTimeField()
#     type = models.TextField()
#     content = models.JSONField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'profile_complaint_report'
#         unique_together = (('profile', 'created_at'),)


class Project(models.Model):
    id = models.UUIDField(primary_key=True)
    team = models.ForeignKey('Team', models.CASCADE, related_name="projects")
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    is_default = models.BooleanField()
    name = models.TextField()

    members = models.ManyToManyField(through="penpot.ProjectProfileRel",
                                     to="penpot.Profile",
                                     related_name="projects_member_of")


    def __str__(self):
        return f"Project: '{self.name}'"

    class Meta:
        managed = False
        db_table = 'project'
        verbose_name = "Project"
        verbose_name_plural = "Projects"


class ProjectProfileRel(models.Model):
    id = models.UUIDField(primary_key=True)
    profile = models.ForeignKey(Profile, models.CASCADE)
    project = models.ForeignKey(Project, models.CASCADE)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    is_owner = models.BooleanField(blank=True, null=True)
    is_admin = models.BooleanField(blank=True, null=True)
    can_edit = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_profile_rel'
        unique_together = (('profile', 'project'),)

        verbose_name = "Project Member"
        verbose_name_plural = "Project Members"

    def __str__(self):
        return f"Project Member: {self.id}"


# class ScheduledTask(models.Model):
#     id = models.TextField(primary_key=True)
#     created_at = models.DateTimeField()
#     modified_at = models.DateTimeField()
#     cron_expr = models.TextField()

#     class Meta:
#         managed = False
#         db_table = 'scheduled_task'


# class ScheduledTaskHistory(models.Model):
#     id = models.UUIDField(primary_key=True)
#     task = models.ForeignKey(ScheduledTask, models.DO_NOTHING)
#     created_at = models.DateTimeField()
#     is_error = models.BooleanField()
#     reason = models.TextField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'scheduled_task_history'
#         unique_together = (('id', 'created_at'),)


# class ServerErrorReport(models.Model):
#     id = models.UUIDField(primary_key=True)
#     created_at = models.DateTimeField()
#     content = models.JSONField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'server_error_report'
#         unique_together = (('id', 'created_at'),)


# class ServerProp(models.Model):
#     id = models.TextField(primary_key=True)
#     content = models.JSONField(blank=True, null=True)
#     preload = models.BooleanField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'server_prop'


class ShareLink(models.Model):
    id = models.UUIDField(primary_key=True)
    file = models.ForeignKey(File, models.DO_NOTHING)
    owner = models.ForeignKey(Profile, models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField()
    pages = models.TextField(blank=True, null=True)  # This field type is a guess.
    flags = models.TextField(blank=True, null=True)  # This field type is a guess.
    who_comment = models.TextField()
    who_inspect = models.TextField()

    class Meta:
        managed = False
        db_table = 'share_link'

        verbose_name = "Share Link"
        verbose_name_plural = "Share Links"


class StorageObject(models.Model):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    size = models.BigIntegerField()
    backend = models.TextField()
    metadata = models.JSONField(blank=True, null=True)
    touched_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'storage_object'
        verbose_name = "Storage Object"
        verbose_name_plural = "Storage Objects"

    def __str__(self):
        return str(self.id)


class Task(models.Model):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    completed_at = models.DateTimeField(blank=True, null=True)
    scheduled_at = models.DateTimeField()
    priority = models.SmallIntegerField(blank=True, null=True)
    queue = models.TextField()
    name = models.TextField()
    props = models.JSONField()
    error = models.TextField(blank=True, null=True)
    retry_num = models.SmallIntegerField()
    max_retries = models.SmallIntegerField()
    status = models.TextField()
    label = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'task'
        unique_together = (('id', 'status'),)

        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return f"Task: '{self.name}'"


class Team(models.Model):
    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    name = models.TextField()
    is_default = models.BooleanField()
    photo = models.ForeignKey(StorageObject, models.DO_NOTHING, blank=True, null=True)


    members = models.ManyToManyField(through="penpot.TeamProfileRel",
                                     to="penpot.Profile",
                                     related_name="teams_member_of")

    class Meta:
        managed = False
        db_table = 'team'

        verbose_name = "Team"
        verbose_name_plural = "Teams"

    def __str__(self):
        return f"Team: '{self.name}'"


class TeamFontVariant(models.Model):
    id = models.UUIDField(primary_key=True)
    team = models.ForeignKey(Team, models.CASCADE)
    profile = models.ForeignKey(Profile, models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    font_id = models.UUIDField()
    font_family = models.TextField()
    font_weight = models.SmallIntegerField()
    font_style = models.TextField()
    otf_file = models.ForeignKey(StorageObject, models.SET_NULL, blank=True, null=True,
                                 related_name="+")
    ttf_file = models.ForeignKey(StorageObject, models.SET_NULL, blank=True, null=True,
                                 related_name="+")
    woff1_file = models.ForeignKey(StorageObject, models.SET_NULL, blank=True, null=True,
                                   related_name="+")
    woff2_file = models.ForeignKey(StorageObject, models.SET_NULL, blank=True, null=True,
                                   related_name="+")

    class Meta:
        managed = False
        db_table = 'team_font_variant'

        verbose_name = "Team Font Variant"
        verbose_name_plural = "Team Font Variants"

    def __str__(self):
        return f"{self.font_family} ({self.font_weight}/{self.font_style})"



class TeamInvitation(models.Model):
    id = models.UUIDField(primary_key=True)
    team = models.ForeignKey(Team, models.CASCADE,
                             related_name="invitations")
    email_to = models.TextField()
    role = models.TextField()
    valid_until = models.DateTimeField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'team_invitation'
        unique_together = (('team', 'email_to'),)

        verbose_name = "Team Invitation"
        verbose_name_plural = "Team Invitations"

    def __str__(self):
        return f"Invitation for: {self.email_to}"


class TeamProfileRel(models.Model):
    id = models.UUIDField(primary_key=True)
    team = models.ForeignKey(Team, models.CASCADE)
    profile = models.ForeignKey(Profile, models.CASCADE)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    is_admin = models.BooleanField(blank=True, null=True)
    is_owner = models.BooleanField(blank=True, null=True)
    can_edit = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'team_profile_rel'
        unique_together = (('team', 'profile'),)

        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"

    def __str__(self):
        return f"Team Member: {self.id}"


class TeamProjectProfileRel(models.Model):
    id = models.UUIDField(primary_key=True)
    team = models.ForeignKey(Team, models.CASCADE)
    profile = models.ForeignKey(Profile, models.CASCADE)
    project = models.ForeignKey(Project, models.CASCADE)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    is_pinned = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'team_project_profile_rel'
        unique_together = (('team', 'profile', 'project'),)

        verbose_name = "Team && Project & Profile"
        verbose_name = "Teams && Projects & Profiles"

    def __str__(self):
        return str(self.id)


class Webhook(models.Model):
    id = models.UUIDField(primary_key=True)
    team = models.ForeignKey(Team, models.DO_NOTHING)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    uri = models.TextField()
    mtype = models.TextField()
    error_code = models.TextField(blank=True, null=True)
    error_count = models.SmallIntegerField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    secret_key = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'webhook'

        verbose_name = "Webhook"
        verbose_name_plural = "Webhooks"


class WebhookDelivery(models.Model):
    webhook = models.OneToOneField(Webhook, models.DO_NOTHING, primary_key=True)
    created_at = models.DateTimeField()
    error_code = models.TextField(blank=True, null=True)
    req_data = models.JSONField(blank=True, null=True)
    rsp_data = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'webhook_delivery'
        unique_together = (('webhook', 'created_at'),)

        verbose_name = "Webhook Delivery"
        verbose_name_plural = "Webhook Deliveries"
