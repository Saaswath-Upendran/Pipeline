import os
from multiprocessing import Process
import time
from .genotyping import *
from .genotype_from_multi_anno import *
from .aldy_main import *
from .DGE_split import *
from pgxpipelineapp.models import *
from django.utils import timezone
from .filteration import MainFilter

# Now, any Python code executed from here will run in the activated virtual environment.

def annovarRunner(vcf_input,ref,output_loc):
    #annovar path and database location
    annovar_cmd_avi = f"perl /mnt/disks/sdb/GATK/annovar/convert2annovar.pl -format vcf4 {vcf_input} -outfile {output_loc}.avinput -includeinfo -withzyg"
    print(annovar_cmd_avi)
    out = os.popen(annovar_cmd_avi).read()
    if 'Error:' in str(out):
        print(out)
    else:
        print("Annovar Avi Generated")
    if ref == "Hg38":        
        
        annovar_cmd = f"perl /mnt/disks/sdb/GATK/annovar/table_annovar.pl {output_loc}.avinput /mnt/disks/sdb/GATK/humandb/ -buildver hg38 -out {output_loc} -remove -protocol refGene,cytoband,exac03,1000g2015aug_all,1000g2015aug_afr,1000g2015aug_amr,1000g2015aug_sas,1000g2015aug_eur,1000g2015aug_eas,avsnp150,dbnsfp42c,cosmicv96_coding,clinvar_20190305,esp6500siv2_all,gnomad211_exome,intervar_20180118 -operation g,r,f,f,f,f,f,f,f,f,f,f,f,f,f,f -polish -otherinfo -nastring ."
        print(annovar_cmd)
        out = os.popen(annovar_cmd).read()
        if 'Error:' in str(out):
            print(out)
        else:
            print("Annovar Completed")
    else:

        annovar_cmd = f"perl /mnt/disks/sdb/GATK/annovar/table_annovar.pl {output_loc}.avinput /mnt/disks/sdb/GATK/annovar/humandb/ -buildver hg19 -out {output_loc}  -remove -protocol refGene,cytoband,exac03,1000g2015aug_all,1000g2015aug_afr,1000g2015aug_amr,1000g2015aug_sas,1000g2015aug_eur,1000g2015aug_eas,avsnp150,dbnsfp35c,cosmic92_coding,clinvar_20190305,esp6500siv2_all,gnomad211_exome,intervar_20180118 -operation g,r,f,f,f,f,f,f,f,f,f,f,f,f,f,f -polish -otherinfo -nastring ."    
        print(annovar_cmd_avi)
        out = os.popen(annovar_cmd).read()
        if 'Error:' in str(out):
            print(out)
        else:
            print("Annovar Completed")
    return True

def liftover(sort_bam,out_path,patient_name,base_dir):
    bam_inst = Pgxpipeline_bam.objects.get(patient_name=patient_name)
    Pgxpipeline_log.objects.filter(patient_name=bam_inst).update(status="started xhla")
    cmd = f"CrossMap.py bam /mnt/disks/sdb/GATK/tools/hg19ToHg38.over.chain.gz {sort_bam} {out_path}/{patient_name}_Hg38"
    print(cmd)
    out = os.popen(cmd).read()
    if 'Error:' in str(out):
        print(out)
    else:
        print("Cross Map Completed")
    crossmap = f"{base_dir}/other_results/{patient_name}_Hg38.sorted.bam"
    cmd = f"docker run -v `pwd`:`pwd` -w `pwd` humanlongevity/hla \--sample_id {patient_name} --input_bam_path {crossmap} --output_path {patient_name}_xhla"
    print(cmd)
    out = os.popen(cmd).read()
    if 'Error:' in str(out):
        print(out)
    else:
        print("XHLA Completed")
    print("Moving Xhla results")
    out = os.popen(f"sudo mv ./{patient_name}_xhla   {base_dir}/pharmacogenomics/xhla/{patient_name}").read()
    Pgxpipeline_log.objects.filter(patient_name=bam_inst).update(status="Completed xhla")
    return True

def haplotypecaller(sort_bam,bed_file,vcf_file,gvcf_vcf,reference,patient_name,base_dir):
    
    str_tab = f"./{base_dir}/{patient_name}.table"
    out_put = f"./{base_dir}/{patient_name}_drag.txt"
    final_vcf = f"./{base_dir}/{patient_name}_hardfiltered.vcf"
    multi_anno = f"./{base_dir}/annotation/{patient_name}.hg19_multianno.txt"
    results1 = f"./{base_dir}/pharmacogenomics/genotyping/{patient_name}_results.xlsx"
    gvcf_path = f"./{base_dir}/other_results/{patient_name}.g.vcf.gz"
    other_res_folder = f"./{base_dir}/pharmacogenomics/other_results/"
    additional_gene_res = f"./{base_dir}/pharmacogenomics/report/{patient_name}_additional_gene.xlsx"
    additional_gene_res_gvcf = f"./{base_dir}/pharmacogenomics/report/{patient_name}_additional_gene_GVCF.xlsx"
    final_result = f"./{base_dir}/pharmacogenomics/final_report/{patient_name}_final_results.xlsx"
    aldy_gene_res = f"./{base_dir}/pharmacogenomics/report/{patient_name}_aldy_genes.xlsx"
    aldy_main_res = f"./{base_dir}/pharmacogenomics/aldy/{patient_name}_aldy.txt"
    curation_path = f"./{base_dir}/curation/"
    genotype_rsid_res = f"./{base_dir}/pharmacogenomics/genotyping/{patient_name}_genotype_rsid.xlsx"
    pharmacogenomics_folder = f"./{base_dir}/pharmacogenomics/"
    cmd = "/mnt/disks/sdb/GATK/gatk-4.3.0.0/gatk-4.3.0.0/gatk --java-options -Xmx8g ComposeSTRTableFile -R {reference_file} -O {str_tab}".format(reference_file=reference,str_tab=str_tab)
    print(cmd)
    out = os.popen(cmd).read()

    print("Strated Calibratedragstrmodel....")
    cmd = "/mnt/disks/sdb/GATK/gatk-4.3.0.0/gatk-4.3.0.0/gatk --java-options -Xmx8g CalibrateDragstrModel -R {ref_file} -I {in_file} -str {table} -O {out_file}".format(ref_file=reference,in_file=sort_bam,table=str_tab,out_file=out_put)
    print(cmd)
    out = os.popen(cmd).read()
    if 'Error:' in str(out):
        print(out)
    else:
        print("Calibrate Drag Str Model Completed")
    print("Started haplotypecaller....")
   
    cmd = "/mnt/disks/sdb/GATK/gatk-4.3.0.0/gatk-4.3.0.0/gatk --java-options -Xmx8g HaplotypeCaller -R {ref} -I {sortedbam_file} -L {bedfile} -O {output} --dragen-mode true --dragstr-params-path {drag}".format(ref=reference,sortedbam_file=sort_bam,bedfile=bed_file,output=vcf_file,drag=out_put)
    print(cmd)
    out = os.popen(cmd).read()
    if 'Error:' in str(out):
        print(out)
    else:
        print("Haplotypecaller  VCF Generation Completed")
    file_created = False
    while not file_created:
        if os.path.exists(f"./pipeline_results/{patient_name}.vcf"):
            file_created =True
        time.sleep(1)
    print("\n....strated variant filtration....")
    cmd = r"""/mnt/disks/sdb/GATK/gatk-4.3.0.0/gatk-4.3.0.0/gatk --java-options -Xmx8g VariantFiltration -V {vcf_in} --filter-expression "QUAL < 10.4139" --filter-name "DRAGENHardQUAL" -O {vcf_out}""".format(vcf_in=vcf_file,vcf_out=final_vcf)
    print(cmd)
    out = os.popen(cmd).read()
    if 'Error:' in str(out):
        print(out)
    else:
        print("Calibrate Drag Str Model Completed")
    
    annovarRunner(final_vcf,"Hg19",f"./{base_dir}/annotation/{patient_name}")
    run_cmd = genotype_multiannov_data(multi_anno,"./support/DGE_rs_ID.xlsx",patient_name,base_dir)
    run_cmd4 = splited(aldy_main_res,"./support/Aldy_Gene.csv",patient_name,base_dir)
    run_cmd5 = GenoTypeMerge_With_rsid(genotype_rsid_res,"./support/Additional_Gene.csv",patient_name,base_dir)
    cmd = r"""/mnt/disks/sdb/GATK/gatk-4.3.0.0/gatk-4.3.0.0/gatk --java-options -Xmx8g HaplotypeCaller -R {ref} -I {sortbam} -O {outfile} -L {bedfile} --minimum-mapping-quality 20 --min-base-quality-score 20  -ip 200  -ERC GVCF """.format(ref=reference,sortbam=sort_bam,outfile=gvcf_vcf,bedfile=bed_file)
    print(cmd)
    out = os.popen(cmd).read()
    time.sleep(60)
    if 'Error:' in str(out):
        print(out)
    else:
        print("Haplotypecaller GVCF Generation Completed")
    
    run_cmd3 = liftover(sort_bam,pharmacogenomics_folder,patient_name,base_dir)
    # run_cmd2 = genotype_patient_data(multi_anno,"./support/demo_1st_patient.xlsx",results1,gvcf_path,"hg19",reference,other_res_folder,patient_name)
    run_cmd6 = rsid_for_remaing(results1,additional_gene_res,patient_name,base_dir)
    sheet_name_1 = "aldy genes"
    sheet_name_2 = "additional genes"
    run_cmd7 = merge_excel_files(aldy_gene_res,additional_gene_res_gvcf,final_result,sheet_name_1,sheet_name_2)
    run_cmd8 = sample_solution_from_Aldy(aldy_main_res,patient_name,base_dir)
    return True
def aldy_runner(sorted_bam,base_dir,profile_file1,aldy_out,patient_name,targeted_seq=False):
    bam_inst = Pgxpipeline_bam.objects.get(patient_name=patient_name)

    Pgxpipeline_log.objects.filter(patient_name=bam_inst).update(status="Started Aldy")
    if targeted_seq:
        cmd = "aldy profile {profile_bam} > {profile_file}".format(profile_bam=sorted_bam,profile_file=profile_file1)
        print(cmd)
        out = os.popen(cmd).read()
        if 'Error:' in str(out):
            print(out)
        else:
            print("Profile file generated")
        
        profile_file1 = f"{base_dir}/pharmacogenomics/aldy/{patient_name}.profile"
        file_created = False
        while not file_created:
           if os.path.exists(profile_file1):
               file_created = True
           time.sleep(1)
        cmd = "aldy genotype -p {profile_file1} {gene} -o {out_file}.txt".format(gene=sorted_bam,out_file=aldy_out,profile_file1=profile_file1)
        print(cmd)
        out = os.popen(cmd).read()
        if 'Error:' in str(out):
            print(out)
        else:
            print("Aldy completed successfully.")
    else:
        cmd = "aldy genotype -p wes {gene}.sorted.bam -o {out_file}.txt".format(gene=sorted_bam,out_file=aldy_out)
        print(cmd)
        out = os.popen(cmd).read()
        if 'Error:' in str(out):
            print(out)
        else:
            print("Aldy completed successfully.")
    Pgxpipeline_log.objects.filter(patient_name=bam_inst).update(status="Completed Aldy")
    return True

def create_directory(directory):
    if os.path.exists(directory):
        # If the directory already exists, append "_1" to the directory name
        base_directory = directory
        counter = 1
        while os.path.exists(f"{base_directory}_{counter}"):
            counter += 1
        directory = f"{base_directory}_{counter}"
    os.mkdir(directory)
    return directory




def PgxFastqRunner(input_file1,input_file2,bed_file,read_group,reference1,patient_name):
    print("Started Pipeline with FastQ Running bwa ...")
    try:
        pipeline_results = create_directory("pipeline_results")
        pharmacogenomics = f"./{pipeline_results}/pharmacogenomics"
        annotation = f"./{pipeline_results}/annotation"
        aldy = f"./{pipeline_results}/pharmacogenomics/aldy"
        xhla_folder = f"./{pipeline_results}/pharmacogenomics/xhla"
        curation = f"./{pipeline_results}/curation"
        genotyping_folder = f"./{pipeline_results}/pharmacogenomics/genotyping"
        report_folder = f"./{pipeline_results}/pharmacogenomics/report"
        final_report = f"./{pipeline_results}/final_report"
        other_results = f"./{pipeline_results}/other_results"
        sam_file = f'./{pipeline_results}/other_results/{patient_name}.sam'
        out_bam = f"./{pipeline_results}/other_results/{patient_name}.bam"
        sorted_bam = f"./{pipeline_results}/other_results/{patient_name}_s.sorted.bam"
        metrics = f"./{pipeline_results}/other_results/{patient_name}_metrics.txt"
        spark_sorted_bam = f"./{pipeline_results}/other_results/{patient_name}_spark.bam"
        spark_sorted_bam_bai = f"./{pipeline_results}/other_results/{patient_name}_spark.bam.bai"
        os.mkdir(pharmacogenomics)
        os.mkdir(annotation)
        os.mkdir(curation)
        os.mkdir(aldy)
        os.mkdir(genotyping_folder)
        os.mkdir(report_folder)
        os.mkdir(final_report)
        os.mkdir(xhla_folder)
        os.mkdir(other_results)
        #------------------------------------------------------------------------------------BWA---------------------------------------------------------------------------------------------#
        cmd = r"bwa mem -t 24 -R '{read_g}', {reference}  {input_file_1}  {input_file_2}  >  {sam_file}".format(read_g=read_group,input_file_1=input_file1,input_file_2=input_file2,sam_file=sam_file,reference=reference1)
        print(cmd)
        out = os.popen(cmd).read()
        if 'Error:' in str(out):
            print(out)
        else:
            print("BWA tool Completed")
        print("running samtools for view ")
        #-------------------------------------------------------------------------------------SamTools View ---------------------------------------------------------------------------------#
        print("sam to bam conversion")
        cmd = "samtools view -S -b {in_file} > {Out_file}".format(in_file=sam_file,Out_file=out_bam) 
        print(cmd)
        out = os.popen(cmd).read()
        if 'Error:' in str(out):
            print(out)
        else :
            print("SamTools View completed")
        #---------------------------------------------------------------------------------------SamTools Sort ------------------------------------------------------------------------------#
        print("Sorting bam file started ")
        cmd = "samtools sort {In_file} -o {sort_file}".format(In_file=out_bam ,sort_file=sorted_bam)
        print(cmd)
        out = os.popen(cmd).read()
        if 'Error:' in str(out):
            print(out)
        else :
            print("SamTools Sort completed")
        #---------------------------------------------------------------------------------------GATK----------------------------------------------------------------------------------------#
        print("markduplicatesspark")
        cmd = "picard MarkDuplicates I={bam_file} M={metrics} O={spark} ".format(bam_file=sorted_bam,metrics=metrics,spark=spark_sorted_bam)
        print(cmd)
        out = os.popen(cmd).read()
        if 'Error:' in str(out):
            print(out)
        else :
            print("GATK mark duplicate completed")
        print("Started Bam index")
        cmd = "samtools index {dup}.bam {out}.bam.bai".format(dup=spark_sorted_bam,out=spark_sorted_bam_bai)
        print(cmd)
        out = os.popen(cmd).read()
        if 'Error:' in str(out):
            print(out)
        else :
            print("Samtools index completed")
        file_detected = False
        while not file_detected:
            if os.path.exists(spark_sorted_bam_bai):
                print("File detected")
                file_detected = True
            time.sleep(1)
        start_time = time.time()
        p1 = Process(target=haplotypecaller,args=(spark_sorted_bam,bed_file,f"../pipeline_results/other_results/{patient_name}.vcf",f"./pipeline_results/other_results{patient_name}.g.vcf.gz",reference1,patient_name))
        p2 = Process(target=aldy_runner,args=(spark_sorted_bam,f"./pipeline_results/pharmacogenomics/aldy/{patient_name}.profile",f"./pipeline_results/pharmacogenomics/aldy/{patient_name}_aldy",patient_name,True))
        p1.start()
        p2.start()
        p1.join()
        p2.join()
        end_time = time.time()
        total_time = round((end_time - start_time)/60 , 3)
        print(f"time taken: {total_time} mins")
    except OSError as error:
            print(error)    
    
    

#PgxFastqRunner(input_file1="/mnt/disks/sdb/GATK/T-MTX-DRV_1/T-MTX-DRV/fastq_files/T-MTX-DRV_S89_L001_R1_001.fastq.gz",input_file2="/mnt/disks/sdb/GATK/T-MTX-DRV_1/T-MTX-DRV/fastq_files/T-MTX-DRV_S89_L001_R2_001.fastq.gz",reference1="/mnt/disks/sdb/GATK/hg19/hg19.fa",bed_file="/mnt/disks/sdb/GATK/SLEEK_Chr.bed",patient_name="T-MTX-DRV",read_group="@RG\tID:H352LDSX7\tLB:LB0\tPL:PL0\tPM:PU0\tSM:T-MTX-DRV")




def haplotypecaller_bam(final_vcf,base_dir,sort_bam,reference,gvcf_vcf,bed_file,patient_name):
    bam_inst = Pgxpipeline_bam.objects.get(patient_name=patient_name)

    log = Pgxpipeline_log.objects.filter(patient_name=bam_inst).update(
        status = "Started haplotypecaller"
    )
    coverage_result = f"{base_dir}/pharmacogenomics/coverage/{patient_name}_rsid_coverage.xlsx"
    multi_anno = f"{base_dir}/annotation/{patient_name}.hg19_multianno.txt"
    results1 = f"{base_dir}/pharmacogenomics/genotyping/{patient_name}_results.xlsx"
    gvcf_path = f"{base_dir}/other_results/{patient_name}.g.vcf.gz"
    other_res_folder = f"{base_dir}/other_results/"
    additional_gene_res = f"{base_dir}/pharmacogenomics/report/{patient_name}_additional_gene.xlsx"
    additional_gene_res_gvcf = f"{base_dir}/pharmacogenomics/report/{patient_name}_additional_gene_GVCF.xlsx"
    final_result = f"{base_dir}/final_report/{patient_name}_final_results.xlsx"
    aldy_gene_res = f"{base_dir}/pharmacogenomics/report/{patient_name}_aldy_genes.xlsx"
    aldy_com = f"{base_dir}/pharmacogenomics/report/{patient_name}_aldy_variants.xlsx"
    aldy_main_res = f"{base_dir}/pharmacogenomics/aldy/{patient_name}_aldy.txt"
    curation_path = f"{base_dir}/curation/"
    diplotype_sheet = "/mnt/disks/sdb/GATK/pgx_pipeline2/backend/pgxpipelineapp/PGxpipeline/support/PGx sample - Copy of DIPLOTYPE.csv"
    db_sheet = "/mnt/disks/sdb/GATK/pgx_pipeline2/backend/pgxpipelineapp/PGxpipeline/support/PGx sample - Copy of REFINED.csv"
    genotype_rsid_res = f"{base_dir}/pharmacogenomics/genotyping/{patient_name}_genotype_rsid.xlsx"
    pharmacogenomics_folder = f"{base_dir}/other_results"
    hla = f"{base_dir}/pharmacogenomics/xhla/{patient_name}/report-{patient_name}-hla.json"
    hla_results = f"{base_dir}/pharmacogenomics/report/{patient_name}_results_with_all_additional_genotype.xlsx"
    annovarRunner(final_vcf,"Hg19",f"{base_dir}/annotation/{patient_name}")
    final_split = split_multiannov(multi_anno,patient_name,base_dir)
    run_cmd = genotype_multiannov_data(multi_anno,"/mnt/disks/sdb/GATK/pgx_pipeline2/backend/pgxpipelineapp/PGxpipeline/support/DGE_rs_ID.xlsx",patient_name,base_dir)
    run_cmd4 = splited(aldy_main_res,"/mnt/disks/sdb/GATK/pgx_pipeline2/backend/pgxpipelineapp/PGxpipeline/support/Aldy_Gene.csv",patient_name,base_dir)
    run_cmd5 = GenoTypeMerge_With_rsid(genotype_rsid_res,"/mnt/disks/sdb/GATK/pgx_pipeline2/backend/pgxpipelineapp/PGxpipeline/support/Additional_Gene.csv",patient_name,base_dir)
    run_cmd3 = liftover(sort_bam,pharmacogenomics_folder,patient_name,base_dir)
    cmd = r"""/mnt/disks/sdb/GATK/gatk-4.3.0.0/gatk-4.3.0.0/gatk --java-options -Xmx8g HaplotypeCaller -R {ref} -I {sortbam} -L {bed_file} -O {outfile}  --minimum-mapping-quality 20 --min-base-quality-score 20  -ip 200  -ERC GVCF """.format(ref=reference,sortbam=sort_bam,bed_file=bed_file,outfile=gvcf_vcf)
    print(cmd)
    out = os.popen(cmd).read()
    time.sleep(60)
    if 'Error:' in str(out):
        print(out)
    else:
        print("Haplotypecaller GVCF Generation Completed")
    run_cmd2 = genotype_patient_data(multi_anno,"/mnt/disks/sdb/GATK/pgx_pipeline2/backend/pgxpipelineapp/PGxpipeline/support/DGE_rs_ID.xlsx",results1,gvcf_path,"hg19",reference,other_res_folder,patient_name)
    run_cmd6 = rsid_for_remaing(results1,additional_gene_res,patient_name,base_dir)
    run_cmd = os.popen(f"Rscript /mnt/disks/sdb/GATK/pgx_pipeline2/backend/pgxpipelineapp/PGxpipeline/support/Coverage_rsid_pipeline.R --bam {sort_bam} --coverage  /mnt/disks/sdb/GATK/pgx_pipeline2/backend/pgxpipelineapp/PGxpipeline/support/DGE_rs_ID.xlsx --result {coverage_result}")
    sheet_name_1 = "aldy genes"
    sheet_name_2 = "additional genes"
    run_cmd11 = write_hla_results(hla,additional_gene_res_gvcf,patient_name,base_dir)
    run_cmd8 = sample_solution_from_Aldy(aldy_main_res,patient_name,base_dir)
    run_cmd7 = merge_excel_files(aldy_main_res,hla_results,final_result,sheet_name_1,sheet_name_2)
    run_cmd = MainFilter().MainFilter_single_gene(aldy_gene_res,patient_name,diplotype_sheet,db_sheet,base_dir)
    run_cmd = MainFilter().MainFilter_combination_gene(aldy_gene_res,hla_results,patient_name,diplotype_sheet,db_sheet)
    Pgxpipeline_log.objects.filter(patient_name=bam_inst).update(
        status="Completed HaplotypeCaller"
    )
    return True

def PgxBamRunner(input_file,vcf_file,patient_name,base_dir):
    try:
        timezone.activate('Asia/Kolkata')
        reference = "/mnt/disks/sdb/GATK/hg19/hg19.fa"
        bed_file = "/mnt/disks/sdb/GATK/New_Sleek_August_2023.bed"
        start_time = time.time()
        start = timezone.localtime()
        bam_inst = Pgxpipeline_bam.objects.get(patient_name=patient_name)
        Pgxpipeline_log.objects.create(
            patient_name=bam_inst,
            start_time = start,
            status = "Started",
        )
        p1 = Process(target=haplotypecaller_bam,args=(vcf_file,base_dir,input_file,reference,f"{base_dir}/other_results/{patient_name}.g.vcf.gz",bed_file,patient_name))
        p2 = Process(target=aldy_runner,args=(input_file,base_dir,f"{base_dir}/pharmacogenomics/aldy/{patient_name}.profile",f"{base_dir}/pharmacogenomics/aldy/{patient_name}_aldy",patient_name,True))
        p1.start()
        p2.start()
        p1.join()
        p2.join()
        end_time = time.time()
        end = timezone.localtime()
        total_time = round((end_time - start_time)/60 , 3)
        print(f"Pipeline Completed time taken: {total_time} mins")
        results = {
            "Annovar and Xhla" : p1.exitcode,
            "Aldy status" : p2.exitcode,
            "time taken" : total_time
        }
        Pgxpipeline_log.objects.filter(patient_name=bam_inst).update(
            end_time= end,
            status="Pipeline Completed",
            total_time = f"{total_time} mins"
        )
        return results
    except (OSError,FileNotFoundError,FileExistsError) as error:
            return error

#PgxBamRunner(input_file="/mnt/disks/sdb/GATK/pgx_pipeline/input_data/T-MTX-DRV.bam",vcf_file="/mnt/disks/sdb/GATK/pgx_pipeline/input_data/T-MTX-DRV.hard-filtered.vcf.gz",reference="/mnt/disks/sdb/GATK/hg19/hg19.fa",bed_file="/mnt/disks/sdb/GATK/SLEEK_Chr.bed",patient_name="T-MTX-DRV")
