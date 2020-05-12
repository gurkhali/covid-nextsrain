import json 
import csv
import operator
import argparse
import datetime
import pprint
import json

# constants
NUM_PARENTS = 10 #number of parents to track
OUT_FORMAT = ["epocTime", "gisaid", "name", "division", "country", "region", 
        "mutations", "divergence"]

# node value
def node_value(key, node):
        if key in node:
            return node[key]['value']
        else:
            return None

class Geo:
    def __init__(self, name, lo, la):
        self.name = name
        self.lo = lo
        self.la = la

# class of sequence
class Sequence:
    def __init__(self, name, date, parent, gisaid):
        self.name = name
        self.dateRaw = date
        self.country = None
        self.division = None
        self.originating_lab = None
        self.submitting_lab = None
        self.region = None
        self.divergence = 0
        self.date = 0
        self.epocTime = 0
        self.claude = None
        self.location = None
        self.gisaid = gisaid
        self.mutations = []
        self.generation = 1
        self.age = None
        self.sex = None
        self.node = None

        # set lineage
        self.parents = []
        self.childrens = []

        # set inherited info       
        if parent:
            self.parents = [parent] + parent.parents[:]
            self.generation = parent.generation + 1
 
        if date: 
            # convert date 
            s = str(date).split('.')
            td = datetime.timedelta(days = 365 * float('0.' + s[1]))
            self.date = datetime.date(year=int(s[0]), month=1, day=1) + td
            self.epocTime = self.date.strftime("%s") + "000000000"

    def __str__(self):
        #return str(self.__dict__)
        parents = str(self.get_parents_gisid(NUM_PARENTS))
        if self.parents and self.parents[0]:
            pn = self.parents[0].name
        else:
            pn = ""
        return("{0}, {1}, {2}, {3}, mutations {4}, div {5}, "\
                "generations {6} {7}".format(
            self.date, 
            pn, self.name, self.gisaid, 
            len(self.mutations), self.divergence, self.generation, parents))

    # return parents gisaid
    def get_parents_gisid(self, num):
        parents = [num]
        for i in range (0, min(num, len(self.parents))):
            if self.parents[i]:
                parents.append(self.parents[i].name)

        return parents

    # special handlers
    def to_list_mutations(self):
        if len(self.mutations):
            ret = 1
        else:
            ret = 0
        return ret

    # conver object to list type based on format
    def to_list(self, format=OUT_FORMAT):
        ret = []
        excludes = ['name', 'mutations', 'divergence']
        
        for f in format:
            try:
                # handle mutations differently
                if f == "mutations":
                    v = self.to_list_mutations()
                else:
                    v = getattr(self, f)         
                    if f not in excludes and v:
                        v = v.replace(' ', '-')
                # strip spa

            except AttributeError:
                ret.append(None)
            else:
                ret.append(v)
        return ret
            

def add_geo(location, values, ret):
    for l in values :
        if l['key'] != location:
            continue
    if l:
        for (k, v) in l['demes'].items():
            ret.update({k: Geo(k, v['longitude'], v['latitude'])})
    return ret

def get_mutations(node):
    if 'branch_attrs' in node and 'mutations' in node['branch_attrs'] and len(
            node['branch_attrs']['mutations']):
        return node['branch_attrs']['mutations']
    else:
        return None
       
def add_branch_node(node, parent, flat_list, mutations):
    children = []

    # append mutations if present
    m = get_mutations(node)
    if m:
        mutations.append(m)

    # cant have empty children
    if not 'children' in node:
        raise NameError("### Empty Children")

    for c in node['children']:
        childs = add_node(c, parent, flat_list)
        for c in childs:
            if len(mutations) > 0: 
                c.mutations.append(mutations)
            children.append(c)

    return children

def has_leafs(node):
    if 'children' in node:
        for c in node['children']:
            if (node_value('gisaid_epi_isl',  c['node_attrs'])):
                return True

    return False

# add each of the nodes and children to a queue
def add_node(node, parent, flat_list):
    name = node['name']
    value = node_value('num_date', node['node_attrs'])
    gisaid = node_value('gisaid_epi_isl', node['node_attrs'])

    # 
    # Check if its a branch node; skip the branches
    # 
    if not gisaid and not has_leafs(node):
        return add_branch_node(node, parent, flat_list, [])

    # sequence object
    seq = Sequence(name, value, parent, gisaid)
    
    # mutations 
    m = get_mutations(node)
    if m:
        seq.mutations.append(m)

    # divergence
    if 'div' in node['node_attrs']:
        seq.divergence = node['node_attrs']['div']

    # node 
    seq.node = node

    # age
    seq.age =  node_value('age', node['node_attrs'])

    # sex
    seq.sex = node_value('sex', node['node_attrs'])

    # claude
    seq.claude = node_value('claude_membership', node['node_attrs'])

    # region
    seq.region = node_value('region', node['node_attrs'])

    # location
    seq.location = node_value('location', node['node_attrs'])

    # country
    seq.country = node_value('country', node['node_attrs'])

    # division
    seq.division = node_value('division', node['node_attrs'])

    # originating_lab
    seq.originating_lab = node_value('originating_lab', node['node_attrs'])

    # submittinh lab
    seq.submitting_lab = node_value('submitting_lab', node['node_attrs'])

    # iterate children
    flat_list.append(seq)
  
    if 'children' in node:
        for c in node['children']:
            nodes = add_node(c, seq, flat_list)
            for n in nodes:
                seq.childrens.append(n)

    return [seq]

def write_csv(out_file, headers, output):
    f = open(out_file, 'w')
    writer = csv.writer(f, delimiter=',', doublequote=True,
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    
    writer.writerow(headers)
    for o in output:
        # skip if not a sample
        if not o.gisaid:
            continue
        output = o.to_list()
        writer.writerow(output)

# build timeline
def parse_json(file_name, flat_list, region_geo, country_geo):
    print (file_name)
    # root node
    root = Sequence("root", None, None, None)

    with open(file_name) as json_file: 
        data = json.load(json_file) 

    # add region geo
    add_geo('region', data['meta']['geo_resolutions'], 
            region_geo)
    # add country geo
    add_geo('country', data['meta']['geo_resolutions'], 
            country_geo)

    # genome nodem
    add_node(data['tree'], root, flat_list)

# define a main function
def main(args):
    flat_list = []
    region_geo = {}
    country_geo = {}


    # parse the json file
    parse_json(args.file, flat_list, region_geo, country_geo)

    # write out data
    write_csv(args.outfile, OUT_FORMAT, flat_list)


# # # # # # # # # # # # 
parser = argparse.ArgumentParser()
parser.add_argument('--file', nargs='?', 
        default = "/home/ubuntu/covid/data/covid.json",
        help='covid input file name')
parser.add_argument('--outfile', nargs='?', 
        default = "/home/ubuntu/covid/output/data.csv",
        help='covid output file name')
args = parser.parse_args()

# call main function
main(args)
