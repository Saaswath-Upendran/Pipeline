import pandas as pd
import numpy as np
import json

def splited(input_data,out_file,file_name,base_dir):
    df = pd.read_csv(input_data,sep="\t")
    df2 = pd.read_csv(out_file)
    df2["Gene"] = df2["CORE GENES"][1:] 
    df2["Genotype"] = df2["Unnamed: 1"][1:]
    nan_val = df2.isna().any(axis=1)
    nan = df2[nan_val]
    df3 = set(df["Gene"]).intersection(set(df2["Gene"]))

    gene_list = []
    dict_m = {}
    for i in df3:
        nan_vl = df2["Genotype"].isna()
        nan = df2[nan_vl]
        nan = nan.loc[nan["Gene"] == f'{i}']
        gene_list.append(nan["Gene"].values)
    for j in gene_list:
        for n in j:
            print(n)
            df4 = df.loc[df['Gene'] == f'{n}']
            Major = list(set(df4["Major"]))
            print(Major)
            dict_m[n] = Major
            df2["Unnamed: 1"] = df2.apply(lambda row: ",".join(str(f) for f in dict_m[n]) if row["Gene"] == n and pd.isna(row["Unnamed: 1"]) else row["Unnamed: 1"], axis=1)
    
    df2 = df2.drop("Gene",axis=1)
    df2 = df2.drop("Genotype",axis=1)
    df2.rename(columns={"Unnamed: 1":"","Unnamed: 2":""})
    df2.to_excel(f"{base_dir}/pharmacogenomics/report/{file_name}_aldy_genes.xlsx",index=False)




def GenoTypeMerge_With_rsid(input_file,output_file,patient_name,base_dir):
    
    df = pd.read_excel(input_file)
    df2 = pd.read_csv(output_file)

    #print(df["rsID"])
    df2["rsid"]=df2["Unnamed: 1"][1:]
    df3 = set(df2["rsid"]).intersection(set(df["rsID"]))
    print(df3)
    for i in df3:
        df4 = df.loc[df["rsID"] == f"{i}"]
        gt = list(set(df4["GT"]))
        print(gt)
    #print("genotype",df["GT"])
        for j in gt:
            df2["Unnamed: 2"] =df2.apply(lambda row: j if row["rsid"] == i and pd.isna(row["Unnamed: 2"]) else row["Unnamed: 2"], axis=1)

    df2 = df2.drop("rsid",axis=1)
    df2.rename(columns={"Unnamed: 1":"","Unnamed: 2":""})
    df2.to_excel(f"{base_dir}/pharmacogenomics/report/{patient_name}_additional_gene.xlsx",index=False)

def rsid_for_remaing(input_file1_j,output_file_s,patient_name,base_dir):

    df = pd.read_excel(input_file1_j)
    df2 = pd.read_excel(output_file_s)

    #rsID
    df2["rsid"]=df2["Unnamed: 1"][1:]
    df3 = set(df2["rsid"]).intersection(set(df["rsID"]))
    print(df3)
    for i in df3:
        df4 = df.loc[df["rsID"] == f"{i}"]
        gt = list(set(df4["GENOTYPE"]))
        print(gt)
    #print("genotype",df["GT"])
        for j in gt:
            df2["Unnamed: 2"] =df2.apply(lambda row: j if row["rsid"] == i and pd.isna(row["Unnamed: 2"]) else row["Unnamed: 2"], axis=1)

    df2 = df2.drop("rsid",axis=1)
    df2.rename(columns={"Unnamed: 1":"","Unnamed: 2":""})
    df2.to_excel(f"{base_dir}/pharmacogenomics/report/{patient_name}_additional_gene_GVCF.xlsx",index=False)
    

def merge_excel_files(input_file1, input_file2, output_file, sheet_name_1, sheet_name_2):
    try:
        df1 = pd.read_excel(input_file1)
        df2 = pd.read_excel(input_file2)

        with pd.ExcelWriter(output_file) as writer:
            df1.to_excel(writer, sheet_name=sheet_name_1, index=False)
            df2.to_excel(writer, sheet_name=sheet_name_2, index=False)

        print(f"Excel files merged successfully into {output_file} with sheet names {sheet_name_1} and {sheet_name_2}")
    except Exception as e:
        print(f"An error occurred: {e}")

def sample_solution_from_Aldy(input_file,patient_name,base_dir):
    df = pd.read_csv(input_file,sep="\t")
    df = df[df["Gene"] != "Gene"]
    solution_1_df = df[df["#Sample"].str.contains("#Solution ", na=False)]
    new_df = df.drop(df[["#Sample","SolutionID","Minor","Code","Status"]],axis=1)
    new_df["solution"] = solution_1_df["#Sample"].str.replace("#Solution ","") 
    
    new_df=new_df[["solution","Gene","Copy","Allele","Location","Type","Coverage","Effect","dbSNP"]]
    new_df.to_excel(f"{base_dir}/pharmacogenomics/report/{patient_name}_aldy_variants.xlsx", index=False)
    

# phase 2
def write_hla_results(input_file,out_file,patient_name,base_dir):
    df = pd.read_json(input_file)
    alleles_list = df["hla"]["alleles"]
    print(df["hla"]["alleles"])
    filtered_alleles_a = [allele.replace("A","") for allele in alleles_list if allele.startswith("A")]
    
    joined_alleles_a = "/".join(filtered_alleles_a)
    print(joined_alleles_a)
    filtered_alleles_b = [allele.replace("B","") for allele in alleles_list if allele.startswith("B")]
    
    joined_alleles_b = "/".join(filtered_alleles_b)
    print(joined_alleles_b)
    filtered_alleles_c = [allele.replace("C","") for allele in alleles_list if allele.startswith("C")]
    
    joined_alleles_c = "/".join(filtered_alleles_c)
    print(joined_alleles_c)
    filtered_alleles_drb1 = [allele.replace("DRB1","") for allele in alleles_list if allele.startswith("DRB1")]
    joined_alleles_drb1 = "/".join(filtered_alleles_drb1)
    df2 = pd.read_excel(out_file)
    df2["genes"] =  df2["Additional Genes Checked"][1:]
    # print(df2["genes"].str.contains("HLA-A") )
    df2.loc[df2["genes"] == "HLA-A", "Unnamed: 2"] = joined_alleles_a
    df2.loc[df2["genes"] == "HLA-B", "Unnamed: 2"] = joined_alleles_b
    df2.loc[df2["genes"] == "HLA-C", "Unnamed: 2"] = joined_alleles_c
    df2.loc[df2["genes"] == "HLA-DRB1" ,"Unnamed: 2"] = joined_alleles_drb1

    df2 = df2.drop("genes",axis=1)
    df2.to_excel(f"{base_dir}/pharmacogenomics/report/{patient_name}_results_with_all_additional_genotype.xlsx",index=False)
    #print(df2["Unnamed: 2"])


#phase 3 
    



# Example usage:

# aldy_result = "./pipeline_results/T-MTX-SP_aldy.txt"
# template = "./support/Aldy_Gene.csv"
# patient_name = "T-MTX-SP"
# file_with_rsid = "./pipeline_results/T-MTX-SP_genotype_rsid.xlsx"
# additional_gene = "./support/Additional_Gene.csv"
# splited(aldy_result,template,patient_name)
# GenoTypeMerge_With_rsid(file_with_rsid,additional_gene,patient_name)
# rsid_for_remaing(f"./pipeline_results/{patient_name}_results.xlsx",f"./pipeline_results/{patient_name}_additional_gene.xlsx","T-MTX-SP")
# input_file1 = f"/home/saaswath/Project/PGxDatabase/pgx_pipeline/pipeline_results/pharmacogenomics/report/T-MTX-DRV_aldy_genes.xlsx"
# input_file2 = f"/home/saaswath/Project/PGxDatabase/pgx_pipeline/pipeline_results/pharmacogenomics/report/T-MTX-DRV_additional_gene_GVCF.xlsx"
# output_file = f"./pipeline_results/final_report/T-MTX-DRV_final_results.xlsx"
# sheet_name_1 = "aldy genes"
# sheet_name_2 = "additional genes"

# merge_excel_files(input_file1, input_file2, output_file, sheet_name_1, sheet_name_2)
# sample_solution_from_Aldy(aldy_result,patient_name)


# structure variants pending

#write_hla_results("/home/saaswath/Project/PGxDatabase/pgx_outputs/pipeline_results/pharmacogenomics/xhla/T-MTX-DRV/report-T-MTX-DRV-hla.json","/home/saaswath/Project/PGxDatabase/pgx_outputs/pipeline_results/pharmacogenomics/report/T-MTX-DRV_additional_gene_GVCF.xlsx","T-MTX-DRV")

