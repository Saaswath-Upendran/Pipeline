from rest_framework import serializers 
from .models import Pgxpipeline_log
class BamSerializer(serializers.Serializer):
    sorted_bam = serializers.FileField()
    vcf_file = serializers.FileField()
    refrence_file =serializers.FileField()
    bed_file = serializers.FileField()
    patient_name = serializers.CharField(max_length=120)

class Pgxlog(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient_name.patient_name') 
    class Meta:
        model = Pgxpipeline_log
        fields = "__all__"


