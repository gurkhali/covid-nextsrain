import pandas as pd
import datetime
from csv import DictReader

file_name_countries = '../data/countries.csv'
file_name_infections = '../data/infections.csv'
file_name_deaths = '../data/deaths.csv'
file_name_apple = '../data/apple_mobility.csv'
file_name_strains = '../output/data.csv'

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
            # add mapping with and without dashes
            d[country] = continent
            d[country.replace(' ', '-')] = continent
    return d

def write_hopkins_data(measurement, file_name_input, 
        file_name_countries,  out_file):
    co = build_continent(file_name_countries)

    infections = []

    df = pd.read_csv(file_name_input)
    for v in df.values:
        # see if division is set
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

            out_file.write(measurement + "," +
                    "country="+ c + ","
                    "division="+ d + ","
                    "region=" + cn + ""
                    " " +
                    "positives={0} {1}\n".format(value, dt))

def apple_mobility_tags(fields, continent):
    geo_type = fields[0]
    transport = fields[2]
    name = str(fields[1]).replace(' ', '-').replace('.', '')
    country = str(fields[5]).replace(' ', '-').replace('.', '')
    state = str(fields[4]).replace(' ', '-').replace('.', '')

    if geo_type == "country/region":
        ret = "division={0},country={0},region={1}".format(name,
                continent[name].replace(' ', '-'))
    elif geo_type == "city":
        ret = "city={0},division={1},country={2},region={3}".format(name, state, country,
                continent[country].replace(' ', '-'))
    elif geo_type == "sub-region":
        ret = "division={0},country={1},region={2}".format(name, country,
                continent[country].replace(' ', '-'))
    elif geo_type == "county":
        ret = "county={0},division={1},country={2},region={3}".format(name, state, country,
                continent[country].replace(' ', '-'))
    else:
        print("######## - unknown type")
    return "type={0},geo_type={1},{2}".format(transport, geo_type, ret)

def write_apple_data(measurement, file_name_input, 
        file_name_countries,  out_file):
    co = build_continent(file_name_countries)

    infections = []

    df = pd.read_csv(file_name_input)
    for v in df.values:
        fields_string = apple_mobility_tags(v, co) 
        #print(fields_string)

        for i in range(7, len(v)):
            # skip if invalid
            if str(v[i]) == "nan":
                continue

            dt = datetime.datetime.strptime(df.columns[i],
                    '%Y-%m-%d').strftime("%s") + "000000000"

            out_file.write("mobility,{0} activity={1} {2}\n".format(fields_string,
                v[i], dt))

def write_strains(file_name, out_file):
    df = pd.read_csv(file_name)
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


out_file = open('../output/chronograf.txt', 'w')

#write_strains(file_name_strains, out_file)

#write_hopkins_data("infections", file_name_infections, 
#        file_name_countries,  out_file)
#write_hopkins_data("deaths", file_name_deaths, 
#        file_name_countries,  out_file)
write_apple_data("moility", file_name_apple, 
        file_name_countries,  out_file)
