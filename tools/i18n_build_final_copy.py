import json, re, os
os.chdir('/root/mhpss-nepal-work/form-translation')

final = json.load(open('tools/i18n-ne-final.json'))
settled = json.load(open('tools/i18n-ne-authority-resolved.json'))
entries = {e['key']: e for e in json.load(open('tools/translatable.json'))}

copy = dict(final)
for k, v in settled.items():
    copy[k] = v['np']

print("parent edits:", len(final))
print("review additions:", len(settled), sorted(settled))
print("final copy for back-translation:", len(copy))

# real markup / id / href already checked by the parent tooling; re-assert here
TAG = re.compile(r'<[^>]+>')
bad = []
for k, v in copy.items():
    en = entries[k]['en']
    if entries[k].get('html') and TAG.findall(v) != TAG.findall(en):
        bad.append((k, 'markup'))
    for token in ('storeWarn','descCount','ver','cnt'):
        if ('id="%s"' % token) in en and token not in v:
            bad.append((k, 'lost id '+token))
print("defects in the composed copy:", bad)

json.dump(copy, open('tools/i18n-ne-final-copy.json','w',encoding='utf-8'),
          ensure_ascii=False, indent=2, sort_keys=True)
print("wrote tools/i18n-ne-final-copy.json")

# also write the English side, for the back-translation comparison
json.dump({k: entries[k]['en'] for k in copy},
          open('tools/i18n-backtrans-final-input.json','w',encoding='utf-8'),
          ensure_ascii=False, indent=2, sort_keys=True)
print("wrote tools/i18n-backtrans-final-input.json")
