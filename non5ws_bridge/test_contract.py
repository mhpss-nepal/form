import unittest
from non5ws_bridge.contract import adapt, ContractError

class ContractTests(unittest.TestCase):
    def test_training_units_and_unknown_are_not_attendance(self):
        raw = dict(kind='training', schema='mhpss-np-training/0.1.0-draft', org='SYNTHETIC', reporting_role='LEAD', counts_held_by_lead=False, participants=[dict(district='D', palika='P', cadre='C', female=1, male=0, other=0, total=1)], trained_total=1, under_18=None, with_disability=0)
        result = adapt(raw)
        self.assertEqual(result.collection, 'training_events')
        self.assertEqual(result.unit, 'people-trained-per-event')
        self.assertEqual(result.metrics, {'trained_total': 1, 'under_18': None, 'with_disability': 0})
        self.assertNotIn('reach', result.metrics)
        self.assertEqual(raw['participants'][0]['female'], 1)
        for bad in ('', '1', -1, 1.5, True):
            with self.subTest(bad=bad), self.assertRaises(ContractError):
                adapt(dict(raw, trained_total=bad))

if __name__ == '__main__': unittest.main()
