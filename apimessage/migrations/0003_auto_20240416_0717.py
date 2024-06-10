# Generated by Django 3.2 on 2024-04-15 23:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apimessage', '0002_auto_20240416_0323'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystaticmodel',
            name='agent_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='apimessage.bot_llm_config', to_field='agent_id'),
        ),
        migrations.AddField(
            model_name='mystaticmodel',
            name='username',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='用户名'),
        ),
    ]
