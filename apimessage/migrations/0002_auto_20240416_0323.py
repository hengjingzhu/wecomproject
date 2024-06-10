# Generated by Django 3.2 on 2024-04-15 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apimessage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyStaticModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('video', models.ImageField(blank=True, null=True, upload_to='video/')),
                ('voice', models.ImageField(blank=True, null=True, upload_to='voice/')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否活跃')),
            ],
        ),
        migrations.AlterField(
            model_name='bot_llm_config',
            name='agent_name',
            field=models.CharField(max_length=255, verbose_name='bot名字'),
        ),
        migrations.AlterField(
            model_name='generalblackbox',
            name='corp_id',
            field=models.CharField(max_length=255, verbose_name='企业微信corpid'),
        ),
    ]