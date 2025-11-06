#!/usr/bin/env python3
import sys

import requests

base = 'http://127.0.0.1:5000'

def fetch(name, lang):
    r = requests.get(f'{base}/api/problem/{name}', params={'language': lang})
    r.raise_for_status()
    return r.json()


def main():
    problems = ['summation','palindrome','two_sum']
    langs = ['python','javascript','java','cpp']
    ok = True
    for prob in problems:
        hints = {}
        for l in langs:
            j = fetch(prob, l)
            h = j.get('hints', {})
            hints[l] = (h.get('pseudocode',''), tuple(h.get('bullets',[])))
        # Check that at least two languages differ
        uniq = set(hints.values())
        print(f'{prob} -> unique hint variants: {len(uniq)}')
        if len(uniq) < 2:
            print('  WARNING: hints appear identical across languages for', prob)
            ok = False
    if not ok:
        sys.exit(2)
    print('Hints appear language-aware for core problems')

if __name__=='__main__':
    main()
    main()
