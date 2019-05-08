"""
Loading, checking, evaluation and export of indicators.

If run from the command line a survey_id and an indicator expression (e.g.
IND1: '''(QID1 + QID2)/2'''
) (or more than one) must be given and the indicator(s) are checked
syntactically against the survey (existence of fields etc.).
"""

import re
import hjson
from collections import namedtuple
from .formulas import validate, evaluate, debug
from .questions import get_questions


Indicator = namedtuple('Indicator', ['name', 'formula'])


re_comment = re.compile(r'^\s*#')


def parse_indicator_definitions(indicator_definitions):
    """
    Parse a str for indicator definitions in hjson format.

    The definition rawtext must be an hjson encoded dict mapping indicator
    names to formulas; the curly braces at the begining and
    end of the dict are optional (they will be added).

    Load hjson, replace newlines with spaces in formulas and return
    the result. Also remove comment lines and empty lines.

    :returns: a list of Indicator objects

    :Example:

      indicator_definitions might look like this:

      IND1: '''(Q1 + Q2) / 2'''
      # some comment
      IND2: '''ITE(HASVAL(Q3, A1), Q4, 0)'''
    """
    lines = indicator_definitions.strip().replace('\r\n', '\n').split('\n')
    lines_filtered = [line for line in lines if line and not re_comment.match(line)]
    prefix = '' if lines_filtered[0].strip()[0] == '{' else '{'
    postfix = '' if lines_filtered[-1].strip()[-1] == '}' else '}'
    indicators_raw = hjson.loads(prefix + '\n'.join(lines_filtered) + '\n' + postfix + '\n')
    indicators = []
    for ind_name, formula in indicators_raw.items():
        indicators.append(Indicator(name=str(ind_name), formula=str(formula).replace('\n', ' ')))
    return indicators


def check_indicators(survey_id, indicator_definitions):
    """
    Return check results for rawtext indicator definitions.

    Return
    1) a boolean status flag (True mean ok),
    2) a ``problems`` dict, which maps indicator names to lists of error messages,
    3) a list of good indicator (those which passed the check)
    """
    questions = get_questions(survey_id)
    try:
        indicators = parse_indicator_definitions(indicator_definitions)
    except:
        return False, {'all indicators': ['The input must be in hjson format']}, []
    problems = {}
    found_errors = False
    good_indicators = []
    for indicator in indicators:
        errors = validate(indicator.formula, questions, debug=False)
        if errors:
            found_errors = True
            problems[indicator.name] = errors
        else:
            good_indicators.append(indicator)
    return not found_errors, problems, good_indicators


def calculate_indicators(survey_id, indicators, responses, response_ids):
    """
    Calculate indicator values for specified responses of a survey.

    Return a dict mapping response_ids to response results
    and a dict mapping response_ids to response errors.

    Each response result is a dict mapping indicator names
    to a result. This result ist a dict containing an 'expression'
    and a 'value'. The 'expression' is a string and 'value' is the
    float content of 'expression', or None. The 'expression' contains
    the number calculated from the indicator expression when substituting
    the answer values. If not all answer variable can be substituted,
    their names remain. If an error occurred, both 'expression' and
    'value' are None.

    Each response error is a dict mapping indicator names
    to a list of error message strings.
    """
    questions = get_questions(survey_id)
    all_results = {}
    all_errors = {}
    for response_id in response_ids:
        response = responses[response_id]
        response_result = {}
        response_errors = {}
        for indicator in indicators:
            expression, value, errors = evaluate(
                indicator.formula, questions, response, debug=False, debug_subs=False)
            response_result[indicator.name] = {
                'expression': str(expression),
                'value': value,
            }
            if errors:
                response_errors[indicator.name] = errors
        all_results[response_id] = response_result
        if response_errors:
            all_errors[response_id] = response_errors
    return all_results, all_errors


if __name__ == '__main__':
    import sys
    from pprint import pprint
    if len(sys.argv) < 2:
        print('Please give a survey_id and an indicator as args.')
        print("Example:   123456 \"IND1: '''(Q! + Q2)/2'''\"")
        sys.exit(1)
    try:
        survey_id = int(float(sys.argv[1]))
        indicator_definitions = sys.argv[2]
    except:
        print('Invalid arguments')
        sys.exit(1)
    inds = parse_indicator_definitions(indicator_definitions)
    status_ok, problems, good_indicators = check_indicators(survey_id, indicator_definitions)
    print('==== status_ok:', status_ok)
    if problems:
        print('==== problems:')
        pprint(problems)
    print('==== indicators which have passed the check:')
    pprint(good_indicators)
    if len(sys.argv) == 4:
        # calculate result value
        response_id = int(float(sys.argv[3]))
        from .responses import get_responses
        responses = get_responses(survey_id)[0]
        results, errors = calculate_indicators(survey_id, good_indicators, responses, [response_id])
        print('==== calculated indicator results (after substituting response values)')
        pprint(results)
        print('==== errors while caclulating indicator values')
        pprint(errors)
