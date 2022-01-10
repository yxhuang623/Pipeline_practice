# Introduction

The YXPipeline was developed to accomplish reference-based alignments to create multi FASTA alignment of core genome SNPs (also called SNP “matrix” in this pipeline) for a given set of samples. This pipeline starts with the generation of VCF files which contain the high-quality SNPs for each sample. Then the “pseudo_sequence caller” will be conducted to determine all the core genome SNP positions and create a pseudo FASTA sequence using bases at core genome positions. After generating the SNP “matrix”, the multi FASTA alignment could be used to build the phylogenetic tree.

This pipeline focuses on the closely-related pathogens, which means that it’s not suitable for those distantly related organisms. This software was developed with the goal to help distinguish which pathogen genomes are more likely to be outbreak-associated and which are less likely to be associated. Such a tool may be useful for answer some certain evolutionary questions and trace food safety investigations.

The YXPipeline is completely written in Python. The code is designed to be easy to read and modified as necessary. The important parameters of used tools such as BWA and Varscan are able to be changed directly in the python script, depending on the input data sets.


# Before running the pipeline

1.Operating System Requirements

The YXPipeline could run in a Linux environment, and it has been tested to work well on Ubuntu system.

2.Executable Software Dependencies

The software used in this pipeline include BWA, SAMtools, GATK4, VarScan. Please make sure that your operating system has the following software installed before running the YXPipeline.

3.Environment Variables

export CLASSPATH=~ /<varscan_version>/VarScan.jar:$CLASSPATH

export PATH="~/<gatk_version>/:$PATH"

4.Notes to make sure the pipeline could work

Please download the python script named “YXpipeline” in Github and run the script directly in your command line.
Please create a new folder named "reference_file" in your current path and put your ref file in this folder. Then run the YXpipeline python script in the same path.

