"""Rework JSON files for storage and later diffing.

Take a collection of FamilySearch JSON files and rewrite them to snip
out redundant sections and place them in common files.  This creates
prettier diffs, where a single change to a child doesn't show up in the
git history of both parents.

"""
import argparse
import json
import sys
from pathlib import Path
from unittest import TestCase

test_case = TestCase()
test_case.maxDiff = None
assert_equal = test_case.assertEqual

def main(argv):
    parser = argparse.ArgumentParser(description='Rework JSON for archiving')
    parser.parse_args(argv)

    cachedir = Path('~/genealogy/cache').expanduser()
    people = {}
    children = {}

    for p in cachedir.iterdir():
        with p.open() as f:
            j = json.load(f)
        people[p.name] = j
        excise_children(j, children)

    outdir = Path('~/Plain/FamilySearch').expanduser()

    for key, j in people.items():
        outpath = outdir / key
        with open(outpath, 'w') as w:
            json.dump(j, w, indent=2)
            w.write('\n')

    for key, j in children.items():
        outpath = outdir / ('child-' + key)
        with open(outpath, 'w') as w:
            json.dump(j, w, indent=2)
            w.write('\n')

def excise_children(j, children):
    if isinstance(j, list):
        for item in j:
            excise_children(item, children)
    elif isinstance(j, dict):
        if sorted(j) == ['child', 'id', 'lineageConclusions']:
            del j['child']['principlePerson']  # field varies between records
            id = j['id']
            if id in children:
                assert_equal(children[id], j)
            else:
                children[id] = dict(j)  # copy before editing
            j['child'] = 'excised'
        for value in j.values():
            if isinstance(value, (dict, list)):
                excise_children(value, children)

if __name__ == '__main__':
    main(sys.argv[1:])
