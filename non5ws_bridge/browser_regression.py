"""Synthetic-only browser exercise; loopback server; outbound traffic denied.
Uses existing Hub assets read-only. Never simulates a backend acknowledgement.
"""
import csv
import hashlib
import io
import json
import mimetypes
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HUB = Path('/root/mhpss-nepal-work/hub')
OUT = ROOT / 'non5ws_bridge/evidence'
FILES = ['training-report.html', 'drafts/contact.html', 'drafts/referral-outcome.html', 'drafts/service-point.html', 'drafts/provider-register.html', 'phq9.html', 'selfreport.html']
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def do_GET(self):
        path = urlparse(self.path).path
        if path.endswith(('fb.js', 'fb-config.js', 'pwa.js')):
            data, mime = b'/* intentionally disabled in isolated synthetic test; no backend */', 'application/javascript'
        else:
            file = HUB / path.removeprefix('/hub/') if path.startswith('/hub/') else ROOT / path.removeprefix('/form/')
            if not file.is_file(): self.send_error(404); return
            data, mime = file.read_bytes(), mimetypes.guess_type(file.name)[0] or 'text/plain'
        self.send_response(200); self.send_header('Content-Type', mime); self.end_headers(); self.wfile.write(data)

def run():
    OUT.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}'
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for file in FILES:
            context = browser.new_context(accept_downloads=True, service_workers='block')
            context.route('**/*', lambda r: r.continue_() if r.request.url.startswith(base) else r.abort())
            page = context.new_page(); errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(base + '/form/' + file); page.wait_for_timeout(150)
            page.evaluate('''() => {
              const ev = e => {e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));};
              document.querySelectorAll('select').forEach(e=>{const o=[...e.options].find(o=>o.value && !['OTHER','OTH'].includes(o.value));if(o){e.value=o.value;ev(e);}});
              document.querySelectorAll('input[type=text],input[type=tel],input[type=email],textarea').forEach(e=>{e.value=e.type==='email'?'synthetic@example.invalid':e.type==='tel'?'0000000000':e.id==='ccode'?'NP-ABCDE-12345':e.id==='byear'?'2000':e.id==='dateBS'?'':'SYNTHETIC ONLY';ev(e);});
              document.querySelectorAll('input[type=date]').forEach(e=>{e.value='2026-10-01';ev(e);});
              document.querySelectorAll('input[type=number]').forEach(e=>{e.value='1';ev(e);});
              document.querySelectorAll('input[type=checkbox]').forEach(e=>{e.checked=true;ev(e);});
              const groups=new Set([...document.querySelectorAll('input[type=radio]')].map(e=>e.name));
              groups.forEach(n=>{const es=[...document.querySelectorAll('input[type=radio]')].filter(e=>e.name===n);const e=es.find(e=>e.value==='1')||es[0];e.checked=true;ev(e);});
              const q=document.querySelector('input[name=q8][value="1"]');if(q){q.checked=true;ev(q);}
              const mins=document.querySelector('#mins');if(mins)mins.value='15';
              const arrival=document.querySelector('#arrDate');if(arrival)arrival.value='2026-10-02';
            }''')
            checks = {}
            if file == 'drafts/contact.html':
                page.select_option('#outcome', 'REFER')
            if file == 'training-report.html':
                # Optional unknown is null; observed zero remains zero.
                page.fill('#u18', '')
                page.fill('#pwd', '0')
                page.fill('[data-f=female]', '')
                page.locator('button[type=submit]').click()
                checks['missing_sex_rejected'] = page.evaluate("() => L1.all('training').length === 0")
                # Keep test able to expose a defective save without inflating evidence.
                page.evaluate("() => L1.clear('training')")
                page.fill('[data-f=female]', '1')
                page.fill('#u18', '99')
                page.locator('button[type=submit]').click()
                checks['over_total_rejected'] = page.evaluate("() => L1.all('training').length === 0")
                page.fill('#u18', '')
            if file == 'drafts/contact.html':
                page.uncheck('#notgbv')
                page.locator('button[type=submit]').click()
                checks['safeguarding_rejected'] = page.evaluate("() => L1.all('contact').length === 0")
                page.check('#notgbv')
            if file == 'phq9.html':
                page.uncheck('#consent')
                page.locator('button[type=submit]').click()
                checks['no_consent_rejected'] = page.evaluate("() => L1.all('phq9').length === 0")
                page.check('#consent')
            inputs = page.evaluate("() => [...document.querySelectorAll('input,select')].map(e=>({id:e.id,name:e.name,type:e.type,value:e.value,valid:e.checkValidity()}))")
            # Ordinary submit control, retaining HTML constraint validation.
            page.locator('button[type=submit]').click()
            page.wait_for_timeout(100)
            records = page.evaluate("() => Object.fromEntries(Object.entries(localStorage).filter(([k,v])=>k.startsWith('mhpss-np-l1-')).map(([k,v])=>[k,JSON.parse(v)]))")
            csv_text = None
            if records:
                export = '#expCsv' if page.locator('#expCsv').count() else '#csvBtn'
                with page.expect_download() as dl: page.locator(export).click()
                csv_text = Path(dl.value.path()).read_text()
            result = {'checks':checks,'file':file,'page_errors':errors,'inputs':inputs,'records':records,'csv':csv_text,'messages':page.locator('#errs, #problems').all_text_contents(),'saved':bool(records),'exported':bool(csv_text)}
            if file=='phq9.html':
                result['dictionary_sha256'] = hashlib.sha256((HUB/'assets/i18n-strings.js').read_bytes()).hexdigest()
                result['languages'] = {}
                for lang in ('en','ne'):
                    page.evaluate('(lang)=>I18N.setLang(lang)',lang)
                    result['languages'][lang] = page.evaluate('''() => ({items:[...document.querySelectorAll('#items [data-i18n]')].filter(e=>/^phq9.item[1-9]$/.test(e.dataset.i18n)).map(e=>({key:e.dataset.i18n,text:e.textContent,dictionary:I18N.t(e.dataset.i18n)})),risk:document.querySelector('#risk').innerHTML,ribbon:document.querySelector('.ribbon').textContent})''')
            if file == 'training-report.html':
                page.select_option('#reportingRole', 'PARTNER')
                page.locator('button[type=submit]').click()
                partner = page.evaluate("() => L1.all('training').at(-1)")
                checks['partner_empty_counts'] = partner['participants'] == [] and partner['trained_total'] == 0 and partner['under_18'] is None
                result['partner_record'] = partner
            if file == 'selfreport.html':
                checks['answer_reset'] = page.locator('#say').input_value() == '' and page.locator('input[type=radio]:checked').count() == 0
                checks['age_options'] = page.locator('#ageband option').evaluate_all('(es)=>es.map(e=>e.value)')
            results.append(result)
            context.close()
        browser.close()
    server.shutdown()
    (OUT/'browser.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
    print(json.dumps([{'file':r['file'],'saved':r['saved'],'exported':r['exported'],'errors':r['page_errors'],'messages':r['messages']} for r in results],ensure_ascii=False,indent=2))
    return results
if __name__ == '__main__': run()
