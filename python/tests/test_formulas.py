"""
Unit test the formula parser.
"""

import unittest
from extractor.formulas import validate, evaluate


def get_response():
    return {
        'QID1': [
            ('SQ001', 'SQ001', 'AX'),
            ('SQ001', 'SQ002abc', 'AY'),
            ('SQ002', 'SQ001', 'AZ'),
            ('SQ002', 'SQ002abc', 'AX'),
        ],
        'QID2': [
            ('SQ001', 'SQ001', 4),
            ('SQ001', 'SQ002', 7),
            ('SQ002', 'SQ001', 10),
            ('SQ002', 'SQ002', 200),
        ],
        'QID3': 7,
        'QID4': 'Y',
        'QID5': 'A3X',
        'QID6': [
            ('SQ001', 'A2'),
            ('SQ002', 'A1'),
        ],
    }


def get_questions():
    return {
        'QID1': [';',  # Array (Multi Flexible) (Text)
            ['SQ001', 'SQ002'],
            ['SQ001', 'SQ002abc'],
        ],
        'QID2': ['1',  # Array (Flexible Labels) dual scale
            ['SQ001', 'SQ002'],
            ['SQ001', 'SQ002'],
        ],
        'QID3': ['N', None, None],  # Numerical input
        'QID4': ['Y', None, None],  # Yes/No
        'QID5': ['M', None, None],  # Multiple options
        'QID6': ['C',  # Array (Yes/No/Uncertain)
            ['SQ001', 'SQ002'],
        ] 
    }


def get_valid_formulas():
    return {
        'QID3': 7,
        '1': 1,
        'ITE(HASVAL(QID5, A3X), 5, 10)': 5,
        '2*ITE(HASVAL(QID5, A3Y), 5, 10)': 20,
        'VAL(QID2,SQ001, SQ002)+2': 9,  # 7 + 2 = 9
        'ITE(Eq(QID3,7.0), 5, 10) + 7 + VAL(QID2, SQ001, SQ001)': 16,  # 5 + 7 + 4 = 16
    }


def get_invalid_formulas():
    return {
        1: 'QID4',  # boolean
        2: '1 < 2',  # boolean
        3: 'ITE(ITE(HASVAL(QID5, A3X), 5, 10), 9, 11)',  # 1st arg of ITE should be Boolean
        4: 'ITE(VAL(QID2, SQ001, SQ002) < 1, QID3 >= 5, 11)',  # 1st arg of ITE should be Boolean
        5: 'ITE(HASVAL(QID2,SQ001, SQ002), 20, 30)-2*QID3',
        6: 'ITE(Eq(QID3,7.0), 5, 10) / 3 + 7 + HASVAL(QID2, HH)',
    }


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.response = get_response()
        self.questions = get_questions()
        self.valid_formulas = get_valid_formulas()
        self.invalid_formulas = get_invalid_formulas()

    def test_validate_and_evaluate_valid(self):
        for formula in self.valid_formulas:
            errors = validate(formula, self.questions)
            self.assertEqual(errors, [])
            expected_value = self.valid_formulas[formula]
            expr, value, errors = evaluate(formula, self.questions, self.response)
            #print(errors, formula, expr)
            self.assertEqual(value, expected_value)
            self.assertEqual(errors, [])

    def test_validate_valid(self):
        formulas = self.invalid_formulas
        errors = validate(formulas[1], self.questions)
        self.assertEqual(errors, ['QID4 refers to a question of type Boolean, but should be Number'])
        errors = validate(formulas[2], self.questions)
        self.assertEqual(errors, ['True is Boolean, but no Boolean was expected'])
        errors = validate(formulas[3], self.questions)
        self.assertEqual(errors, ['ITE(HASVAL(QID5, A3X), 5, 10) is a Numeric expression, but no Number is expected'])
        errors = validate(formulas[4], self.questions)
        self.assertEqual(errors, ['QID3 >= 5 is a Boolean expression, but no Boolean is expected'])
        errors = validate(formulas[5], self.questions)
        self.assertEqual(errors, ['HASVAL(QID2, SQ001, SQ002) refers to non-existent subquestion'])
        errors = validate(formulas[6], self.questions)
        self.assertEqual(set(errors), set([
            'HASVAL(QID2, HH) evaluates to Boolean, but no Boolean was expected',
            'HASVAL(QID2, HH) refers to non-existent question'
        ]))


if __name__ == '__main__':
    unittest.main()
