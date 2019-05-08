"""
Pre-made sample data used for standalone runs of formulas.py.
"""

def get_sample_questions():
    """
    Return a sample of questions.
    """
    questions = {
        'CIGOVX1': [
            '1',
            ['SQ001', 'SQ002'],
            ['SQ001', 'SQ002abc'],
        ],
        'CIGOVX2': [
            '1',
            ['SQ001', 'SQ002'],
            ['SQ001', 'SQ002'],
        ],
        'CIGOVX3': [
            'N',
            None,
            None,
        ],
        'CIGOVX4': [
            'Y',
            None,
            None,
        ],
    }
    return questions


def get_sample_response():
    """
    Return a map of question ids to a single value or list of tuples.

    For array-like questions types return a list of tuples, where
    the last tuple entry is an answer and the 1st and possibly 2nd
    element is the subquestion-id.
    """
    response = {
        'CIGOVX1': [
            ('SQ001', 'SQ001', 'AX'),
            ('SQ001', 'SQ002abc', 'AY'),
            ('SQ002', 'SQ001', 'AZ'),
            ('SQ002', 'SQ002abc', 'AX'),
        ],
        'CIGOVX2': [
            ('SQ001', 'SQ001', 4),
            ('SQ001', 'SQ002', 7),
            ('SQ002', 'SQ001', 10),
            ('SQ002', 'SQ002', 200),
        ],
        'CIGOVX3': 7,
        'CIGOVX4': 'Y',
    }
    return response
