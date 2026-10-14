#!/usr/bin/env python3
"""Extract source questions, never source writers, into protected previews."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
FILES = ['contact', 'referral-outcome', 'provider-register', 'service-point']

def build(name):
    interactive = name in ['contact', 'referral-outcome']
    source_path = ROOT / 'tools' / 'source-templates' / (name + '.txt') if interactive else ROOT / 'drafts' / (name + '.html')
    source = source_path.read_text()
    scripts = re.findall(r'<script\b[^>]*>(.*?)</script>', source, re.S)
    dictionary = next(s for s in reversed(scripts) if 'var EN = {' in s)
    assert 'localStorage' not in dictionary and 'L1.' not in dictionary
    match = re.search(r'<body[^>]*>(.*?)<script', source, re.S)
    assert match is not None
    body = match.group(1)
    styles = '\n'.join(re.findall(r'<style[^>]*>.*?</style>', source, re.S))
    body = re.sub(r'<div class="ribbon".*?</div>', '', body, count=1, flags=re.S)
    body = re.sub(r'\s(?:on\w+|action|formaction)="[^"]*"', '', body)
    body = re.sub(r'<div class="banner"[^>]*>.*?(?:<span id="storeWarn"></span>).*?</div>', '', body, flags=re.S)
    body = re.sub(r'<section class="saved">.*?</section>', '', body, flags=re.S)
    body = re.sub(r'<p class="xs"[^>]*data-i18n="(?:pr|sp)\.foot".*?</p>', '', body, flags=re.S)
    body = body.replace('data-i18n="svc.p012"', '').replace('remembered for next time', 'Template question')
    body = body.replace('data-i18n="sp.h1hint"', '').replace('saved for next time', 'Template question')
    lists = '\n'.join('window.REVIEW_LISTS.' + key + ' = ' + value + ';' for key, value in re.findall(r'var (SERVICES|REASONS|ORG_TYPES|ACCESS|COST|A11Y) = (\[.*?\]);', source, re.S))
    note = ('Interactive preview — not saved or sent. Do not enter real personal information. Only sending, saving, export, location and contact-code generation are held. No account is needed.' if interactive else 'Read-only source questions. Saving, export and location are disabled. No account is needed.')
    html = '''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'none'; connect-src 'none'; form-action 'none'; base-uri 'none'; object-src 'none'">
<title>Protected preview — MHPSS Nepal</title>
<link rel="stylesheet" href="../../hub/assets/app.css"><link rel="stylesheet" href="../../hub/assets/design.css"><link rel="stylesheet" href="../../hub/assets/form.css">
<style>html,body{max-width:100%;margin:0} .wrap{min-width:0} .review-bar{padding:14px;background:#183039;color:white} .review-bar a{color:white} .review-bar button{min-width:44px;min-height:44px;margin:6px} .review-bar p{margin:6px 0} :focus-visible{outline:3px solid #d19e14} input:disabled,select:disabled,textarea:disabled{opacity:1;color:inherit;-webkit-text-fill-color:currentColor} [hidden]{display:none!important} .actions,.savebar,.sticky-save{position:static!important} pre{white-space:pre-wrap;overflow-wrap:break-word} .tw{max-width:100%;overflow:auto} #toast:empty{display:none} .top{flex-wrap:wrap} .top>*{min-width:0} .hint{white-space:normal} .review-bar button[aria-pressed=true]{font-weight:bold;text-decoration:underline}</style>
''' + styles + '''
<script src="../template-preview-20261014.js"></script></head><body class="fx">
<header class="review-bar"><a href="../index.html" target="_top">← Forms</a> · <a href="../../hub/" target="_top">Hub</a><strong> · Protected preview — not collecting</strong><p data-preview-notice>''' + note + '''</p><p>Source descriptions of saving describe a proposed workflow, not this preview. Nepali template wording remains a draft pending human review.</p><button type="button" data-review-lang="en">EN</button><button type="button" data-review-lang="ne">NE</button>''' + ('<button type="button" data-review-reset>Clear current preview</button>' if interactive else '') + '''</header>
''' + body + '''
<script src="../../hub/assets/codes.js"></script><script src="../../hub/assets/i18n-strings.js"></script>
<script>window.REVIEW_LISTS={};
''' + lists + '\n' + dictionary + '''
</script><script>mountTemplateReview(''' + repr(name) + ''');</script></body></html>
'''
    html = re.sub(r'<(input|select|textarea)\b', r'<\1 disabled autocomplete="off"', html)
    html = re.sub(r'<button\b(?![^>]*data-review-)', '<button disabled', html)
    output = 'contact-instrument' if name == 'contact' else name
    (ROOT / 'review' / (output + '.html')).write_text('\n'.join(line.rstrip() for line in html.splitlines()) + '\n')

if __name__ == '__main__':
    for name in ['contact', 'referral-outcome']: build(name)
    print('Built protected source-question previews; no writers included')
