import pandas as pd

thefile = open('../output/chronograf.txt', 'w')
df = pd.read_csv("../output/data.csv")
infections = [ "infections"
         + ",country=" + str(df["country"][d]) + ","
         + "division=" + str(df["division"][d]) + ","
         + "region=" + str(df["region"][d]) + ""
         + " "
         + "gisaid=\"" + str(df["gisaid"][d]) + "\","
         + "strain=\"" + str(df["strain"][d]) + "\","
         + "strainname=\"" + str(df["strainname"][d]) + "\","
         + "divergence=" + str(df["divergence"][d]) + ","
         + "first_strain=" + str(df["first_strain"][d]) + ","
         + "strain_division=\"" + str(df["strain_division"][d]) + "\","
         + "branch_id=\"" + str(df["branch_id"][d]) + "\","
         + "branch_ids=\"" + str(df["branch_ids"][d]) + "\","
         + "value=1,"
         + "name=\"" + str(df["name"][d]) + "\","

         + "mutations=\"" + str(df["mutations"][d]) + "\""
         + " " + str(df["epocTime"][d]) for d in range(len(df))]

for item in infections:
    thefile.write("%s\n" % item)

strains = [ "strains,"
         + "country=" + str(df["country"][d]) + ","
         + "division=" + str(df["division"][d]) + ","
         + "first_strain=" + str(df["first_strain"][d]) + ","
         + "region=" + str(df["region"][d]) + ""
         + " "
         + "gisaid=\"" + str(df["gisaid"][d]) + "\","
         + "strain=\"" + str(df["strain"][d]) + "\","
         + "strainname=\"" + str(df["strainname"][d]) + "\","
         + "divergence=" + str(df["divergence"][d]) + ","
         + "strain_division=\"" + str(df["strain_division"][d]) + "\","
         + "branch_id=\"" + str(df["branch_id"][d]) + "\","
         + "branch_ids=\"" + str(df["branch_ids"][d]) + "\","
         + "value=1,"
         + "name=\"" + str(df["name"][d]) + "\","

         + "mutations=\"" + str(df["mutations"][d]) + "\""
         + " " + str(df["epocTime"][d]) for d in range(len(df))]

for item in strains:
    thefile.write("%s\n" % item)
