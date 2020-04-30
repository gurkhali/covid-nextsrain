import json
import csv
import operator
import argparse
import datetime

# class of sequence
class Sequence:
    def __init__(self, name, date, parent):
        self.name = name
        self.parent = parent
        self.dateRaw = date
        self.mutation = False

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
        value = node['node_attrs']['num_date']['value']
        seq = Sequence(name, value, parent)

        # set mutation value
        if 'branch_attrs' in node:
            if 'mutations' in node['branch_attrs']:
                seq.mutation = len(node['branch_attrs']['mutations']) > 0

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

flat_list.sort(key=lambda x: x.epocTime, reverse=False

