import pandas as pd
import sys

#infile = sys.argv[1]
#second_argv = sys.argv[2]

def split_multiannov(infile, second_argv,base_dir):
    df = pd.read_csv(infile,sep="\t", low_memory=False)
    print("Read Input File Successfully!!!")
    df["Gene.refGene"] = df["Gene.refGene"].str.split(";").to_list()
    df = df.explode('Gene.refGene')
    df = df[df['Otherinfo10'] == "PASS"]

    df = df.rename(columns={'DP': 'DP_Total'})
    df = df.rename(columns={'AF': 'AF_Initial'})
    print(df.shape)

    unique_gene_functions = df["Func.refGene"].unique()
    for gene_fun in unique_gene_functions:
        df2 = df[df['Func.refGene'] == str(gene_fun)]
        print(gene_fun)
        print(df2.shape)
        df2 = df2.reset_index()
        for index,row in df2.iterrows():  #Remember to reset index for df2 before this for loop
            try:
                temp = df2.iloc[index,145].split(";")#180
                for ech in temp:
                    temp1 = ech.split("=")
                    df2.loc[index,temp1[0]] = temp1[1]
                temp2 = df2.iloc[index,146].split(":")
                temp3 = df2.iloc[index,147].split(":")
                for loop in range(0,len(temp2)):
                    df2.loc[index,temp2[loop]] = temp3[loop]
            except IndexError:
                print("There is an error at index ",str(index))
                print(df2.iloc[index,145])#180
                print(df2.iloc[index,146])#181
                print(df2.iloc[index,147])
            file_name = f"{base_dir}/curation/{second_argv}_{gene_fun}.xlsx"
        df2.to_excel(file_name,index=False)
        print("Wrote ",gene_fun," successfully!!!")

#split_multiannov("/home/sahal/Downloads/T-MTX-DRV.hg19_multianno.txt","/home/sahal/Downloads/Result/T-MTX-DRV")
