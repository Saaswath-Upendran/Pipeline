from django.db import models
# Create your models here.


class Pgxpipeline_bam(models.Model):
    bamfile_path = models.CharField(max_length=150)  # FileField is a generic relation to files
    vcf_file_path = models.CharField(max_length=150)
    results_path = models.CharField(max_length=150)
    # bed_path = models.CharField(max_length=150)
    patient_name = models.CharField(max_length=150,unique=True)

    def __str__(self):
        return self.patient_name
class Pgxpipeline_log(models.Model):
    patient_name = models.ForeignKey(Pgxpipeline_bam,on_delete=models.CASCADE)
    start_time = models.CharField(max_length=150,null=True,blank=True)
    status = models.CharField(max_length=190)
    end_time = models.CharField(max_length=150,null=True,blank=True)
    total_time = models.CharField(max_length=150,null=True,blank=True)

    def __str__(self):
        return self.patient_name.patient_name


