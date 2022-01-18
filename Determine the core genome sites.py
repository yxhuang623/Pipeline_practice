import os

os.system("cd YXpipeline")
path = os.path.abspath("YXpipeline")
print(path)

# Creat a list which contain all the sites
print("Creat a list which contain all the sites")
rawsnpsitsnumber = []
for sample_folder in os.listdir(path + "/samples"):
    print(sample_folder)
    fastqpath = []
    sample_folderpath = path + "/samples/" + sample_folder.__str__()
    print(sample_folderpath)
    open_vcffile = open(sample_folderpath + "/var.vcf", 'r')
    vcfline = open_vcffile.readline()
    while (vcfline):
        if (vcfline[0] != "#"):
            column = vcfline.split("\t")
            rawsnpsitsnumber.append(column[1])
        vcfline = open_vcffile.readline()
    open_vcffile.close()

rawsnpsitsnumber.sort()
print(rawsnpsitsnumber)
print(len(rawsnpsitsnumber))

realsites =[]
for i in rawsnpsitsnumber:
    if int(rawsnpsitsnumber.count(i)) == 52:
        realsites.append(i)
Rrealsites = list(set(realsites))
print(Rrealsites)
print("The length of core genome sites will be:")
print(len(Rrealsites))
Rrealsites.sort()

for sample_folder in os.listdir(path + "/samples"):
    print(sample_folder)
    willaddsites = []
    snponlysite = []
    sample_folderpath = path + "/samples/" + sample_folder.__str__()

    # Find the REF and ALT bases at SNP sites
    varvcf = open(sample_folderpath + "/var.vcf", 'r')
    newvarvcf = open(sample_folderpath + "/coregenome_sites.vcf", 'w')
    vline = varvcf.readline()
    while (vline):
        if (vline[0] != "#"):
            column = vline.split("\t")
            if column[1] in Rrealsites:
                newvarvcf.write(vline)
        vline = varvcf.readline()
    varvcf.close()
    newvarvcf.close()
