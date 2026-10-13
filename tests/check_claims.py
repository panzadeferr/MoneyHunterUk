#!/usr/bin/env python3
"""Banned-claims check (Albertino, 13 Oct 2026).

Hard-fails on app.html and index.html. Data files (playbook + questions) are
Albertino's reviewed teaching content: they quote scam phrases such as
"guaranteed 20% a month" to teach what fraud sounds like, so "guaranteed" is
reported there as a warning, everything else hard-fails. Allowed wording:
"can earn", "up to GBP", "free cash", and condition statements like
"must earn GBP5,000/month". Extended 13 Oct 2026 (Albertino): also bans
"available to earn", "get paid", "no experience needed", and unqualified
"save GBP X/year" figures (allowed only with "some people" or "up to" on the
same line); those four are warnings in reviewed data files.
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
    (r'(?i)available\s+to\s+earn', '"available to earn" claim'),
    (r'(?i)get\s+paid', '"get paid" promise'),
    (r'(?i)no\s+experience\s+needed', '"no experience needed" claim'),
    (r'(?i)claim\s+an\s+offer', 'reward for claiming an offer'),
    (r'(?i)complete\s+an\s+offer', 'reward for completing an offer'),
    (r'(?i)earn\s+xp', 'XP reward wording'),
    (r'(?i)never\s+miss\s+a\s+' + GBP, 'absolute marketing line'),
    (r'(?i)unlock[^.\n]{0,60}offer|offer[^.\n]{0,60}unlock', 'unlock tied to offers'),
]
# labels that are only warnings inside Albertino's reviewed data files
SOFT_IN_DATA = {'guarantee claim', '"available to earn" claim', '"get paid" promise',
                '"no experience needed" claim', 'unqualified annual saving figure',
                'reward for claiming an offer', 'reward for completing an offer',
                'XP reward wording', 'absolute marketing line', 'unlock tied to offers'}

def save_rule_hits(path):
    """Unqualified 'save GBP X ... year' figures; allowed only with
    'some people' or 'up to' on the same line (Albertino, 13 Oct 2026)."""
    out = []
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            if (re.search(r'(?i)save\s+' + GBP + r'\s*[\d,]', line)
                    and re.search(r'(?i)\byear\b', line)
                    and not re.search(r'(?i)some people|up to', line)):
                out.append((path, 'unqualified annual saving figure', line.strip()[:110]))
    return out

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
        fails += hits(f, HARD) + save_rule_hits(f)
    for f in sorted(glob.glob('data/*.json') + glob.glob('data/questions/*.json')):
        found = hits(f, HARD) + save_rule_hits(f)
        for p, l, c in found:
            (warns if l in SOFT_IN_DATA else fails).append((p, l, c))
    for p, l, c in warns:
        print('WARN (reviewed data, allowed): %s: %s: ...%s...' % (p, l, c))
    if fails:
        print('BANNED CLAIMS FOUND:')
        for p, l, c in fails:
            print('  %s: %s: ...%s...' % (p, l, c))
        sys.exit(1)
    print('OK: no banned claims')

if __name__ == '__main__':
    main()
