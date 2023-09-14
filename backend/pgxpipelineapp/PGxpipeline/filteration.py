import pandas as pd

class MainFilter:

    def MainFilter_single_gene(self,aldy_gene_sheet,patient_name,deplotype_sheet,db_sheet,base_dir):
        df = pd.read_excel(aldy_gene_sheet)
        df2 = pd.read_csv(deplotype_sheet)
        df3 = pd.read_csv(db_sheet)
        df["GENE SYMBOL"] = df["CORE GENES"][1:] 
        df["DIPLOTYPE"] = df["Unnamed: 1"][1:]
        # diplotype = df["Genotype"][df["Gene"] == 'CYP2D6'].values
        # Gene and Diplotype Filter
        merged_df = df.merge(df2, on=["GENE SYMBOL", "DIPLOTYPE"], how="inner")
        merged_df.to_excel(f"./{patient_name}_merged_df.xlsx",index=False)
        activity_score = merged_df["TOTAL ACTIVITY SCORE"].tolist()
        gene = merged_df["GENE SYMBOL"]
        phenotype = merged_df["PHENOTYPE"]
        print(gene,activity_score,phenotype)
        # print(merged_df["GENE SYMBOL"].values.tolist(),phenotype)
        # df3 = df3[df3['SINGLE PROFILE'] == "Yes"]
        # Gene and Phenotype Filter
        filtered_data = []
        filtered_activity_data = []
        for i,j in zip(merged_df["GENE SYMBOL"],merged_df["PHENOTYPE"]):
            filterd_df3 = df3[(df3["GENE/GENE_COMBINATION"].str.strip() == i)]
            filterd_df3 = filterd_df3[(df3["Phenotype 1"].str.lower() == j.lower())]
            filtered_data.append(filterd_df3)
        df3 = pd.concat(filtered_data)
        df3.to_excel(f"./{patient_name}_after_filteration_without_activity_score.xlsx",index=False)
        # Activity Score Filter
        for a in merged_df["TOTAL ACTIVITY SCORE"]:
            activity_score_filter = df3[(df3["Score 1A"] == a ) | (df3["Score 1B"] == a) | (df3["Score 1C"] == a) | (df3["Score 1D"] == a) | (df3["Score 1E"] == a) | (df3["Score 1F"] == a) | (df3["Score 1G"] == a) | (df3["Score 1H"] == a) | (df3["Score 1I"] ==a) | (df3["Score 1K"] == a)]
            filtered_activity_data.append(activity_score_filter)
        # print(filtered_activity_data)
        df3 = pd.concat(filtered_activity_data)
        # df3 = df3[(df3["Score 1A"].isin(activity_score)) | (df3["Score 1B"].isin(activity_score))]
        # df3.to_excel("./after_filteration_with_activity_score.xlsx",index=False) 
        df3 = df3[["DRUG","TYPE OF DRUG_GENE INTERACTION","DRUG_CLASS","Level of Evidence","GENE/GENE_COMBINATION","Additional Information","Professional Guidelines","Phenotype/RS_ID","Drug_Gene interaction","Type of Action","Phenotype_Category","Icon","Recommendation","Other not recommended Drugs","Recommended Drug","COMMENT_ARTI"]]
        df3.to_excel(f"{base_dir}/{patient_name}_Full_Result.xlsx",index=False)
        return True

    def MainFilter_combination_gene(self,aldy_genes,additional_sheet,patient_name,diplotype_sheet,db_sheet):
        df4 = pd.read_excel(aldy_genes)
        df5 = pd.read_excel(additional_sheet)
        df6 = pd.read_csv(diplotype_sheet)
        df7 = pd.read_csv(db_sheet)
        df4["GENE SYMBOL"] = df4["CORE GENES"][1:]
        df4["GENOTYPE"] = df4["Unnamed: 1"][1:]
        input_gene = "CYP2D6 + CYP2C19"
        # Dual Genes Filter
        input_genes = input_gene.split("+")
        diplotype = [df4["GENOTYPE"][df4["GENE SYMBOL"].str.lower() == i.strip().lower()].values for i in input_genes]
        # cmp_gene = [df6[(df6["GENE SYMBOL"].str.lower() == g.strip().lower()) ]for g in input_genes]
        # df6 = pd.concat(cmp_gene)
        # cmp_diplotype = [df6[(df6["DIPLOTYPE"] == d)] for d in diplotype]
        diplotype_values = [d for sublist in diplotype for d in sublist]
        cmp_diplotype = []
        for n,k in zip(input_genes,diplotype_values):
            cmp_gene = df6[(df6["GENE SYMBOL"].str.lower() == n.strip().lower()) & (df6["DIPLOTYPE"] == k)]
            cmp_diplotype.append(cmp_gene)
        df6 = pd.concat(cmp_diplotype)
        df6.to_excel(f"./{patient_name}_filter_after_gene_diplotype.xlsx",index=False)
        # Gene and Phenotype Filter
        filtered_data = []
        filtered_activity_data = []
        # df7 = df7[df7['SINGLE PROFILE'] == "No"]
        df7 = df7[(df7["GENE/GENE_COMBINATION"].str.strip() == input_gene)]
        for m in df6["PHENOTYPE"]:
            print(m)
            df7 = df7[(df7["Phenotype 1"].str.lower() == m.lower()) | (df7["Phenotype 2"].str.lower() == m.lower()) | (df7["Phenotype 3"].str.lower() == m.lower())]
            filtered_data.append(df7)
        # df7 = pd.concat(filtered_data)
        df7.to_excel(f"./{patient_name}_filtered_data_without_activity_score_dual.xlsx",index=False)
        for k in df6["TOTAL ACTIVITY SCORE"]:
            df7 = df7[(df7["Score 1A"] == k ) | (df7["Score 1B"] == k) | (df7["Score 1C"] == k) | (df7["Score 1D"] == k) | (df7["Score 1E"] == k) | (df7["Score 1F"] == k) | (df7["Score 1G"] == k) | (df7["Score 1H"] == k) | (df7["Score 1I"] ==k) | (df7["Score 1K"] == k) | (df7["Score 2A"] == k ) | (df7["Score 3A"] == k)]
            filtered_activity_data.append(df7)
            # & (df7["Phenotype 1"] == j)
        df7 = pd.concat(filtered_activity_data)
        df7 = df7[["DRUG","TYPE OF DRUG_GENE INTERACTION","DRUG_CLASS","Level of Evidence","GENE/GENE_COMBINATION","Additional Information","Professional Guidelines","Phenotype/RS_ID","Drug_Gene interaction","Type of Action","Phenotype_Category","Icon","Recommendation","Other not recommended Drugs","Recommended Drug","COMMENT_ARTI"]]
        df7.to_excel(f"./{patient_name}_with_activity_score.xlsx",index=False)
        # df7.to_excel(f"./{patient_name}_Full_Result.xlsx")
        return True


# Example Usage


#filters = MainFilter()

#filters.MainFilter_single_gene("/home/saaswath/Project/PGxDatabase/pgx_pipeline/ssm/T-MTX-SSM_aldy_genes.xlsx","T-MTX-SSM","/home/saaswath/Project/PGxDatabase/pgx_pipeline/support/PGx sample - Copy of DIPLOTYPE.csv","/home/saaswath/Project/PGxDatabase/pgx_pipeline/support/PGx sample - Copy of COMPLETE_INFO.csv")
#filters.MainFilter_combination_gene("/home/saaswath/Project/PGxDatabase/pgx_pipeline/ARP1/T_MTX_ARP1_aldy_genes.xlsx","/home/saaswath/Project/PGxDatabase/pgx_pipeline/ARP1/T_MTX_ARP1_additional_gene_GVCF.xlsx","T-MTX-ARP1","/home/saaswath/Project/PGxDatabase/pgx_pipeline/support/PGx sample - Copy of DIPLOTYPE.csv","/home/saaswath/Project/PGxDatabase/pgx_pipeline/support/PGx sample - Copy of COMPLETE_INFO.csv")



