"""Acceptance assertions over actual browser saves/downloads, not invented API responses."""
import csv
import io
import json
from pathlib import Path
import subprocess
import unittest
from non5ws_bridge.contract import adapt, ContractError, MAPPINGS

ROOT = Path(__file__).resolve().parents[1]

class BrowserEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = json.loads((ROOT/'non5ws_bridge/evidence/browser.json').read_text())

    def test_seven_actual_saves_and_csv_downloads_map_to_separate_receiving_targets(self):
        self.assertEqual(len(self.evidence), 7)
        collections = set()
        for evidence in self.evidence:
            with self.subTest(file=evidence['file']):
                self.assertEqual(evidence['page_errors'], [])
                self.assertTrue(evidence['saved'])
                self.assertTrue(evidence['exported'])
                rows = [r for records in evidence['records'].values() for r in records]
                self.assertEqual(len(rows), 1)
                received = adapt(rows[0])
                collections.add(received.collection)
                csv_rows = list(csv.DictReader(io.StringIO(evidence['csv'])))
                self.assertEqual(len(csv_rows), 1)
                self.assertNotIn('reach', received.metrics)
                if received.instrument == 'training':
                    self.assertEqual(json.loads(csv_rows[0]['participants']), rows[0]['participants'])
        self.assertEqual(len(collections), 7)

    def test_training_rejects_missing_sex_and_over_total_without_saving(self):
        training = self.evidence[0]
        self.assertTrue(training['checks']['missing_sex_rejected'])
        self.assertTrue(training['checks']['over_total_rejected'])
        received = adapt(next(iter(training['records'].values()))[0])
        self.assertIsNone(received.metrics['under_18'])
        self.assertEqual(received.metrics['with_disability'], 0)
        self.assertTrue(training['checks']['partner_empty_counts'])
        partner = adapt(training['partner_record'])
        self.assertIsNone(partner.metrics['trained_total'])

    def test_source_sensitive_paths_preserved(self):
        base = 'c71b18c4f667f5b53ff4ff98334dd2a9b48f3db3'
        for file in ['5ws-report.html','lib/store.js','index.html','contact.html','referral.html']:
            original = subprocess.check_output(['git','show',f'{base}:{file}'],cwd=ROOT)
            self.assertEqual(original, (ROOT/file).read_bytes(), file)
        for file in ['phq9.html','selfreport.html']:
            self.assertIn('data-home-link', (ROOT/file).read_text())
        for file in ['drafts/contact.html','selfreport.html']:
            self.assertNotIn('>10–19</option>', (ROOT/file).read_text())
            self.assertNotIn('>20–59</option>', (ROOT/file).read_text())

    def test_phq9_source_vs_render_dictionary_and_safety(self):
        evidence = next(e for e in self.evidence if e['file']=='phq9.html')
        self.assertTrue(evidence['checks']['no_consent_rejected'])
        for lang, rendered in evidence['languages'].items():
            self.assertEqual(len(rendered['items']), 9)
            self.assertTrue(all(i['text']==i['dictionary'] for i in rendered['items']))
            self.assertIn('<b>', rendered['risk'])
            self.assertNotIn('&lt;b&gt;', rendered['risk'])
        self.assertIn('referral.html', evidence['languages']['en']['risk'])
        # Actual Hub dictionary still owns instruction; source wording cannot override it.
        self.assertIn('English items only', (ROOT/'phq9.html').read_text())
        self.assertIn('प्रमाणीकृत', evidence['languages']['ne']['ribbon'])

    def test_legacy_age_and_anonymous_feedback(self):
        evidence = next(e for e in self.evidence if e['file']=='selfreport.html')
        raw = next(iter(evidence['records'].values()))[0]
        self.assertTrue(evidence['checks']['answer_reset'])
        self.assertIn('10-17', evidence['checks']['age_options'])
        self.assertNotIn('10-19', evidence['checks']['age_options'])
        for age in ('10-19','20-59'):
            received = adapt(dict(raw, age_band=age))
            self.assertEqual(received.payload['age_band'], age)
            self.assertTrue(any('legacy' in w for w in received.warnings))
        with self.assertRaises(ContractError): adapt(dict(raw, contact_code='NP-ABCDE-12345'))
        with self.assertRaises(ContractError): adapt(dict(raw, phone='0000000000'))
        self.assertTrue(any('human review' in w for w in adapt(raw).warnings))

    def test_schema_and_instrument_isolation(self):
        for kind, mapping in MAPPINGS.items():
            with self.assertRaises(ContractError): adapt({'kind':kind,'schema':'5ws/1'})
        with self.assertRaises(ContractError): adapt({'kind':'5ws','schema':'5ws/1'})
        with self.assertRaises(ContractError): adapt({'kind':'referral','schema':MAPPINGS['referral'][0],'record_type':'referral'})

if __name__=='__main__': unittest.main()
