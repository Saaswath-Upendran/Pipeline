import pandas as pd
# import vcf
import numpy as np
# import subprocess

def genotype_multiannov_data(infile,patient_data,patient_name,base_dir):
    #output_folder = basepath+patient_id+"/genotyping_results/genotype_results.xlsx"
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
    #rsid_df = rsid_df[["Drug", "Description", "DRUG_CLASS", "Gene_name", "rsID", "Ref", "Alt", "HETERO/HOMO","GENOTYPE", "Evidence", "Func.refGene_y"]]
    rsid_df = rsid_df[["rsID", "Ref", "Alt", "HETERO/HOMO"]]
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
    #rsid_df = rsid_df[["rsID", "Ref", "Alt", "HETERO/HOMO","GENOTYPE", "GT", "multiannov/GVCF"]]
    #print(rsid_df)
    print("Extracted details present in multiannov file.")
    #rsid_df.drop(["Drug","Description","DRUG_CLASS","Gene_name","GENOTYPE","GENOTYPE","Evidence","Func.refGene_y"])
    #print(rsid_df)
    rsid_df.to_excel(f"{base_dir}/pharmacogenomics/genotyping/{patient_name}_genotype_rsid.xlsx")
    print("Take rest of genotype manually")

#genotype_multiannov_data("/media/sahal/kyvor1/patient_data/29-06-2023/INDTNR51091/INDTNR51091_multianno.hg19_multianno.txt", "/home/sahal/commants/PGx/DGE_rs_ID.xlsx")

