#!/usr/bin/env python

from __future__ import print_function

import argparse
import json
import sys
from pprint import pprint

def main(argv):
    # parser = argparse.ArgumentParser(description=put description here)
    # parser.add_argument('integers', metavar='N', type=int, nargs='+',
    #                     help='an integer for the accumulator')
    # parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                     const=sum, default=max,
    #                     help='sum the integers (default: find the max)')
    # args = parser.parse_args(argv)
    # print(args.accumulate(args.integers))

    # import urllib.request as r
    twr = 'G33C-HXS'
    process(twr, 0, set())

def process(id, depth, already):
    if depth > 20:
        return
    r = get_record(id)
    name = r['name']
    birthplace = get(r, 'birth', 'details', 'place', 'normalizedText')
    print(' ' * depth, name, birthplace)
    for key in 'parent1', 'parent2':
        id = get(r, 'parents', 0, key, 'id')
        if not id:
            continue
        if id in already:
            continue
        already.add(id)
        process(id, depth + 1, already)

def get(value, *keys):
    for key in keys:
        try:
            value = value[key]
        except LookupError:
            return None
        if (value is None) or (value == 'UNKNOWN'):
            return None
    return value

def get_record(person):
    path = 'cache/' + person
    import os
    if os.path.exists(path):
        with open(path) as f:
            data = f.read()
        return json.loads(data)

    print('Fetching', person)

    import requests
    import browsercookie
    cj = browsercookie.chrome()

    for cookie in cj:
        if cookie.expires == 0:
            cookie.expires = None
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

    url = 'https://www.familysearch.org/service/tree/tree-data/v8/person/{}/details?locale=en'.format(person)
    r = requests.get(url, cookies=cj)

    data = r.content
    with open(path, 'wb') as c:
        c.write(data)

    return json.loads(data)
    return

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
