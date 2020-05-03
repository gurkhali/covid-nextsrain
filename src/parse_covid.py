import json 
import csv
import operator
import argparse
import datetime
import pprint
import json

# constants
NUM_PARENTS = 10 #number of parents to track


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
    def __init__(self, name, date, parent):
        self.name = name
        self.dateRaw = date
        self.mutations = False
        self.country = None
        self.originating_lab = None
        self.submitting_lab = None
        self.region = None
        self.mutations_protein = False
        self.mutations_rna = False
        self.div = 0
        self.generartion = 1
        self.date = 0
        self.epocTime = 0
        self.generation = 0
        self.claude = None
        self.location = None
        self.gisaid = None

        # set lineage
        self.parents = [NUM_PARENTS]
        self.childrens = []
        
        # generation info       
        if parent:
            self.generation = parent.generation + 1
            self.parents = [parent] + parent.parents
        else:
            self.parents = [parent]
 
        if date: 
            # convert date 
            s = str(date).split('.')
            td = datetime.timedelta(days = 365 * float('0.' + s[1]))
            self.date = datetime.date(year=int(s[0]), month=1, day=1) + td
            self.epocTime = self.date.strftime("%s")

    def __str__(self):
        #return str(self.__dict__)
        return("{0},{1},{2},{3},{4}".format(self.date, 
            self.parents[0].name, self.name, self.mutations, self.generation))

def add_geo(location, values):
    ret = {}
    for l in values :
        if l['key'] != location:
            continue
    if l:
        for (k, v) in l['demes'].items():
            ret.update({k: Geo(k, v['longitude'], v['latitude'])})
    return ret

# add each of the nodes and children to a queue
def add_node(node, parent, flat_list):
        name = node['name']
        value = node_value('num_date', node['node_attrs'])
        seq = Sequence(name, value, parent)
        
        # mutations 
        if 'branch_attrs' in node:
            if 'mutations' in node['branch_attrs']:
                seq.mutations = len(node['branch_attrs']['mutations'])
                if seq.mutations > 0:
                    # amino mutations
                    if 'nuc' in node['branch_attrs']['mutations']:
                        seq.mutations_protein = True
                    
                    # rna mutations
                    if seq.mutations > 1 or (not seq.mutations_protein):
                        seq.mutations_rna = True

        seq.gisaid = node_value('num_date', node['node_attrs'])

        # divergence
        if 'div' in node['node_attrs']:
            seq.divergence = node['node_attrs']['div']

        # claude
        seq.claude = node_value('claude_membership', node['node_attrs'])

        # region
        seq.region = node_value('region', node['node_attrs'])

        # location
        seq.location = node_value('location', node['node_attrs'])

        # country
        seq.country = node_value('country', node['node_attrs'])

        # originating_lab
        seq.originating_lab = node_value('originating_lab', node['node_attrs'])

        # submittinh lab
        seq.submitting_lab = node_value('submitting_lab', node['node_attrs'])

        # iterate children
        flat_list.append(seq)
        if 'children' in node:
            for c in node['children']:
                seq.childrens.append(add_node(c, seq, flat_list))

        return seq

parser = argparse.ArgumentParser()
parser.add_argument('--file', nargs='?', default = "../data/sample.json",
                   help='covid input file name')
args = parser.parse_args()

flat_list = []
region_geo = {}
country_gep = {}


# root node
root = Sequence("root", None, None)

with open(args.file) as json_file: 
    data = json.load(json_file) 

# add geo
region_geo = add_geo('region', data['meta']['geo_resolutions'])
country_geo = add_geo('country', data['meta']['geo_resolutions'])

# genome nodes
add_node(data['tree'], root, flat_list)

flat_list.sort(key=lambda x: x.epocTime, reverse=False)
for f in flat_list:
    #pprint.PrettyPrinter(indent=1, depth=1).pprint(f)
    print (f)

