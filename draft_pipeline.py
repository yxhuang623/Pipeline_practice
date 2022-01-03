import os
import codecs

# Activate the environment of gatk4
os.system("conda activate gatk4")

# Download raw reads using sratoolkits
sranumber = open("/home/yixiao/SraAccList.txt")
sralist = list(sranumber)
#fsralist = list(x.strip() for x in sralist)
for SRRnumber in sralist:
    os.system("cd /home/yixiao/pipeline-practice/samples")
    command1 = "prefetch " + SRRnumber.__str__()
    os.system(command1)
    command2 = "cd /home/yixiao/pipeline-practice/samples/" + SRRnumber.__str__()
    os.system(command2)
    command3 = "fasterq-dump -S " + SRRnumber.__str__()
    os.system(command3)

# Path to the reference
referencepath = "/home/yixiao/pipeline-practice/reference/"
os.system("cd /home/yixiao/pipeline-practice")
# Create index file for reference
os.system("bwa index " + referencepath)

# Path to samples
os.system("cd /home/yixiao/pipeline-practice/samples")

# Alignment using BWA
i = 1
for sample_folder in os.listdir("/home/yixiao/pipeline-practice/samples"):
    fastqpath = []
    sampleDirectories = "/home/yixiao/pipeline-practice/output_files/sampleDirectories.txt"
    sample_folderpath = "/home/yixiao/pipeline-practice/samples/" + sample_folder.__str__()
    #sample_folder_pathlist.append(sample_folderpath)
    with open(sampleDirectories, 'w') as txtfile:
        txtfile.write(sample_folderpath + "\n")
    txtfile.close()

    if (sample_folder.startswith(".")):
        continue
    else:
        for file in os.listdir(sample_folderpath):
            if (file.startswith(".")):
                continue
            else:
                fastqpath.append(sample_folderpath + "/" + file.__str__())
        print(fastqpath)
        output_name = sample_folderpath + "/reads.sam"
        i += 1
        # Alignment
        command = "bwa mem /home/yixiao/pipeline-practice/reference/ " + \
              fastqpath[0] + " " + fastqpath[1] + " > " + output_name
        os.system(command)

# Call SNPs
for sample_folder in os.listdir("/home/yixiao/pipeline-practice/samples"):
    sample_folderpath = "/home/yixiao/pipeline-practice/samples/" + sample_folder.__str__()
    for samfile in os.listdir(sample_folderpath):
        if (samfile.endswith(".sam")):
            bam_name = "YX.unsortedreads.bam"

            # Convert sam to bam
            command = "samtools view -o " + bam_name + " " + samfile.__str__()
            os.system(command)

            # Sort bam
            sorted_name = "YX.sortedreads.bam"
            os.system("samtools sort " + bam_name + " -o " + sorted_name)

            # Remove duplicate reads
            dup_name = "YX.dedupreads.bam"
            Mdup_name = "marked_dup_metrics.txt"
            command = "picard MarkDuplicates I=" + sorted_name + " O=" + dup_name + " M=" + Mdup_name
            os.system(command)

            # Call variants by gatk Haplotypecaller
            vcf_file_name = "YX.raw.vcf"
            command = "gatk HaplotypeCaller -R " + referencepath + " -I " + dup_name + \
                      " --minimum-mapping-quality 30 -O " + vcf_file_name
            os.system(command)

            # Snp filter - gatk VariantFiltration - remove dense regions
            filter_vcf_output_name = "YX.filter.vcf"

            command = 'Gatk VariantFiltration -R  ' + referencepath + \
                      '-cluster 3 -window 10 -V ' \
                      + vcf_file_name + ' -O ' + filter_vcf_output_name
            os.system(command)

            # Remove dense regions - Extract VCF with only "PASS"
            PASS_vcf_output_name = "YX.PASS.vcf"
            reoutput_file = open(PASS_vcf_output_name, 'w')
            denfvcf_file = open(filter_vcf_output_name, 'r')
            line = denfvcf_file.readline()
            while (line):
                if (line[0] == "#"):
                    reoutput_file.write(line)
                elif (line[0] != "#"):
                    column = line.split("\t")
                    if column[6] != "PASS":
                        reoutput_file.write(line)

                line = reoutput_file.readline()
            reoutput_file.close()
            denfvcf_file.close()

            # Mark those failed-pass sites
            refilter_vcf_output_name = "YX.refilter.vcf"
            command = 'Gatk VariantFiltration -R ' + referencepath \
                      + '-V ' + PASS_vcf_output_name + ' -O ' + refilter_vcf_output_name \
                      + '--filter-name "MYfilter" --filter-expression "DP < 10 || AF < 0.75 || ADF < 2 || ADR < 2"'

            os.system(command)

            # Replace the bases in those failed-pass sites with "N"
            remarked_file = "YX.remarked.vcf"
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
          "/home/yixiao/pipeline-practice/output_files/sampleDirectories.txt"
os.system(command)

# Find the sites belong to the core genome in snplist.txt
filteredsnplist = "filteredsnplist.txt"
remarkedoutput_file = open("/home/yixiao/pipeline-practice/output_files/" + filteredsnplist, 'w')
snplistfile = open("/home/yixiao/pipeline-practice/output_files/snplist.txt", 'r')
listline = snplistfile.readline()

while(listline):
    token = listline.split("\t")
    if token[2] == "52":         #The number here is equal to the total number of samples
        remarkedoutput_file.write(listline)
    listline = snplistfile.readline()

remarkedoutput_file.close()
snplistfile.close()

# Create a [list] containing all the core-genome sites
fsnplistfile = codecs.open("/home/yixiao/pipeline-practice/output_files/snplist.txt", 'r')
snpsitsnumber = []
flistline = fsnplistfile.readline()
while flistline:
    token = flistline.split("\t")
    tokens = token[1]
    snpsitsnumber.append(tokens)
    flistline = fsnplistfile.readline()
fsnplistfile.close()

# Remove the non-core-genome sites in vcf file of each sample
for sample_folder in os.listdir("/home/yixiao/pipeline-practice/samples"):
    sample_folderpath = "/home/yixiao/pipeline-practice/samples/" + sample_folder.__str__()
    for files in os.listdir(sample_folderpath):
        if (files.endswith("remarked.vcf")):
            remarked_vcffile = open(files.__str__(), 'r')
            coresnp = sample_folderpath + "coresnp.vcf"
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
                    pseudo_seq_list.append(token[4])
                coresnpline = coresnp_file.readline()
            pseudo_seq_str = ''.join(pseudo_seq_list)
            # Write the title and pseudo_sequence into fasta file
            pse_output_name = sample_folderpath + "pseudoseq.fasta"
            pse_output_file = open(pse_output_name, "w")
            pse_output_file.write(">" + sample_folderpath[39:] + "\n")
            pse_output_file.write(pseudo_seq_str+ "\n")
            pse_output_file.close()

            # Change the title of pseudo-sequence for each sample
            fasta = open(pse_output_name, "r")
            newfa = sample_folderpath + "newpseudoseq.fasta"
            newfasta = open(newfa, "w")
            for line in fasta:
                if line.startswith(">"):
                    newfasta.write(sample_folderpath[39:] + "\n")
                else:
                    newfasta.write(line + "\n")
            fasta.close()
            newfasta.close()

# Create snp 'matrix' --combine files of consensus.fasta into single fasta file
for sample_folder in os.listdir("/home/yixiao/pipeline-practice/samples"):
    sample_folderpath = "/home/yixiao/pipeline-practice/samples/" + sample_folder.__str__()
    snpma_output_file = "/home/yixiao/pipeline-practice/output_files/snpmatrix.fasta"
    opsnpma_output_file = open(snpma_output_file, "w")
    pseq_list = []
    for pseq_file in os.listdir(sample_folderpath):
        if pseq_file.endswith("pseudoseq.fasta"):
            pseq_list.append(sample_folderpath + pseq_file)

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
    command = "snp-dists" + snpma_output_file + " > /home/yixiao/pipeline-practice/output_files/snpmatrix.tsv"
    os.system(command)

'''
        # Removing (marking) duplicates with GATK4
        dup_name = sorted_name[:-4] + ".dedup.bam"
        Mdup_name = sorted_name[:-4] + "marked_dup_metrics.txt"
        command = "gatk MarkDuplicatesSpark -I " + sorted_name + " -O " + dup_name + " -M " + Mdup_name
        os.system(command)        

        # Generate pileup file
        pileup_file_name = dup_name[:-4] + ".mpileup"
        command = "samtools mpileup -f " + referencepath + "" + sorted_name + " >" + pileup_file_name
        os.system(command)

        # Varscan
        vcf_file_name = pileup_file_name[:-4] + ".vcf"
        command = "varscan mpileup2snp" + pileup_file_name + ">" + vcf_file_name + "--min-var-freq 0.90 --output-vcf 1"
        os.system(command)

        # Filter indels within 5bp by bcftools
        filadjacent_file_name = vcf_file_name[:-4]+ ".fil.vcf"
        command = "bcftools filter --IndelGap 5 " + vcf_file_name + " -0b -o " + filadjacent_file_name
        os.system(command)
        
        # Filter parameters of DP, FREQ, ADF and ADR - MY own script
        parafiltered_vcf = PASS_vcf_output_name[:-4] + ".filtered.vcf"
        output_file = open("/home/yixiao/pipeline-practice/ " + parafiltered_vcf, 'w')
        vcf_file = open("/home/yixiao/pipeline-practice/" + PASS_vcf_output_name, 'r')
        line = vcf_file.readline()

        while (line):
            if (line[0] != "#"):
                token = line.split("\t")
                para_lst = token[9].split(":")
                if token[4] != "." and len(para_lst) == 14 and para_lst[0] == "1/1" and int(
                        para_lst[3]) >= 10 and float(para_lst[6][:-1]) >= 75 and int(
                    para_lst[12]) >= 2 and int(para_lst[13]) >= 2:
                    output_file.write(line)   
                                                                     
                else:
                    line = line.replace(column[6], 'failed_pass')
                    output_file.write(line)

            line = vcf_file.readline()

        output_file.close()
        vcf_file.close()
        
         # Remove dense regions - Extract VCF with only "PASS"
            PASS_vcf_output_name = "YX.PASS.vcf"
            command = "bcftools view -f PASS " + filter_vcf_output_name + " > " + PASS_vcf_output_name
            os.system(command)

        #Output a new vcf file from the input vcf file that removes any indel sites
        vcftools --vcf input_file.vcf --remove-indels --recode --recode-INFO-all --out SNPs_only
                    
        # Generate a single pseudo-sequence for each sample - gatk
        pse_output_name = sample_folderpath + "pseudoseq.fasta"
        command = "gatk FastaAlternateReferenceMaker -R " \
                    + referencepath + " -O " + pse_output_name + " -V " + coresnp
        os.system(command)
        
        # Mark those failed-pass sites
        refilter_vcf_output_name = "YX.refilter.vcf"
        command = 'Gatk VariantFiltration -R  ' + referencepath + '-V ' + PASS_vcf_output_name + \
                    '--filter-expression "DP < 10" --filter-name "DPffilter" ' \
                    '--filter-expression "AF < 0.75" --filter-name "AFffilter" ' \
                    '--filter-expression "ADF < 2 || ADR < 2" --filter-name "ADFRffilter"' \
                    + ' -O ' + refilter_vcf_output_name
        os.system(command)
'''
