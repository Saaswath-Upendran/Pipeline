# Generated by Django 4.2.4 on 2023-08-28 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pgxpipelineapp', '0003_alter_pgxpipeline_log_end_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pgxpipeline_log',
            name='patient_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='pgxpipeline_log',
            name='start_time',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]