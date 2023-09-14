library(Rsamtools)
library(readxl)
library(openxlsx)
library(dplyr)
library(tidyr)
library(optparse)
option_list <- list(
  make_option(c("--coverage"), type = "character", default = NULL, help = "COVERAGE_PATH"),
  make_option(c("--bam"), type = "character", default = NULL, help = "BAM_PATH"),
  make_option(c("--result"), type = "character", default = NULL, help = "RESULT_PATH")
)

# Parse command-line arguments
opt_parser <- OptionParser(usage = "Usage: %prog --coverage <COVERAGE_PATH> --bam <BAM_PATH> --result <RESULT_PATH>", option_list = option_list)
opt <- parse_args(opt_parser)
coverage_data <- opt$coverage
bam <- opt$bam
final_result_table <- opt$result
coverage_data <- read_excel(coverage_data)
param <- ScanBamParam(which=GRanges(coverage_data$Chromosome,
IRanges(start=coverage_data$Positions, end=coverage_data$Positions)))
p_param <- PileupParam(max_depth=10000, distinguish_strand=FALSE)
pileup<-pileup(bam, scanBamParam=param,pileupParam=p_param)
print("Completed Covearge from bam")
print("Started taking coverage for alt allele")

#Creating coverage for alternate alleles

table1_split <- coverage_data %>%
     separate_rows(Alt, sep = ",")
result <- table1_split %>%
     left_join(pileup, by = c("Chromosome" = "seqnames", "Positions" = "pos", "Alt" = "nucleotide")) %>%
     select( -which_label) 
     
result_summary <- result %>%
     group_by(RSIDS, Chromosome, Positions, Ref, Alt) %>%
     summarize(Count = paste(count, collapse = ","))
result_summary$Count[result_summary$Count == "NA"] <- 0
merged_data <- result_summary %>%
     group_by(RSIDS, Chromosome, Positions, Ref) %>%
     summarize(
         MergedAlt = paste0(unique(Alt), collapse = ","),
         MergedCount = paste0(Count, collapse = ",")
     )
colnames(merged_data)[colnames(merged_data) == "MergedCount"] <- "Alt_Count"
colnames(merged_data)[colnames(merged_data) == "MergedAlt"] <- "Alt"
print("completed alt coverage")
print("started taking coverage for ref allele")
#Creating Coverages Ref Alleles

coverage_data$CountRef<-NA
updated_coverage_data <- coverage_data %>%
left_join(pileup, by = c("Chromosome" = "seqnames", "Positions" = "pos", "Ref" = "nucleotide")) %>%
mutate(CountRef = ifelse(!is.na(count), count, CountRef)) %>%
select(-count)
print("completed ref coverage")
Final_Result <- merge(merged_data, updated_coverage_data, by = c("RSIDS","Chromosome","Positions","Ref","Alt"), suffixes = c("_merged_data", "_updated_coverage_data"))
Final_Result <- Final_Result[c("Gene","RSIDS","Chromosome","Positions","Ref","Alt","Clinical_significance","Validation_status","Function_class","Frequency","HGVS","CountRef","Alt_Count")]
Final_Result$CountRef[is.na(Final_Result$CountRef)] <- 0
Genotype <- Final_Result %>%
  separate_rows(Alt, Alt_Count, sep = ',') %>%
  mutate(Alt_Count = as.numeric(Alt_Count))
Genotype$CountRef <- ifelse(Genotype$CountRef == 0, "", Genotype$CountRef)
Genotype$Alt_Count <- ifelse(Genotype$Alt_Count == 0, "", Genotype$Alt_Count)

Genotype$Alt_Count <- as.numeric(Genotype$Alt_Count)
Genotype$CountRef <- as.numeric(Genotype$CountRef)
Genotype$GT <- ifelse(is.na(Genotype$CountRef) & is.na(Genotype$Alt_Count), "no reads in bam",
ifelse(is.na(Genotype$Alt_Count), paste(Genotype$Ref, "/", Genotype$Ref, sep = ""),
ifelse(is.na(Genotype$CountRef), paste(Genotype$Alt, "/", Genotype$Alt, sep = ""),
ifelse(Genotype$Alt_Count / (Genotype$Alt_Count + Genotype$CountRef) > 0.2,
paste(Genotype$Ref, "/", Genotype$Alt, sep = ""),
paste(Genotype$Ref, "/", Genotype$Ref, sep = "")
)
)
)
)
Genotype <- Genotype %>%
     group_by(RSIDS) %>%
     summarize(GT = unique(GT)) %>%
     arrange(row_number())

Genotype <- Genotype %>%
     group_by(RSIDS) %>%
     # Remove rows with GT value "no reads in bam" if there are duplicates
     mutate(GT = ifelse(n() > 1 & GT == "no reads in bam", NA, GT)) %>%
     ungroup()
Genotype <- Genotype %>%
     filter(!is.na(GT))

Genotype <- Genotype %>%
     group_by(RSIDS) %>%
     # Remove rows with GT value "no reads in bam" if there are duplicates
     mutate(GT = ifelse(n() > 1 & GT %in% c("A/A", "G/G", "C/C", "T/T"), NA, GT)) %>%
     ungroup()
Genotype <- Genotype %>%
     filter(!is.na(GT))
Final_Result <- Final_Result %>%
  left_join(Genotype, by = "RSIDS")
write.xlsx(Final_Result,final_result_table,rowNames =FALSE)#Change output path
print("Analysis completed")
