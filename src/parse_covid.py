import json 
import csv
import operator
import argparse
import datetime
import pprint
import json

# branch id generator
unique_id = 0

# constants
NUM_PARENTS = 10 #number of parents to track
OUT_FORMAT = ["epocTime", "gisaid", "name", "division", "country", "region", 
        "mutations", "divergence"]

def get_next_id(prefix):
    global unique_id
    unique_id = unique_id + 1

    return ("{0}_{1}".format(prefix, str(unique_id)))

def get_mutations(node):
    if 'branch_attrs' in node and 'mutations' in node['branch_attrs'] and len(
            node['branch_attrs']['mutations']):
        return node['branch_attrs']['mutations']
    else:
        return None

def get_dates(date):
    # convert date 
    s = str(date).split('.')
    td = datetime.timedelta(days = 365 * float('0.' + s[1]))
    date = datetime.date(year=int(s[0]), month=1, day=1) + td
    epocTime = date.strftime("%s") + "000000000"

    return date, epocTime

# node value
def node_value(key, node):
        if key in node:
            return node[key]['value']
        else:
            return None

def is_leaf(node):
    if (node_value('gisaid_epi_isl', node['node_attrs'])):
        return True
    return False

def has_leaf_mutation(node):
    if 'children' in node:
        for n in node['children']:
            if is_leaf(n) and get_mutations(n):
                return True
    return False

class Geo:
    def __init__(self, name, lo, la):
        self.name = name
        self.lo = lo
        self.la = la

class Branch:
    def __init__(self, node, parent):

        self.generation = 1
        
        self.sequences = []
        self.mutations = []
        self.date = None

        if node:
            self.name = node['name']
        else:
            self.name = "root"

         # set lineage
        self.parent = parent
        self.branches = []
        self.node = node

        # unique id
        self.id = get_next_id("BR")

        # date
        if node:
            self.date, self.epocTime = get_dates(node_value('num_date', 
            node['node_attrs']))

    def add_sequence(self, node):
        name = node['name']
        date = node_value('num_date', node['node_attrs'])
        gisaid = node_value('gisaid_epi_isl', node['node_attrs'])

        if not gisaid:
            raise NameError("### Invalid Sequence")

        # sequence object
        seq = Sequence(name, date, self, gisaid)
        
        # transfer and add mutations 
        seq.mutations = self.mutations[:]
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

        # set branch name
        seq.branch = self

        self.sequences.append(seq)

        return seq

    def __str__(self):
        if self.date:
            date = self.date
        else:
            date = ""

        ret = "{0}, {1}, {2}, {3}".format(
            date, self.parent, self.name, len(self.sequences))
        
        for s in self.sequences:
            ret = ret + "\t{1}\n".format(str(s))

        for b in self.branches:
            ret = ret + "\t{1}\n".format(b.name)

        return (ret)

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
        self.age = None
        self.sex = None
        self.node = None
        self.branch = None

        if not date:
            raise NameError("### Empty date for sequences")
        
        self.date, self.epocTime = get_dates(date)

    def __str__(self):
        return("{0}, {1}, {2}, {3}, {4}, div {5}, "\
                "generations {6} {7}".format(
            self.date, self.parent, self.name, self.gisaid, self.division))

    def get_siblings(self):
        ret = []
        sequences = self.branch.sequences
        for s in sequences:
            ret.append(s.name)
        return ret

    def get_parents(self):
        ret = []
        parent = self.branch
        while parent:
            ret.append(parent.id)
            parent = parent.parent
        return ret

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
       
def add_branch_node(node, parent, flat_list):
    leaf_nodes = []
    branch_nodes = []

    # create branch if there are mutations
    branch_mutation = get_mutations(node)
    if branch_mutation:
        branch = Branch(node, parent)
        parent.branches.append(branch)
        
        # store mutation
        branch.mutations.append(branch_mutation)
    else:
        # map to the parent branch
        branch = parent

    # build sequences to walk
    for n in node['children']:
        if is_leaf(n):
            leaf_nodes.append(n)
        else:
            branch_nodes.append(n)

    # add sequences
    for n in leaf_nodes:
        # if leaf is a mutation we need to add a solo branch
        if get_mutations(n):
            mutated_leaf = Branch(node, branch)
            branch.branches.append(mutated_leaf)
            flat_list.append(mutated_leaf.add_sequence(n))
        else:
            flat_list.append(branch.add_sequence(n))

    # walk non leaf branches
    for n in branch_nodes:
        add_branch_node(n, branch, flat_list)
    return

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
    root = Branch(None, None)

    with open(file_name) as json_file:      
        data = json.load(json_file) 

    # add region geo
    add_geo('region', data['meta']['geo_resolutions'], 
            region_geo)
    # add country geo
    add_geo('country', data['meta']['geo_resolutions'], 
            country_geo)

    # genome nodem
    add_branch_node(data['tree'], root, flat_list)
     
    return root


# define a main function
def main(args):
    flat_list = []
    region_geo = {}
    country_geo = {}

    # parse the json file
    root = parse_json(args.file, flat_list, region_geo, country_geo)

    # write out data
    write_csv(args.outfile, OUT_FORMAT, flat_list)

    count = 10
    for i in flat_list:
        parents = i.get_parents()
        siblings = i.get_siblings()
        print("{0}: \n    {1}, \n    {2}".format(i.gisaid, 
            str(parents), str(siblings)))

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
