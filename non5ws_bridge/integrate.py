"""Reproducible selective integration from exact source. Not a whole branch merge."""
from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parents[1]
PIN = '3f89f6ed118398efeb71fe3219d8f0988088fac1'
def source(name): return subprocess.check_output(['git','show',f'{PIN}:{name}'],cwd=ROOT,text=True)
def change(name, old, new):
    p=ROOT/name; s=p.read_text()
    if new in s: return
    if old not in s:
        raise ValueError(f'{name}: missing exact source context')
    p.write_text(s.replace(old,new))
# Only two age replacements; retain Home and all legacy records untouched.
for name in ['selfreport.html','drafts/contact.html']:
    change(name,'value="10-19"','value="10-17"')
    change(name,'value="20-59"','value="18-59"')
    change(name,'>10–19</option>','>10–17</option>')
    change(name,'>20–59</option>','>18–59</option>')
# Reapply the regression-proven explicit-zero fix after the pinned training delta.

change('selfreport.html','data-i18n="sr.age.10to19"','data-i18n="sr.age.10to17"')
change('selfreport.html','data-i18n="sr.age.20to59"','data-i18n="sr.age.18to59"')
change('selfreport.html','<script src="../hub/assets/i18n.js"></script>','<script src="lib/selfreport-strings.js"></script>\n<script src="../hub/assets/i18n.js"></script>')
# Training source delta is only a debug payload removal and null-safe repaint.
(ROOT/'training-report.html').write_text(source('training-report.html'))
change('training-report.html', 'return Number.isNaN(x[s]);', 'return x[s] === null || Number.isNaN(x[s]);')
change('training-report.html', 'Counts must be whole numbers, zero or more (', 'Enter every sex count explicitly, including zero; counts must be whole numbers, zero or more (')
change('training-report.html', 'L.toCSV(list, COLS), "text/csv"', 'L.toCSV(list.map(function (r) { var row = Object.assign({}, r); row.participants = JSON.stringify(r.participants); row.partners = JSON.stringify(r.partners); return row; }), COLS), "text/csv"')
# Training source diff contains no navigation changes. Other forms retain Home.
# Baseline training itself has no data-home-link; do not invent source history.
# Parked forms were moved down a directory without rebasing their assets.
# Keep them parked; fix only relative paths so the existing code can be tested.
for name in ['drafts/contact.html','drafts/referral-outcome.html','drafts/service-point.html','drafts/provider-register.html']:
    change(name,'../hub/','../../hub/')
    change(name,'src="pwa.js"','src="../pwa.js"')
# Source binding correction only: keep validated dictionary and clinical wording.
change('phq9.html','data-i18n="phq9.item9Instruction"><b>','data-i18n="phq9.item9Instruction" data-i18n-html><b>')
p = ROOT/'training-report.html'
p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines()) + '\n')
print('Selective source integration complete; no shared store/5Ws/dictionary changes.')
