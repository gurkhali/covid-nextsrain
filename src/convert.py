import pandas as pd
df = pd.read_csv("../output/data.csv")
lines = [ "strains"
         + ",country=" + str(df["country"][d]) + ","
         + "division=" + str(df["division"][d]) + ","
         + "region=" + str(df["region"][d]) + ""
         + " "
         + "gisaid=\"" + str(df["gisaid"][d]) + "\","
         + "strain=\"" + str(df["strain"][d]) + "\","
         + "divergence=" + str(df["divergence"][d]) + ","
         + "name=\"" + str(df["name"][d]) + "\","
         + "mutations=" + str(df["mutations"][d])
         + " " + str(df["epocTime"][d]) for d in range(len(df))]
thefile = open('../output/chronograf.txt', 'w')
for item in lines:
    thefile.write("%s\n" % item)
