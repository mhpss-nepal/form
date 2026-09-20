import json, re, os, collections
os.chdir('/root/mhpss-nepal-work/form-translation')
held = json.load(open('tools/i18n-ne-authority-held.json'))
hdr = json.load(open('tools/i18n-ne-human-decision-required.json'))
DEV = re.compile(r'[\u0900-\u097F]+')
TAG = re.compile(r'<[^>]+>')

def toks(v): return DEV.findall(TAG.sub(' ', v))

FAMILIES = {
    'referral (रेफरल/रेफर vs प्रेषण)': {'रेफरल','रेफर','प्रेषण'},
    'follow-up (फलोअप vs अनुगमन)': {'फलोअप','अनुगमन'},
    'score (स्कोर vs अङ्क)': {'स्कोर','अङ्क'},
    'site (स्थान vs स्थल)': {'स्थान','स्थल'},
    'stated (खुलाइएको/जनाइएको vs भनिएको)': {'खुलाइएको','जनाइएको','भनिएको'},
    'administration (सञ्चालन vs मापन)': {'सञ्चालन','मापन'},
    'in-one (कतै insertions)': set(),
}

def diffs(key):
    a, b = toks(hdr[key]['lane-A']), toks(hdr[key]['lane-B'])
    ca, cb = collections.Counter(a), collections.Counter(b)
    onlyA = set(t for t in a if ca[t] > cb.get(t,0))
    onlyB = set(t for t in b if cb[t] > ca.get(t,0))
    return onlyA, onlyB

blockers = collections.Counter()
exclusive = []
for k in held:
    oa, ob = diffs(k)
    touched = set()
    for name, fam in FAMILIES.items():
        if fam and ((oa | ob) & fam):
            touched.add(name)
    for name in touched:
        blockers[name] += 1
    if touched == {'referral (रेफरल/रेफर vs प्रेषण)'}:
        exclusive.append(k)

print("held keys:", len(held))
print()
print("held keys whose difference touches each family:")
for name, n in blockers.most_common():
    print("   %-40s %d" % (name, n))
print()
print("held ONLY by the referral term (one human decision unlocks all of these): %d" % len(exclusive))
for k in sorted(exclusive):
    print("   %-12s %s" % (k, hdr[k]['english'][:80]))
