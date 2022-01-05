import os
import codecs

# Download raw reads using sratoolkits
sranumber = open("/home/yixiao/fullSraAccList.txt")
sralist = list(sranumber)
# Obtain the total number of samples for further usage
totalsample_numbers = len(sralist)
print(totalsample_numbers)

for SRRnumber in sralist:
    SRRnumber = SRRnumber[0:10]
    os.system("cd /home/yixiao/pipeline-practice/samples")
    command1 = "prefetch " + SRRnumber + " -O /home/yixiao/pipeline-practice/samples"
    os.system(command1)
    command3 = "fasterq-dump -S " + SRRnumber + " -O /home/yixiao/pipeline-practice/samples/" + SRRnumber
    os.system(command3)
    
# Path to the reference
referencepath = "/home/yixiao/pipeline-practice/reference/P125109.fasta"
# Create index file for reference
os.system("bwa index " + referencepath)

# Alignment using BWA
# i = 1
sampleDirectories = "/home/yixiao/pipeline-practice/output_files/sampleDirectories.txt"
SD_file = open(sampleDirectories, 'w')
for sample_folder in os.listdir("/home/yixiao/pipeline-practice/test_samples"):
    print(sample_folder)
    fastqpath = []
    sample_folderpath = "/home/yixiao/pipeline-practice/test_samples/" + sample_folder.__str__()
    print(sample_folderpath)
    #sample_folder_pathlist.append(sample_folderpath)
    SD_file.write(sample_folderpath + "\n")

    if (sample_folder.startswith(".")):
        continue
    else:
        for file in os.listdir(sample_folderpath):
            if (file.endswith(".fastq")):
                fastqpath.append(sample_folderpath + "/" + file.__str__())
        print(fastqpath)
        output_name = sample_folderpath + "/reads.sam"

        # Alignment
        command = "bwa mem /home/yixiao/pipeline-practice/reference/P125109.fasta " + \
              fastqpath[0] + " " + fastqpath[1] + " > " + output_name
        os.system(command)

SD_file.close()

# Call SNPs
# Creating the fasta index file
os.system("samtools faidx " + referencepath)
# Creating the FASTA sequence dictionary file
os.system("gatk CreateSequenceDictionary -R " + referencepath)

for sample_folder in os.listdir("/home/yixiao/pipeline-practice/test_samples"):
    sample_folderpath = "/home/yixiao/pipeline-practice/test_samples/" + sample_folder
    bam_name = sample_folderpath + "/YX.unsortedreads.bam"
    command = "samtools view -o " + bam_name + " " + sample_folderpath + "/reads.sam"
    os.system(command)

    # Sort bam
    sorted_name = sample_folderpath + "/YX.sortedreads.bam"
    os.system("samtools sort " + bam_name + " -o " + sorted_name)

    # Add @RG to BAM file
    sorted_name = sample_folderpath + "/YX.sortedreads.bam"
    RGsorted_name = sample_folderpath + "/RGsortedreads.bam"
    command = "gatk AddOrReplaceReadGroups I=" + sorted_name + " O=" + RGsorted_name + \
              " RGID=4 RGLB=lib1 RGPL=ILLUMINA RGPU=unit1 RGSM=20"
    os.system(command)

    # Samtools index
    os.system("samtools index " + RGsorted_name)
    # Generate raw vcf files
    vcf_file_name = sample_folderpath + "/YX.raw.vcf"
    command = "gatk HaplotypeCaller -R " + referencepath + " -I " + RGsorted_name + \
              " --minimum-mapping-quality 30 -O " + vcf_file_name
    os.system(command)

    # Snp filter - gatk VariantFiltration - remove dense regions
    filter_vcf_output_name = sample_folderpath + "/YX.filter.vcf"

    command = 'gatk VariantFiltration -R  ' + referencepath + \
              ' -cluster 3 -window 10 -V ' \
              + vcf_file_name + ' -O ' + filter_vcf_output_name
    os.system(command)

    # Remove dense regions - Extract VCF with only "PASS"
    PASS_vcf_output_name = sample_folderpath + "/YX.PASS.vcf"
    reoutput_file = open(PASS_vcf_output_name, 'w')
    denfvcf_file = open(filter_vcf_output_name, 'r')
    line = denfvcf_file.readline()
    while (line):
        if (line[0] == "#"):
            reoutput_file.write(line)
        elif (line[0] != "#"):
            column = line.split("\t")
            if column[6] == "PASS":
                reoutput_file.write(line)

        line = denfvcf_file.readline()
    reoutput_file.close()
    denfvcf_file.close()

    # Mark those failed-pass sites
    refilter_vcf_output_name = sample_folderpath + "/YX.refilter.vcf"
    command = 'gatk VariantFiltration -R ' + referencepath \
              + ' -V ' + PASS_vcf_output_name + ' -O ' + refilter_vcf_output_name \
              + ' --filter-name "MYfilter" --filter-expression "DP < 10 || AF < 0.75 || ADF < 2 || ADR < 2"'

    os.system(command)

    # Replace the bases in those failed-pass sites with "N"
    remarked_file = sample_folderpath + "/YX.remarked.vcf"
    remarkedoutput_file = open(remarked_file, 'w')
    markedvcf_file = open(refilter_vcf_output_name, 'r')
    line = markedvcf_file.readline()
    while (line):
        if (line[0] == "#"):
            remarkedoutput_file.write(line)
        elif (line[0] != "#"):
            column = line.split("\t")
            if column[6] != "PASS":
                line = line.replace(column[4], 'N')
                remarkedoutput_file.write(line)
            else:
                remarkedoutput_file.write(line)
        line = markedvcf_file.readline()

    remarkedoutput_file.close()
    markedvcf_file.close()

# Create a single merged snplist.txt file with all remarked-VCFs
command = "cfsan_snp_pipeline merge_sites -n YX.remarked.vcf -o " \
          "/home/yixiao/pipeline-practice/output_files/snplist.txt " \
          "/home/yixiao/pipeline-practice/output_files/sampleDirectories.txt " \
          "/home/yixiao/pipeline-practice/output_files/filteredsampleDirectories.txt"
os.system(command)

# Find the sites belong to the core genome in snplist.txt
filteredsnplist = "filteredsnplist.txt"
remarkedoutput_file = open("/home/yixiao/pipeline-practice/output_files/" + filteredsnplist, 'w')
snplistfile = open("/home/yixiao/pipeline-practice/output_files/snplist.txt", 'r')
listline = snplistfile.readline()

while(listline):
    token = listline.split("\t")
    if token[2] == "3":         #The number here is equal to the total number of samples
        remarkedoutput_file.write(listline)
    listline = snplistfile.readline()

remarkedoutput_file.close()
snplistfile.close()

# Create a [list] containing all the core-genome sites
fsnplistfile = codecs.open("/home/yixiao/pipeline-practice/output_files/filteredsnplist.txt", 'r')
snpsitsnumber = []
flistline = fsnplistfile.readline()
while flistline:
    token = flistline.split("\t")
    tokens = token[1]
    snpsitsnumber.append(tokens)
    flistline = fsnplistfile.readline()
fsnplistfile.close()

# Remove the non-core-genome sites in vcf file of each sample
for sample_folder in os.listdir("/home/yixiao/pipeline-practice/test_samples"):
    sample_folderpath = "/home/yixiao/pipeline-practice/test_samples/" + sample_folder
    for files in os.listdir(sample_folderpath):
        if (files.endswith(".remarked.vcf")):
            remarked_vcffile = open(sample_folderpath + "/YX.remarked.vcf", 'r')
            coresnp = sample_folderpath + "/coresnp.vcf"
            coresnp_vcf = open(coresnp, "w")
            flistline = remarked_vcffile.readline()
            while (flistline):
                if (flistline[0] == "#"):
                    coresnp_vcf.write(flistline)
                elif (flistline[0] != "#"):
                    token = flistline.split("\t")
                    if token[1] in snpsitsnumber:
                        coresnp_vcf.write(flistline)
                flistline = remarked_vcffile.readline()
            coresnp_vcf.close()
            remarked_vcffile.close()

            # Generate a single pseudo-sequence for each sample- my own script
            coresnp_file = open(coresnp, "r")
            coresnpline = coresnp_file.readline()
            pseudo_seq_list = []
            while coresnpline:
                if (coresnpline[0] != "#"):
                    token = coresnpline.split("\t")
                    pseudo_seq_list.append(token[4][-1:])
                coresnpline = coresnp_file.readline()
            pseudo_seq_str = ''.join(pseudo_seq_list)

            # Write the title and pseudo_sequence into fasta file
            pse_output_name = sample_folderpath + "/pseudoseq.fasta"
            pse_output_file = open(pse_output_name, "w")
            pse_output_file.write(">" + sample_folderpath[44:] + "\n")
            pse_output_file.write(pseudo_seq_str+ "\n")
            pse_output_file.close()

# Create snp 'matrix' --combine files of consensus.fasta into single fasta file
pseq_list = []
for sample_folder in os.listdir("/home/yixiao/pipeline-practice/test_samples"):
    sample_folderpath = "/home/yixiao/pipeline-practice/test_samples/" + sample_folder
    print(sample_folderpath)
    snpma_output_file = "/home/yixiao/pipeline-practice/output_files/snpmatrix.fasta"
    opsnpma_output_file = open(snpma_output_file, "w")

    pseq_list.append(sample_folderpath + "/pseudoseq.fasta")
    print(pseq_list)

    for pseq_file_path in pseq_list:
        input_file = open(pseq_file_path, "r")
        line = input_file.readline()
        while (line):
            if line.startswith(">"):
                opsnpma_output_file.writelines(line)
            else:
                opsnpma_output_file.writelines(line)
            line = input_file.readline()

    opsnpma_output_file.close()

    # Create snp distance matrix by snp-dists
    command = "snp-dists /home/yixiao/pipeline-practice/output_files/snpmatrix.fasta > " \
              "/home/yixiao/pipeline-practice/output_files/snpmatrix.tsv"
    os.system(command)
    
