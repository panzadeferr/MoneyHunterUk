#!/usr/bin/env python3
"""Banned-claims check (Albertino, 13 Oct 2026).

Hard-fails on app.html and index.html. Data files (playbook + questions) are
Albertino's reviewed teaching content: they quote scam phrases such as
"guaranteed 20% a month" to teach what fraud sounds like, so "guaranteed" is
reported there as a warning, everything else hard-fails. Allowed wording:
"can earn", "up to GBP", "free cash", and condition statements like
"must earn GBP5,000/month".
"""
import re, sys, glob

GBP = '\u00a3'
HARD = [
    (r'(?i)most\s+users\s+earn', 'typical-result claim'),
    (r'(?i)first\s+' + GBP + r'200\s+is', 'speed/amount promise'),
    (r'(?i)guaranteed', 'guarantee claim'),
    (r'(?i)risk[-\s]?free', 'risk-free claim'),
    (r'(?i)always\s+yours', 'unconditional safety claim'),
    (r'(?i)(?<!up to )(?<!can )(?<!must )earn\s+' + GBP, 'bare "earn GBP" without up to / can / must'),
]
SOFT_IN_DATA = {'guarantee claim'}

def hits(path, patterns):
    src = open(path, encoding='utf-8').read()
    out = []
    for pat, label in patterns:
        for m in re.finditer(pat, src):
            ctx = src[max(0, m.start() - 45):m.end() + 45].replace('\n', ' ')
            out.append((path, label, ctx))
    return out

def main():
    fails, warns = [], []
    for f in ('app.html', 'index.html'):
        fails += hits(f, HARD)
    for f in sorted(glob.glob('data/*.json') + glob.glob('data/questions/*.json')):
        for p, l, c in hits(f, HARD):
            (warns if l in SOFT_IN_DATA else fails).append((p, l, c))
    for p, l, c in warns:
        print('WARN (reviewed anti-scam teaching, allowed): %s: %s: ...%s...' % (p, l, c))
    if fails:
        print('BANNED CLAIMS FOUND:')
        for p, l, c in fails:
            print('  %s: %s: ...%s...' % (p, l, c))
        sys.exit(1)
    print('OK: no banned claims')

if __name__ == '__main__':
    main()
