import os

# filter window size: 3 in 1000bp
os.system("cd YXpipeline")
path = os.path.abspath("YXpipeline")
print(path)

output_name = path + "/snpvar.vcf"
filtered_vcf = path + "/redense_snpvar.vcf"
output_file = open(filtered_vcf, 'w')
vcf_file = open(output_name, 'r')

# skip comments
line = vcf_file.readline()
while line:
    if line[0] == "#":
        output_file.write(line)
        line = vcf_file.readline()
    else:
        break

line1 = line
line2 = vcf_file.readline()
line3 = vcf_file.readline()
line4 = vcf_file.readline()
line5 = vcf_file.readline()
line6 = vcf_file.readline()
line7 = vcf_file.readline()

if line1 != "" and line2 != "" and line3 != "" and line4 != "" and line5 != "" and line6 != "" and line7 != "":
    p1 = int(line1.split("\t")[1])
    p2 = int(line2.split("\t")[1])
    p3 = int(line3.split("\t")[1])
    p4 = int(line4.split("\t")[1])
    p5 = int(line5.split("\t")[1])
    p6 = int(line6.split("\t")[1])
    p7 = int(line7.split("\t")[1])
    token = line1.split("\t")

    # check for 1st element
    if p4 - p1 < 1000:
        for i in range(0, 6):
            output_file.write(token[i])
            output_file.write("\t")

        output_file.write("ClusterSNP")
        output_file.write("\t")
        for i in range(7, 10):
            output_file.write(token[i])
            if i != 9:
                output_file.write("\t")
    else:
        output_file.write(line1)

    # check for 2nd element
    token = line2.split("\t")
    if p5 - p2 < 1000 or p4 - p1 < 1000:
        for i in range(0, 6):
            output_file.write(token[i])
            output_file.write("\t")

        output_file.write("ClusterSNP")
        output_file.write("\t")
        for i in range(7, 10):
            output_file.write(token[i])
            if i != 9:
                output_file.write("\t")
    else:
        output_file.write(line2)

    # check for 3rd element
    token = line3.split("\t")
    if p6 - p3 < 1000 or p5 - p2 < 1000 or p4 - p1 < 1000:
        for i in range(0, 6):
            output_file.write(token[i])
            output_file.write("\t")

        output_file.write("ClusterSNP")
        output_file.write("\t")
        for i in range(7, 10):
            output_file.write(token[i])
            if i != 9:
                output_file.write("\t")
    else:
        output_file.write(line3)

    while line7:
        p1 = int(line1.split("\t")[1])
        p2 = int(line2.split("\t")[1])
        p3 = int(line3.split("\t")[1])
        p4 = int(line4.split("\t")[1])
        p5 = int(line5.split("\t")[1])
        p6 = int(line6.split("\t")[1])
        p7 = int(line7.split("\t")[1])

        token = line4.split("\t")

        if p4 - p1 < 1000 or p5 - p2 < 1000 or p6 - p3 < 1000 or p7 - p4 < 1000:
            for i in range(0, 6):
                output_file.write(token[i])
                output_file.write("\t")

            output_file.write("ClusterSNP")
            output_file.write("\t")
            for i in range(7, 10):
                output_file.write(token[i])
                if i != 9:
                    output_file.write("\t")

        else:
            output_file.write(line4)

        line1 = line2
        line2 = line3
        line3 = line4
        line4 = line5
        line5 = line6
        line6 = line7
        line7 = vcf_file.readline()

    # check for 3rd last element
    token = line4.split("\t")
    if p5 - p2 < 1000 or p6 - p3 < 1000 or p7 - p4 < 1000:
        for i in range(0, 6):
            output_file.write(token[i])
            output_file.write("\t")

        output_file.write("ClusterSNP")
        output_file.write("\t")
        for i in range(7, 10):
            output_file.write(token[i])
            if i != 9:
                output_file.write("\t")
    else:
        output_file.write(line4)

    # check for 2nd last element
    token = line5.split("\t")
    if p6 - p3 < 1000 or p7 - p4 < 1000:
        for i in range(0, 6):
            output_file.write(token[i])
            output_file.write("\t")

        output_file.write("ClusterSNP")
        output_file.write("\t")
        for i in range(7, 10):
            output_file.write(token[i])
            if i != 9:
                output_file.write("\t")
    else:
        output_file.write(line5)

    # check for the last element
    token = line6.split("\t")
    if p7 - p4 < 1000:
        for i in range(0, 6):
            output_file.write(token[i])
            output_file.write("\t")

        output_file.write("ClusterSNP")
        output_file.write("\t")
        for i in range(7, 10):
            output_file.write(token[i])
            if i != 9:
                output_file.write("\t")
    else:
        output_file.write(line6)

else:
    if line1 == "":
        print("")
    elif line2 == "":
        output_file.write(line1)
    elif line3 == "":
        output_file.write(line1)
        output_file.write(line2)
    elif line4 == "":
        p1 = int(line1.split("\t")[1])
        p2 = int(line2.split("\t")[1])
        p3 = int(line3.split("\t")[1])
        if p3 - p1 > 1000:
            output_file.write(line1)
            output_file.write(line2)
            output_file.write(line3)
    else:
        p1 = int(line1.split("\t")[1])
        p2 = int(line2.split("\t")[1])
        p3 = int(line3.split("\t")[1])
        p4 = int(line4.split("\t")[1])
        if p3 - p1 > 1000:
            output_file.write(line1)
        if p4 - p2 > 1000:
            output_file.write(line2)
            output_file.write(line3)
            output_file.write(line4)

vcf_file.close()
output_file.close()
