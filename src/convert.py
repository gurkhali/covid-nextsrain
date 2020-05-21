import pandas as pd
import datetime
from csv import DictReader

file_name_countries = '../data/countries.csv'
file_name_infections = '../data/infections.csv'

out_file = open('../output/chronograf.txt', 'w')
df = pd.read_csv("../output/data.csv")
#infections = [ "infections"
#         + ",country=" + str(df["country"][d]) + ","
#         + "division=" + str(df["division"][d]) + ","
#         + "region=" + str(df["region"][d]) + ""
#        + " "
#         + "gisaid=\"" + str(df["gisaid"][d]) + "\","
#         + "strain=\"" + str(df["strain"][d]) + "\","
#         + "strainname=\"" + str(df["strainname"][d]) + "\","
#         + "divergence=" + str(df["divergence"][d]) + ","
#         + "first_strain=" + str(df["first_strain"][d]) + ","
#         + "strain_division=\"" + str(df["strain_division"][d]) + "\","
#         + "branch_id=\"" + str(df["branch_id"][d]) + "\","
#         + "branch_ids=\"" + str(df["branch_ids"][d]) + "\","
#         + "value=1,"
#         + "name=\"" + str(df["name"][d]) + "\","
#
#         + "mutations=\"" + str(df["mutations"][d]) + "\""
#         + " " + str(df["epocTime"][d]) for d in range(len(df))]

#for item in infections:
#    out_file.write("%s\n" % item)

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
    out_file.write("%s\n" % item)

country_rename = {
        'Congo (Brazzaville)' : 'Democratic Republic of the Congo',
        'Congo (Kinshasa)' : 'Democratic Republic of the Congo',
        'Korea, South': 'South Korea',
        'Czechia': 'Czech Repblic',
        'Taiwan*': 'Taiwan',
        'Cabo Verde': 'Cape Verde',
        'Kyrgyz': 'Kyrgyzstan',
        'Burma': 'Myanmar',
}

def build_continent(file_name):
    d = {}
    with open(file_name) as csv:
        reader = DictReader(csv)

        for row in reader:
            country = row['Country_Name'].split(',')[0]
            if country == "Korea":
                country = country + ", South"
            continent = row ['Continent_Name']
            d[country] = continent
    return d

def write_infections(file_name_infections, file_name_countries,  out_file):
    co = build_continent(file_name_countries)

    infections = []

    df = pd.read_csv(file_name_infections)
    for v in df.values:
        if str(v[0]) != "nan":
            d = v[0]
        else:
            d = v[1]
        c = v[1]
        cn = co[c]

        if (c in country_rename) :
            c = country_rename[c]

        d = d.replace(' ', '-')
        d = d.replace(',', '-')
        c = c.replace(' ', '-')
        cn = cn.replace(' ', '-')

        last_value = 0
        for i in range(4, len(v)):
            if v[i] >= last_value:
                value = v[i] - last_value
                last_value = v[i]
            else:
                value = 0
            dt = datetime.datetime.strptime(df.columns[i],
                    '%m/%d/%y').strftime("%s") + "000000000"

            out_file.write("infections," +
                    "country="+ c + ","
                    "division="+ d + ","
                    "region=" + cn + ""
                    " " +
                    "positives={0} {1}\n".format(value, dt))

write_infections(file_name_infections, file_name_countries,  out_file)
