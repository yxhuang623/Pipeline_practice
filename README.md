# Introduction

The YXPipeline was developed to accomplish reference-based alignments to create multi FASTA alignment of core genome SNPs (also called SNP “matrix” in this pipeline) for a given set of samples. This pipeline starts with the generation of VCF files which contain the high-quality SNPs for each sample. Then the “pseudo_sequence caller” will be conducted to determine all the core genome SNP positions and create a pseudo FASTA sequence using bases at core genome positions. After generating the SNP “matrix”, the multi FASTA alignment could be used to build the phylogenetic tree.

This pipeline focuses on the closely-related pathogens, which means that it’s not suitable for those distantly related organisms. This software was developed with the goal to help distinguish which pathogen genomes are more likely to be outbreak-associated and which are less likely to be associated. Such a tool may be useful for answer some certain evolutionary questions and trace food safety investigations.

The YXPipeline is completely written in Python. The code is designed to be easy to read and modified as necessary. The important parameters of used tools such as BWA and Varscan are able to be changed directly in the python script, depending on the input data sets.


# Before running the pipeline
## Operating System Requirements

The YXPipeline could run in a Linux environment, and it has been tested to work well on Ubuntu system.
## Executable Software Dependencies

The software used in this pipeline include BWA, SAMtools, GATK4, VarScan. Please make sure that your operating system has the following software installed before running the YXPipeline.

## Environment Variables

export CLASSPATH=~ /<varscan_version>/VarScan.jar:$CLASSPATH

export PATH="~/<gatk_version>/:$PATH"

# Notes to make sure the pipeline could work

## 1
Please download the python script named “YXpipeline” in Github and run the script directly in your command line.
## 2
This pipeline is able to download the raw reads, if you wanna use this function, please put a textfile(.txt) which contain all the SRRnumbers of your sample sets (one SRRnumber per line) in your current path where you will run the script.
## 3
Please create a new folder named "reference_file" in your current path and put your ref file in this folder. Then run the YXpipeline python script in the same path in your command line.


# High-quality SNPs

In this pipeline, high-quality SNPs are determined using the following criteria: Minimum variant allele frequency of 90%, Minimum base quality at a position to count a read of 15, Minimum read depth at a position to make a call of 8, variants with no more than 90% support on one strand. Only the high-quality SNPs will be used in the downstream analysis and the low-quality SNPs will be removed.


# Outputfiles

The mainly outputfiles include: multi FASTA alignment file, snp distance matrix file (.tls format), pseudo sequence of Reference (FASTA format, containing the bases at core genome postions), Phylip file (optional).
