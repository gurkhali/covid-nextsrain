import pandas as pd
df = pd.read_csv("../output/data.csv")
lines = [ "strains"
         + ",type=BTC"
         + " "
         + "gisaid=\"" + str(df["gisaid"][d]) + "\","
         + "name=\"" + str(df["name"][d]) + "\","
         + "division=\"" + str(df["division"][d]) + "\","
         + "country=\"" + str(df["country"][d]) + "\","
         + "region=\"" + str(df["region"][d]) + "\","
         + "mutations=" + str(df["mutations"][d])
         + " " + str(df["epocTime"][d]) for d in range(len(df))]
thefile = open('../output/chronograf.txt', 'w')
for item in lines:
    thefile.write("%s\n" % item)
