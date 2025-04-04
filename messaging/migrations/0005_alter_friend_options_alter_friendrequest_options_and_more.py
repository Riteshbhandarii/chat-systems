# Generated by Django 5.1.6 on 2025-04-03 20:52

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("messaging", "0004_auto_20250403_0212"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="friend",
            options={"ordering": ["-created_at"]},
        ),
        migrations.AlterModelOptions(
            name="friendrequest",
            options={
                "ordering": ["-timestamp"],
                "verbose_name": "Friend Request",
                "verbose_name_plural": "Friend Requests",
            },
        ),
        migrations.AlterModelOptions(
            name="groupchat",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Group Chat",
                "verbose_name_plural": "Group Chats",
            },
        ),
        migrations.AlterModelOptions(
            name="message",
            options={
                "ordering": ["timestamp"],
                "verbose_name": "Private Message",
                "verbose_name_plural": "Private Messages",
            },
        ),
        migrations.AddField(
            model_name="friend",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                verbose_name="Friendship creation date",
            ),
        ),
        migrations.AddField(
            model_name="groupchat",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="Creation date"
            ),
        ),
        migrations.AddField(
            model_name="groupchat",
            name="creator",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="created_groups",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Group creator",
            ),
        ),
        migrations.AlterField(
            model_name="friendrequest",
            name="timestamp",
            field=models.DateTimeField(
                auto_now_add=True, verbose_name="Request timestamp"
            ),
        ),
        migrations.AlterField(
            model_name="groupchat",
            name="members",
            field=models.ManyToManyField(
                related_name="group_chats",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Group members",
            ),
        ),
        migrations.AlterField(
            model_name="groupchat",
            name="name",
            field=models.CharField(max_length=255, verbose_name="Group name"),
        ),
        migrations.AlterField(
            model_name="message",
            name="content",
            field=models.TextField(verbose_name="Message content"),
        ),
        migrations.AlterField(
            model_name="message",
            name="read",
            field=models.BooleanField(default=False, verbose_name="Read status"),
        ),
        migrations.AlterField(
            model_name="message",
            name="receiver",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="received_messages",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Receiver",
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="sender",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Sender",
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="timestamp",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="Sent at"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="groupchat",
            unique_together={("name", "creator")},
        ),
        migrations.CreateModel(
            name="GroupMessage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.TextField(verbose_name="Message content")),
                (
                    "timestamp",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="Sent at"
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="messaging.groupchat",
                        verbose_name="Group",
                    ),
                ),
                (
                    "read_by",
                    models.ManyToManyField(
                        blank=True,
                        related_name="read_group_messages",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Read by users",
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Message sender",
                    ),
                ),
            ],
            options={
                "verbose_name": "Group Message",
                "verbose_name_plural": "Group Messages",
                "ordering": ["timestamp"],
            },
        ),
        migrations.DeleteModel(
            name="Groupmchatmessage",
        ),
    ]
