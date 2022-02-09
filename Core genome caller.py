import os

os.system("cd YXpipeline")
path = os.path.abspath("YXpipeline")
print(path)

# Store the whole sites of reference genome into a list
wholesites = []
for i in range(1,4685849):      # The number here is the total length of reference sites plus 1
    wholesites.append(i.__str__())
print("The whole sites of reference genome are: ",len(wholesites))

# Creating a list with the unmapped sites per sample
unsnpsitsnumber = []
for sample_folder in os.listdir(path + "/samples"):
    print(sample_folder)
    sitespers = []
    sample_folderpath = path + "/samples/" + sample_folder.__str__()
    open_pilefile = open(sample_folderpath + "/mpileup.pileup", 'r')
    pileline = open_pilefile.readline()
    while (pileline):
        column = pileline.split("\t")
        sitespers.append(column[1])
        pileline = open_pilefile.readline()
    open_pilefile.close()
    #print("Last site",sitespers[-1])
    unun = list(set(wholesites) - set(sitespers))
    print("The length of unmapped sites (per sample) is: ",len(unun))

    # Store the unmapped sites per sample in .txt file
    sitefile = open(sample_folderpath + "/sitefile.txt", 'w')
    for i in unun:
        sitefile.write(i + "\n")
    open_pilefile.close()
    sitefile.close()

#Combine the unmapped sites per sample into single list
unmsites = []
for sample_folder in os.listdir(path + "/samples"):
    print(sample_folder)
    sample_folderpath = path + "/samples/" + sample_folder.__str__()
    sfile = open(sample_folderpath + "/sitefile.txt", 'r')
    sline = sfile.readline()
    while (sline):
        column = sline.split("\t")
        column[0] = column[0].replace("\n","")
        unmsites.append(column[0])
        sline = sfile.readline()
    sfile.close()
un = list(set(unmsites))
un.sort()
print(un[-1])
print("The length of all the unmapped sites is:")
print(len(un))

# Creat a list which contain all the sites low mapped read depths
print("Creating a list which contain all the low mapped sites")
rawsnpsitsnumber = []
for sample_folder in os.listdir(path + "/samples"):
    print(sample_folder)
    sample_folderpath = path + "/samples/" + sample_folder.__str__()
    #print(sample_folderpath)
    open_pilefile = open(sample_folderpath + "/mpileup.pileup", 'r')
    pileline = open_pilefile.readline()
    while (pileline):
        column = pileline.split("\t")
        if int(column[3]) < 5:       # The least read depths is 5
            rawsnpsitsnumber.append(column[1])
        pileline = open_pilefile.readline()
    open_pilefile.close()

Rrealsites = list(set(rawsnpsitsnumber))
Rrealsites.sort()
print("The length of all the low sites is:")
print(len(Rrealsites))

# Determine all the need_to_remove sites
remove_sites = Rrealsites + un
Rremove_sites = list(set(remove_sites))
Rremove_sites.sort()
print(remove_sites)
print(Rremove_sites[-1])
print("The total length of need_to_remove sites is:")
print(len(Rremove_sites))

# Determine the core genome sites
core_genome_sites = list(set(wholesites) - set(Rremove_sites))
core_genome_sites.sort()
print("The total length of core genome sites is:")
print(len(core_genome_sites))
print("Create a txt file with all the core genome sites")
core_file = path + "/output_files/core_genome_sites.txt"
ocore_file = open(core_file, "w")
for i in core_genome_sites:
    ocore_file.write(i + "\n")
ocore_file.close()
