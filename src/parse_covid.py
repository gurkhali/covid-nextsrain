import json 
import csv
import operator
import argparse
import datetime

# node value
def node_value(key, node):
        if key in node:
            return node[key]['value']
        else:
            return None

# class of sequence
class Sequence:
    def __init__(self, name, date, parent):
        self.name = name
        self.parent = parent
        self.dateRaw = date
        self.mutation = False
        self.country = None
        self.region = None
        self.div = 0
        
        # convert date 
        s = str(date).split('.')
        td = datetime.timedelta(days = 365 * float('0.' + s[1]))
        self.date = datetime.date(year=int(s[0]), month=1, day=1) + td
        self.epocTime = self.date.strftime("%s")

    def __str__(self):
        return("{0},{1},{2},{3},{4}".format(self.date, 
            self.parent, self.name, self.parent, self.mutation))

# add each of the nodes and children to a queue
def add_node(node, parent, flat_list):
        name = node['name']
        value = node_value('num_date', node['node_attrs'])
        seq = Sequence(name, value, parent)
        
        # mutation 
        if 'branch_attrs' in node:
            if 'mutations' in node['branch_attrs']:
                seq.mutation = len(node['branch_attrs']['mutations']) > 0

        # divergence
        if 'div' in node['node_attrs']:
            seq.divergence = node['node_attrs']['div']

        # region
        seq.region = node_value('region', node['node_attrs'])

        # country
        seq.country = node_value('country', node['node_attrs'])

        # originating_lab
        seq.country = node_value('originating_lab', node)

        # iterate children
        flat_list.append(seq)
        if 'children' in node:
            for c in node['children']:
                add_node(c, name, flat_list)

parser = argparse.ArgumentParser()
parser.add_argument('--file', nargs='?', default = "../data/sample.json",
                   help='covid input file name')
args = parser.parse_args()

flat_list = []
parent = "root"

with open(args.file) as json_file: 
    data = json.load(json_file) 


add_node(data['tree'], "root", flat_list)

flat_list.sort(key=lambda x: x.epocTime, reverse=False)
for f in flat_list:
    print (f)

