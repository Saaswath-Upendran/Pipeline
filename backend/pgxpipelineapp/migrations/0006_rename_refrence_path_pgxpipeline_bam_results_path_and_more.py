# Generated by Django 4.2.4 on 2023-08-29 10:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pgxpipelineapp', '0005_remove_pgxpipeline_bam_bamfile_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pgxpipeline_bam',
            old_name='refrence_path',
            new_name='results_path',
        ),
        migrations.RemoveField(
            model_name='pgxpipeline_bam',
            name='bed_path',
        ),
    ]
