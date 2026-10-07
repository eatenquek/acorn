import unittest
from label_parser import extract, parse_directions, validate


def lines(*texts, confidence=1.0):
    return [{'text': t, 'ocrConfidence': confidence} for t in texts]


class Directions(unittest.TestCase):
    def check(self, text, per_day, dose=None, times=None, hold=None):
        p = parse_directions(text)
        self.assertEqual(p['hold'], hold, text)
        self.assertEqual(p['perDay'], per_day, text)
        if dose is not None:
            self.assertEqual(p['dose'], dose, text)
        if times is not None:
            self.assertEqual(p['times'], times, text)

    def test_daily_wordings(self):
        self.check('Take ONE tablet by mouth once daily.', 1, '1 tablet', ['08:00'])
        self.check('Take 1 tablet(s) every morning', 1, '1 tablet', ['08:00'])
        self.check('TAKE ONE (1) TABLET AT BEDTIME', 1, '1 tablet', ['21:00'])
        self.check('1 TAB ON', 1, '1 tablet', ['21:00'])
        self.check('1 tab OM', 1, '1 tablet', ['08:00'])
        self.check('Take l tablet daily', 1, '1 tablet')
        self.check('Take 1/2 tablet once a day', 1, '1/2 tablet')
        self.check('Take ½ tab daily', 1, '1/2 tablet')
        self.check('Take one tablet at 8am every day', 1, times=['08:00'])
        self.check('Take one tablet at 9.30 pm daily', 1, times=['21:30'])

    def test_multiple_times(self):
        self.check('TAKE 1 CAPSULE BY MOUTH THREE TIMES DAILY FOR 10 DAYS', 3, '1 capsule', ['08:00', '14:00', '20:00'])
        self.check('Take 1 tablet 2 times a day after meals', 2, times=['08:00', '19:00'])
        self.check('Take 2 tablets twice a day', 2, '2 tablets')
        self.check('Take 1 tab BD', 2, '1 tablet')
        self.check('1 cap TDS after food', 3, '1 capsule', ['08:00', '13:00', '19:00'])
        self.check('Take 1 tablet QID', 4)
        self.check('Take 1 tablet 3x daily', 3)
        self.check('Take one tablet in the morning and at night', 2, times=['08:00', '21:00'])
        self.check('Take one tablet after breakfast and dinner', 2, times=['08:00', '19:00'])
        self.check('Take 1 tablet 3 times after meals', 3)

    def test_intervals(self):
        self.check('Take 1 capsule every 8 hours', 3, times=['06:00', '14:00', '22:00'])
        self.check('Take 1 tablet every 12 hours', 2, times=['08:00', '20:00'])
        self.check('Take 1 tablet q6h', 4)
        self.check('Take 1 tablet Q6H', 4)
        self.check('Take 1 tablet every 5 hours', None, hold='unsupported_interval')
        self.assertEqual(parse_directions('Take 1-2 tablets every 4-6 hours')['hold'], 'variable')

    def test_other_forms(self):
        self.check('Take 5 ml three times a day', 3, '5 ml')
        self.check('Instil 1 drop into each eye twice daily', 2, '1 drop')
        self.check('Inhale 2 puffs twice daily', 2, '2 puffs')
        self.assertEqual(parse_directions('Inhale 2 puffs twice daily')['route'], 'Inhaled')
        self.assertEqual(parse_directions('Instil 1 drop into each eye twice daily')['route'], 'Eye')

    def test_held(self):
        for text in ['Take 1 tablet as needed for pain', 'Take 1-2 tablets every 4-6 hours', 'Take 2 tablets daily then 1 tablet daily',
                     'Take one tablet weekly on Monday', 'Take 1 tablet up to 3 times a day', 'Take one or two tablets at night',
                     'Use as directed', 'Inject 10 units at bedtime', 'Take 1 tablet every other day', 'Take 1 tablet PRN']:
            self.assertTrue(parse_directions(text)['hold'], text)

    def test_hold_kinds(self):
        for text, kind in [('Take 1 tablet as needed for pain', 'as_needed'), ('TAKE 1 TABLET BY MOUTH UP TO 2 TIMES DAILY', 'variable'),
                           ('Take one or two tablets at night', 'variable'), ('Take 2 tablets daily then 1 tablet daily', 'changing'),
                           ('Take one tablet weekly on Monday', 'not_daily'), ('Use as directed', 'as_directed'),
                           ('Inject 10 units at bedtime', 'injection')]:
            self.assertEqual(parse_directions(text)['hold'], kind, text)

    def test_until_finished_is_fine(self):
        self.check('Take 1 capsule 3 times a day until finished', 3)
        self.assertEqual(parse_directions('Take 1 tablet twice daily for 2 weeks')['durationDays'], 14)


class Labels(unittest.TestCase):
    def test_wrapped_label_with_garbled_bottle(self):
        meds = extract(lines('PHARMACY', 'Pharmacy Name', '123 Main Street', '(555) 123-4567', 'TAKE 1 CAPSULE BY MOUTH',
                             'THREE TIMES DAILY FOR 10 DAYS', 'Amoxicillin 500 mg Capsules', 'Quantity: 30, Refills: 0',
                             'FINISH ALL MEDICATION UNLESS OTHERWISE DIRECTED.', 'NEICAPSULE BY MOUTH', 'TFEE TIMES DAILY FOR 10 DAYS',
                             'eocin 600mg Capsules'))
        self.assertEqual(len(meds), 1)
        m = meds[0]
        self.assertEqual((m['name'], m['strength'], m['dose'], m['perDay'], m['durationDays']), ('Amoxicillin 500 mg Capsules', '500 mg', '1 capsule', 3, 10))
        self.assertEqual(m['otherCandidates'], ['eocin 600mg Capsules'])
        self.assertFalse(m['needsClarification'])

    def test_ocr_run_together_and_garbled_copy(self):
        meds = extract(lines('TAKE1CAPSULE BY MOUTH', 'THREE TIMES DAILY FOR 10 DAYS', 'Amoxicillin 500 mg Capsules',
                             'NE1CAPSULE BY MOUTH', 'ORCTIRES DRILY PUM FOURA', 'cociin 500 mg Cepsules'))
        self.assertEqual(len(meds), 1)
        self.assertEqual((meds[0]['dose'], meds[0]['perDay']), ('1 capsule', 3))

    def test_dose_and_frequency_on_separate_lines(self):
        m = extract(lines('Losartan 50mg', '1 TABLET', 'TWICE DAILY'))[0]
        self.assertEqual((m['dose'], m['perDay']), ('1 tablet', 2))

    def test_name_split_from_strength(self):
        m = extract(lines('AMOXICILLIN', '500MG CAPSULES', 'Take 1 capsule 3 times a day'))[0]
        self.assertEqual(m['name'], 'AMOXICILLIN 500MG CAPSULES')

    def test_generic_name_above_brand(self):
        meds = extract(lines('Miss Member', 'DATE: 01/01/2016', 'Metformin 500mg', 'IC Glucophage 500mg',
                             'TAKE 1 TABLET BY MOUTH UP TO 2 TIMES DAILY', 'RX 1234567-09', 'QTY: 60'))
        self.assertEqual(meds[0]['name'], 'Metformin 500mg')
        self.assertEqual(meds[0]['holdReasons'], ['variable'])

    def test_name_without_strength(self):
        m = extract(lines('Clinic Pharmacy', 'PANADOL', 'Take 2 tablets 3 times a day'))[0]
        self.assertEqual(m['name'], 'PANADOL')

    def test_advice_line_is_not_second_medicine(self):
        meds = extract(lines('Metformin 500 mg tablets', 'Take one tablet twice daily', 'with meals', 'Take with food'))
        self.assertEqual(len(meds), 1)
        self.assertEqual(meds[0]['perDay'], 2)

    def test_record_with_several_medicines(self):
        meds = extract(lines('Medication record', 'Amlodipine 5 mg tablet', 'Take 1 tablet every morning',
                             'Metformin 500 mg tablet', 'Take 1 tablet twice a day after meals'))
        self.assertEqual([m['name'] for m in meds], ['Amlodipine 5 mg tablet', 'Metformin 500 mg tablet'])
        self.assertEqual([m['perDay'] for m in meds], [1, 2])

    def test_record_rows_with_name_and_directions_together(self):
        meds = extract(lines('Amlodipine 5 mg tablet Take 1 tablet every morning', 'Metformin 500 mg tablet Take 1 tablet twice a day after meals',
                             'Paracetamol 500 mg tablet Take 2 tablets 4 times a day as needed for pain'))
        self.assertEqual([(m['name'], m['perDay'], m['needsClarification']) for m in meds],
                         [('Amlodipine 5 mg tablet', 1, False), ('Metformin 500 mg tablet', 2, False), ('Paracetamol 500 mg tablet', 4, True)])

    def test_missing_route_assumed_for_tablets(self):
        m = extract(lines('Atorvastatin 20mg', 'Take 1 tablet at night'))[0]
        self.assertEqual(m['route'], 'By mouth')
        self.assertIn('route_assumed', m['warnings'])

    def test_low_confidence_warns_instead_of_holding(self):
        m = extract(lines('Atorvastatin 20mg', 'Take 1 tablet at night', confidence=0.5))[0]
        self.assertIn('low_confidence', m['warnings'])
        self.assertFalse(m['needsClarification'])

    def test_no_directions_goes_to_review(self):
        m = extract(lines('Atorvastatin 20mg tablets'))[0]
        self.assertEqual(m['name'], 'Atorvastatin 20mg tablets')
        self.assertIn('no_directions', m['warnings'])


class Validate(unittest.TestCase):
    base = {'name': 'Amoxicillin 500 mg Capsules', 'strength': '500 mg', 'dose': '1 capsule', 'route': 'By mouth',
            'directions': 'TAKE 1 CAPSULE BY MOUTH THREE TIMES DAILY FOR 10 DAYS'}

    def test_ok(self):
        r = validate(dict(self.base))
        self.assertNotIn('error', r)
        self.assertEqual(r['draft']['perDay'], 3)

    def test_dose_written_differently_is_ok(self):
        self.assertNotIn('error', validate({**self.base, 'dose': 'one cap'}))

    def test_mismatches(self):
        self.assertIn('error', validate({**self.base, 'dose': '2 capsules'}))
        self.assertIn('error', validate({**self.base, 'strength': '250 mg'}))
        self.assertIn('error', validate({**self.base, 'directions': 'Take 1 capsule'}))

    def test_edit_into_as_needed_holds(self):
        self.assertTrue(validate({**self.base, 'directions': 'Take 1 capsule as needed'}).get('hold'))


if __name__ == '__main__':
    unittest.main()
