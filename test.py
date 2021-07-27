#!/usr/bin/env python

from __future__ import print_function

import argparse
import json
import os
import requests
import sys
from pathlib import Path
from pprint import pprint
from time import sleep

def main(argv):
    parser = argparse.ArgumentParser(description='Backup family tree')
    parser.add_argument('-d', dest='depth', default=0, type=int,
                        help='depth')
    parser.add_argument('-f', dest='force', action='store_true',
                        help='force reload rather than using cache')
    parser.add_argument('person_id', help='Person ID to start with')
    args = parser.parse_args(argv)

    client = Client(args.force)
    client.max_depth = args.depth

    process(client, args.person_id, set(), 0)

def process(client, id, already, depth):
    if depth > client.max_depth:
        return
    person = get_person(client, id)
    r = person['details']
    #pprint(r)
    lifespan = r['lifespan'].replace('Deceased', '?')
    name = r['name']
    birthplace = get(r, 'birth', 'details', 'place', 'normalizedText')
    if birthplace:
        birthplace = ', '.join(birthplace.split(', ')[-2:])
    else:
        birthplace = '-'
    u = ' -?-' if unsure(person) else ''
    line = '{} {}{} {} ({}) '.format(' ' * depth, id, u, name, lifespan)
    width = 78 - len(line)
    line = f'{line} {birthplace:>{width}}'
    print(line)
    if unsure(person):
        return
    for key in 'parent1', 'parent2':
        id = get(r, 'parents', 0, key, 'id')
        if not id:
            continue
        if id in already:
            continue
        already.add(id)
        process(client, id, already, depth + 1)

def get(value, *keys):
    for key in keys:
        try:
            value = value[key]
        except LookupError:
            return None
        if (value is None) or (value == 'UNKNOWN'):
            return None
    return value

def get_person(client, person_id):
    #path = 'cache/' + person

    cachedir = Path('/home/brandon/Plain/FamilySearch')
    path = cachedir / person_id

    if (not client.force) and os.path.exists(path):
        with open(path) as f:
            data = f.read()
        return json.loads(data)

    print('Fetching', person_id)
    sleep(0.5)

            # cookie.discard = True  # instead of False
            # cookie._rest = {'HttpOnly': None}  # instead of {}
            # if cookie.name == 'fssessionid':
            #     print(cookie)
            #     print(cookie.__dict__)

    # print(type(cj))
    #return

    # print(dir(cj))
    # help(cj.extract_cookies)
    # return
    # opener = r.build_opener(r.HTTPCookieProcessor(cj))

    # print('@' * 20)
    # for cookie in cj:
    #     # print(cookie.__dict__)
    #     # break
    #     if cookie.domain == 'www.familysearch.org':
    #         if cookie.name == 'fssessionid':
    #             print(cookie)
    #             print(cookie.__dict__)

    # return

    # TODO: use this URL to determine who Im following
    # Where does sessionID come from
    # Change names in cache to make clear; all in one JSON? or several
    # files per person? maybe one file per person.

    # url = 'https://www.familysearch.org/service/tree/tree-data/watch/G3YS-1F4?sessionId=086e6c70-6b39-41ad-8d29-f3a4fc035c2e-prod'
    # r = requests.get(url, cookies=cj)
    # print(repr(r.content))
    # print(repr(r.status_code))  # 204 if not following! 200 otherwise.
    # exit()

    # url = 'https://www.familysearch.org/service/tree/tree-data/v8/person/G3YS-1F4/summary?locale=en'
    # url = 'https://www.familysearch.org/service/tree/tree-data/family-members/person/G3YS-1F4?includePhotos=true'
    # url = 'https://edge.fscdn.org/assets/components/fs-icons/dist/svg/watch-on-small-f1f41a449a73451f917e73b17b445fac.svg'

    data = {}

    url = 'https://www.familysearch.org/service/tree/tree-data/v8/person/{}/details?locale=en'.format(person_id)
    r = client.get(url)

    #print(repr(r.content))
    data['details'] = json.loads(r.content)

    url = (
        'https://www.familysearch.org/service/tree/tree-data/watch/{}'
        '?sessionId={}'.format(person_id, client.session_id)
    )
    r = client.get(url)

    data['watch'] = (r.status_code == 200)

    with open(path, 'w') as c:
        json.dump(data, c, indent=2)
        #c.write(data)

    return data

class Client:
    def __init__(self, force):
        self.cj = None
        self.force = force  # not used by class; probably belongs elsewhere?

    def load_cookies(self):
        import browsercookie
        self.cj = cj = browsercookie.chrome()
        for cookie in cj:
            if cookie.expires == 0:
                cookie.expires = None
            if cookie.domain == '.familysearch.org':
                if cookie.name == 'fssessionid':
                    self.session_id = cookie.value

    def get(self, url):
        if self.cj is None:
            self.load_cookies()
        return requests.get(url, cookies=self.cj)

def unsure(person):
    return (not person['details']['living']) and (not person['watch'])

def scrap():
    r = requests.Request('GET', url, cookies=cj)
    p = r.prepare()
    cookie_text = p.headers['Cookie']
    # for k, v in p.headers.items():
    #     print(k)
    #     print(v)
    # print(dir(p))#cookies)
    # print(len(p._cookies))


    rawdata = cookie_text

    d = parse_cookie_text(rawdata)
    from pprint import pprint
    with open('library', 'w') as f:
        for k, v in sorted(d.items()):
            print(k, v, file=f)

    d = parse_cookie_text(rawdata)
    from pprint import pprint
    with open('browser', 'w') as f:
        for k, v in sorted(d.items()):
            print(k, v, file=f)

def parse_cookie_text(s):
    from http.cookies import SimpleCookie
    cookie = SimpleCookie()
    cookie.load(s)
    return {key: morsel.value for key, morsel in cookie.items()}

if __name__ == '__main__':
    main(sys.argv[1:])
