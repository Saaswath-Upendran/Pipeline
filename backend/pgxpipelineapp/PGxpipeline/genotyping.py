import pandas as pd
import vcf
import numpy as np
import subprocess
import myvariant
mv = myvariant.MyVariantInfo()

####INPUT FILES####
#infile = "/home/josh/Patient_data_Feb/April/INDTNB32940-PVB/results/INDTNB32940/annotation_results/INDTNB32940_multianno.hg38_multianno.txt"
#patient_data = "/home/josh/DGE_Pipeline/Automation_Testing_Datasets/demo_1st_patient.xlsx" #Arti's input file with drug list and rsids
#gvcf_file = "/home/josh/basespace/Projects/INDTNR32940/AppSessions.v1/INDTNR32940_DGE/AppResults.312903615.INDTNR32940/Files/INDTNR32940.hard-filtered.gvcf.gz"
#hg38_or_hg19 = "hg38"
#basepath="/home/josh/Patient_data_Feb/April/INDTNB32940-PVB/results/"
#patient_id="INDTNB32940"
###################

####OUTPUT FILES####
#multiannov_output="/home/josh/DGE_Pipeline/Testing/INDTN10793_final_excel_multiannov.xlsx"
#other_output="/home/josh/DGE_Pipeline/Testing/INDTN10793_final_excel_others.xlsx"
#combined_output = "/home/josh/Patient_data_Feb/April/INDTNB32940-PVB/results/INDTNB32940_results.xlsx"
###################

def genotype_patient_data(infile,patient_data,combined_output,gvcf_file, hg38_or_hg19,ref,basepath,patient_id):
    corrected_gvcf = basepath+patient_id+"_corrected_gvcf.gvcf.gz"
    result = subprocess.run(['/mnt/disks/sdb/GATK/gatk-4.3.0.0/gatk-4.3.0.0/gatk','GenotypeGVCFs','-O',corrected_gvcf,'-R', f'{ref}', '-V', gvcf_file, '--call-genotypes', 'true', '--include-non-variant-sites', 'true'], stdout=subprocess.PIPE)
    print(result.stdout.splitlines())
    print("Hopefully, gvcf got generated successfully....")
    print("Called Genotyping module successfully. \nStarted reading Multiannov file...")
    df = pd.read_csv(infile,sep="\t", low_memory=False)
    df["Gene.refGene"] = df["Gene.refGene"].str.split(";").to_list()
    df = df.explode('Gene.refGene')
    df = df[df['Otherinfo10'] == "PASS"]
    print("Read Data\nSplitting columns")
    df = df.reset_index()
    for index,row in df.iterrows():
        try:
            temp = df.iloc[index,145].split(";")
            for ech in temp:
                temp1 = ech.split("=")
                df.loc[index,temp1[0]] = temp1[1]
            temp2 = df.iloc[index,146].split(":")
            temp3 = df.iloc[index,147].split(":")
            for loop in range(0,len(temp2)):
                df.loc[index,temp2[loop]] = temp3[loop]
        except IndexError:
            print("There is an error at index ",str(index))
            print(row)
    print(df.columns)

    pdata = pd.read_excel(patient_data, sheet_name="Sheet1") #You may have to change sheet name...
    print(pdata.shape)
    if("Ref" in pdata):
        pdata = pdata.drop(['Ref'], axis=1)
    if("Alt" in pdata):
        pdata = pdata.drop(['Alt'], axis=1)
    pdata["rsID"].fillna("-", inplace = True)
    pdata = pdata[pdata["rsID"].str.contains("rs")]
    rsids = pdata["rsID"].to_list()
    rsid = set(rsids)
    print(pdata.shape)
    pdata = pdata.drop(['HETERO/HOMO'], axis=1)
    print(pdata.columns)
    df = df[df["avsnp150"].isin(rsid)]
    #df.to_excel("/home/josh/DGE_Pipeline/Testing/INDTN10793_filtered_input.xlsx") #Automate this output file name...
    rsid_df = pd.merge(df,pdata,left_on="avsnp150",right_on="rsID",how="inner")
    rsid_df = rsid_df.rename(columns = {"GT":"HETERO/HOMO"})
    #You may need to change the below column names if columns in the input file changes.
    print(rsid_df.columns)
    rsid_df = rsid_df[["Drug", "Description", "DRUG_CLASS", "Gene_name", "rsID", "Ref", "Alt", "HETERO/HOMO","GENOTYPE", "Evidence", "Func.refGene"]]
    rsid_df = rsid_df.rename(columns = {'Ref':'REFERENCE','Alt':'ALT'})

    for index,row in rsid_df.iterrows():
        if(len(str(rsid_df.loc[index,"REFERENCE"]))>1) or (len(str(rsid_df.loc[index,"ALT"]))>1):
            rsid_df.loc[index,"GT"]="Complex genotype"
        elif(str(rsid_df.loc[index,"HETERO/HOMO"])=="0/1"):
            rsid_df.loc[index,"GT"]=str(rsid_df.loc[index,"REFERENCE"])+str(rsid_df.loc[index,"ALT"])
        elif(str(rsid_df.loc[index,"HETERO/HOMO"])=="0|1"):
            rsid_df.loc[index,"GT"]=str(rsid_df.loc[index,"REFERENCE"])+str(rsid_df.loc[index,"ALT"])
        elif(str(rsid_df.loc[index,"HETERO/HOMO"])=="0/0"):
            rsid_df.loc[index,"GT"]=str(rsid_df.loc[index,"REFERENCE"])+str(rsid_df.loc[index,"REFERENCE"])
        elif(str(rsid_df.loc[index,"HETERO/HOMO"])=="0|0"):
            rsid_df.loc[index,"GT"]=str(rsid_df.loc[index,"REFERENCE"])+str(rsid_df.loc[index,"REFERENCE"])
        elif(str(rsid_df.loc[index,"HETERO/HOMO"])=="1/1"):
            rsid_df.loc[index,"GT"]=str(rsid_df.loc[index,"ALT"])+str(rsid_df.loc[index,"ALT"])
        elif(str(rsid_df.loc[index,"HETERO/HOMO"])=="1|1"):
            rsid_df.loc[index,"GT"]=str(rsid_df.loc[index,"ALT"])+str(rsid_df.loc[index,"ALT"])
        else:
            rsid_df.loc[index,"GT"]="Unknown_genotype"
    
    print(rsid_df["HETERO/HOMO"])
    print(rsid_df["GT"].to_list())
    filtered_rsids = rsid_df["rsID"].to_list()
    rsid_df["multiannov/GVCF"] = "Present in multiannov file."
    print("Extracted details present in multiannov file.")
    filtered_rsid = set(filtered_rsids)
    final_datasets = pdata[~pdata["rsID"].isin(filtered_rsid)]
    final_datasets = final_datasets.reset_index()

    vcf_reader = vcf.Reader(filename=corrected_gvcf)
    for index,row in final_datasets.iterrows():
        rid = final_datasets.iloc[index,5]   # Change here if columns in file changes.
        print(rid, end ="\t")
        search_term = 'dbsnp.rsid:'+str(rid)
        snp_details = mv.query(search_term, fields='dbsnp', assembly=hg38_or_hg19) #REMEMBER to change hg38 to hg19 if reference sequence changes.
        if(len(snp_details["hits"]) == 0):
            final_datasets.loc[index,'multiannov/GVCF']="RsID not found. Probably might have been merged into another rsid. Please make sure to provide only recent rsIDs."
            continue
        loc = snp_details["hits"][0]["_id"]
        chromosome = loc.split(":")[0]
        pos = loc.split(":")[1].replace("g.","")
        st = ""
        ref_alt = ""
        stop_signal=0
        print(loc)
        for ech_letter in pos:
            try:
                if(stop_signal==0):
                    st = st+str(int(ech_letter))
            except ValueError:
                ref_alt = ref_alt + ech_letter
                if(ech_letter == "_"):
                    stop_signal = 1

        final_datasets.loc[index,'Chr']=chromosome
        final_datasets.loc[index,'Start']=st
        if(">" in pos):
            final_datasets.loc[index,'REFERENCE']=ref_alt.split(">")[0]
            final_datasets.loc[index,'ALT']=ref_alt.split(">")[1]
            final_datasets.loc[index,'GT']=ref_alt.split(">")[0]+ref_alt.split(">")[0]
        #Check if this location is present in gvcf file.
        if(st!=""):
            for record in vcf_reader.fetch(chromosome, int(st)-1, int(st)):
                if(record.CHROM==chromosome) and (int(record.POS)==int(st)):
                    final_datasets.loc[index,"multiannov/GVCF"]="Present in gvcf file"
                    final_datasets.loc[index,"HETERO/HOMO"]="0/0"
                    final_datasets.loc[index,"GENOTYPE"]=str(final_datasets.loc[index,"REFERENCE"])+str(final_datasets.loc[index,"REFERENCE"])
                else:
                    print(rid+" is not found in both multiannov file or in gvcf file")
                    final_datasets.loc[index,"multiannov/GVCF"]="NOT found in multiannov file or in gvcf file. "+chromosome+":"+st
                    final_datasets.loc[index,'GT']="NaN"
                    final_datasets.loc[index,'GENOTYPE']="NaN"
        else:
            final_datasets.loc[index,"multiannov/GVCF"]="NOT found in multiannov file or in gvcf file. St is empty"
            final_datasets.loc[index,'GT']="NaN"
            final_datasets.loc[index,'GENOTYPE']="NaN"
    #rsid_df.to_excel(multiannov_output,index=False)
    final_datasets.drop(['index'], axis=1, inplace=True)
    #final_datasets.to_excel(other_output,index=False)
    combined_datasets = pd.concat([rsid_df, final_datasets], ignore_index=True)
    combined_datasets["multiannov/GVCF"].fillna("Not present in both multiannov and gvcf.")
    combined_datasets.to_excel(combined_output,index=False)
    #return(combined_datasets)  #Hashout this line while running pipeline.... It's only for aldy_validation.py

#genotype_patient_data(infile,patient_data,combined_output,gvcf_file, hg38_or_hg19,basepath,patient_id)
