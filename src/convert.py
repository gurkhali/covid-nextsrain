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
         + "value=1,"
         + "name=\"" + str(df["name"][d]) + "\","

         + "mutations=" + str(df["mutations"][d])
         + " " + str(df["epocTime"][d]) for d in range(len(df))]

for item in infections:
    thefile.write("%s\n" % item)

strains = [ "strains,"
         + "first_strain=" + str(df["first_strain"][d]) + ","
         + "key=s"
         + " "
         + "strain=\"" + str(df["strain"][d]) + "\","
         + "gisaid=\"" + str(df["gisaid"][d]) + "\","
         + "country=\"" + str(df["country"][d]) + "\","
         + "division=\"" + str(df["division"][d]) + "\","
         + "divergence=" + str(df["divergence"][d]) + ","
         + "region=\"" + str(df["region"][d]) + "\","
         + "strainname=\"" + str(df["strainname"][d]) + "\","
         + "name=\"" + str(df["name"][d]) + "\","

         + "mutations=" + str(df["mutations"][d])
         + " " + str(df["epocTime"][d]) for d in range(len(df))]

for item in strains:
    thefile.write("%s\n" % item)
