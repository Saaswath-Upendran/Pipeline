from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser,MultiPartParser,FormParser
from django.conf import settings
import os
import pandas as pd
from django.http import FileResponse,JsonResponse
from .models import *
from .serializers import *
from .PGxpipeline.main1 import PgxBamRunner,create_directory
from .models import Pgxpipeline_log


details = []



def save_uploaded_file(folder, uploaded_file):
    file_path = os.path.join(folder, uploaded_file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    return file_path

class BamRunnerView(APIView):
    parser_classes = [MultiPartParser,FormParser]

    def post(self, request, *args, **kwargs):
        # print(request.data)
        
        patient_n = request.data.get('patient_name')
        details.append(patient_n)
        sorted_bam = request.FILES['sorted_bam']
        sorted_bam_bai = request.FILES['sorted_bam_bai']
        vcf_file = request.FILES['vcf_file']
        vcf_file_tbi = request.FILES["vcf_file_tbi"]
        pipeline_results = create_directory(f"{settings.MEDIA_ROOT}/pipeline_results")
        details.append(pipeline_results)
        pharmacogenomics = f"{pipeline_results}/pharmacogenomics"
        annotation = f"{pipeline_results}/annotation"
        aldy = f"{pharmacogenomics}/aldy"
        xhla_folder = f"{pharmacogenomics}/xhla"
        curation = f"{pipeline_results}/curation"
        genotyping_folder = f"{pharmacogenomics}/genotyping"
        report_folder = f"{pharmacogenomics}/report"
        final_report = f"{pipeline_results}/final_report"
        other_results = f"{pipeline_results}/other_results"
        input_files = f"{pipeline_results}/input_files"
        coverage_results = f"{pharmacogenomics}/coverage"
        os.mkdir(pharmacogenomics)
        os.mkdir(annotation)
        os.mkdir(curation)
        os.mkdir(aldy)
        os.mkdir(genotyping_folder)
        os.mkdir(report_folder)
        os.mkdir(final_report)
        os.mkdir(xhla_folder)
        os.mkdir(other_results)
        os.mkdir(input_files)
        os.mkdir(coverage_results)
        sorted_bam_path = save_uploaded_file(input_files, sorted_bam)
        sorted_bam_bai_path=save_uploaded_file(input_files,sorted_bam_bai)
        vcf_file_path = save_uploaded_file(input_files, vcf_file)
        vcf_file_tbi_path = save_uploaded_file(input_files,vcf_file_tbi)
        Pgxpipeline_bam.objects.create(
            bamfile_path = sorted_bam_path,
            vcf_file_path = vcf_file_path,
            results_path = pipeline_results,
            patient_name = patient_n
        )
        pipeline = PgxBamRunner(sorted_bam_path, vcf_file_path,patient_n, pipeline_results)
        return Response(pipeline)

    def get(self, request, *args, **kwargs):
        serailzers = BamSerializer()
        return Response(serailzers.data)

    def http_method_not_allowed(self, request, *args, **kwargs):
        raise Http404("Method not allowed")


def get_results1(request,id):
    fitlers = Pgxpipeline_bam.objects.get(patient_name=id) 
    results_with_aldy_genes = f"{fitlers.results_path}/pharmacogenomics/report/{id}_aldy_genes.xlsx"
    data = pd.read_excel(results_with_aldy_genes)
    res = data.to_dict(orient="records")
    return JsonResponse(res,safe=False)
    
def get_results2(request,id):
    filters = Pgxpipeline_bam.objects.get(patient_name=id)
    results_with_annovar = f"{filters.results_path}/pharmacogenomics/report/{id}_additional_gene.xlsx"
    data = pd.read_excel(results_with_annovar)
    res = data.to_dict(orient='records')
    return JsonResponse(res,safe=False)

def get_results3(request,id):
    filters = Pgxpipeline_bam.objects.get(patient_name=id)
    results_with_vcf = f"{filters.results_path}/pharmacogenomics/report/{id}_additional_gene_GVCF.xlsx"
    data = pd.read_excel(results_with_vcf)
    res = data.to_dict(orient="records")
    return JsonResponse(res,safe=False)

def get_results4(request,id):
    filters = Pgxpipeline_bam.objects.get(patient_name=id)
    results_with_xhla = f"{filters.results_path}/pharmacogenomics/report/{id}_results_with_all_additional_genotype.xlsx"
    data = pd.read_excel(results_with_xhla)
    res = data.to_dict(orient="records")
    return JsonResponse(res,safe=False)
    
def get_results5(request,id):
    filters = Pgxpipeline_bam.objects.get(patient_name=id)
    results_after_single_gene = f"{filters.results_path}/final_report/{id}_Full_Result.xlsx"
    data = pd.read_excel(results_after_single_gene)
    res = data.to_dict(orient="records")
    return JsonResponse(res,safe=False)

def get_history(request):
    history = Pgxpipeline_log.objects.all()
    serializer = Pgxlog(history,many=True)
    return JsonResponse(serializer.data, safe=False)
