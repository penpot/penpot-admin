# Generated by Django 4.1.4 on 2022-12-19 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('penpot', '0002_task_alter_profile_options_alter_project_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField()),
                ('modified_at', models.DateTimeField()),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.TextField()),
                ('is_shared', models.BooleanField()),
                ('has_media_trimmed', models.BooleanField(blank=True, null=True)),
                ('revn', models.BigIntegerField()),
                ('data', models.BinaryField(blank=True, null=True)),
                ('ignore_sync_until', models.DateTimeField(blank=True, null=True)),
                ('comment_thread_seqn', models.IntegerField(blank=True, null=True)),
                ('data_backend', models.TextField(blank=True, null=True)),
                ('features', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'file',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='FileChange',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField()),
                ('session_id', models.UUIDField(blank=True, null=True)),
                ('revn', models.BigIntegerField()),
                ('data', models.BinaryField(blank=True, null=True)),
                ('changes', models.BinaryField(blank=True, null=True)),
                ('features', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'file_change',
                'managed': False,
            },
        ),
    ]