import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from collections import OrderedDict

parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-d","--dry-run",default=False,action="store_true",help="put reordered bibitems into temp file")
parser.add_argument("-q","--quiet",default=False,action="store_true",help="don't print anything")
parser.add_argument("--debug",default=False,action="store_true",help="print debugging messages")
parser.add_argument("bibfile",type=str,help="file containing bibitems")
parser.add_argument("texfile",type=str,help="top-level .tex file")
args = parser.parse_args()

# 1. make list of bibitems
refs = OrderedDict()
before = []
after = []
started = False
with open(args.bibfile,'r') as biblio:
    for line in biblio:
        linesplit = line.split()
        if linesplit[0].startswith(r'\bibitem'):
            started = True
            key = linesplit[0].replace(r'\bibitem{','').replace('}','')
            refs[key] = line
        else:
            if started:
                after.append(line)
            else:
                before.append(line)

# 2. check tex file(s), recursing through \input{} entries, to get refs used in order
def find_refs(fname):
    input_token = r'\input{'
    cite_token = r'\cite{'
    used = []
    def get_cite(line):
        cites = []
        if cite_token in line:
            start = line.find(cite_token)
            subline = line[start+len(cite_token):]
            end = subline.find('}')
            cites = subline[:end].split(',')
            subline = subline[end:]
            # recursive call in case multiple \cite in one line
            cites2 = get_cite(subline)
            cites.extend(cites2)
        return cites
    with open(fname,'r') as file:
        for line in file:
            if line.startswith(input_token):
                fname2 = line.replace(input_token,'').replace('}','').rstrip()+".tex"
                if args.debug: print(fname2)
                # todo: check for infinite loops
                # recursive call
                used2 = find_refs(fname2)
                if args.debug: print(used2)
                used.extend(used2)
            else:
                cites = get_cite(line)
                used.extend(cites)
    # uniquify while preserving order: https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-whilst-preserving-order
    used_set = set()
    used_set_add = used_set.add
    used = [ref for ref in used if not (ref in used_set or used_set_add(ref))]
    return used
used = find_refs(args.texfile)

# 3. make new bibfile w/ refs in correct order
new_bibfile = "new_"+args.bibfile
unknown = []
with open(new_bibfile,'w') as biblio:
    for line in before:
        biblio.write(line)
    for ref in used:
        if ref not in refs:
            unknown.append(ref)
        else:
            biblio.write(refs[ref])
    for line in after:
        biblio.write(line)
if not args.dry_run:
    # easier than mv with overwrite
    os.remove(args.bibfile)
    os.rename(new_bibfile,args.bibfile)

# 4. show unused and unknown refs
used_set = set(used)
unused = [ref for ref in refs if ref not in used_set]
if not args.quiet:
    if len(unused)>0: print("Unused references: {}".format(', '.join(unused)))
    if len(unknown)>0: print("Unknown references: {}".format(', '.join(unknown)))
