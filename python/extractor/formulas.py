"""
Parse, check and evaluate simple formulas against a limesurvey.

This script can also be used on the command line;
please give a survey_id as arg1 and a formula as arg2.

The formulas we can handle are arithmetic expressions with 'ITE'
(the sympy If-Then-Else) and two special functions, 'VAL' and 'HASVAL'.

'VAL' is a function that takes a question id as 1st parameter
and one or two more paramters, being the subquestion ids in the
1st and possibly 2nd dimension. It means the value of the response
for the specified subquestion.

'HASVAL' is also a function and takes the same arguments as 'VAL'
plus a 3rd or 4th argument which may be a number or a string literal.
It evaluates to True or False depending on whether that last
argument equals the the value of the response for the specified
subquestion.

'LEN' is also a function and takes a symbol which must evaluate to a
string. Upon evaluation it return the length of the string.


Howto write formulas:

You write arithmetic expressions with parentheses and use question_ids
(meaning the answer value for that question) or VAL(question_id, subquestion_id1)
or VAL(question_id, subquestion_id1, subquestion_id2) (meaning the answer
value for a subquestion) and moreover these functions: ITE, VAL, HASVAL

In ITE the first argument (boolean) can be a comparison
(<, <=, >, >=, Eq). Note: Eq compares two numeric expressions, e.g.
Eq(1, 1) evaluates to True.

HASVAL compares an answer to a question (subquestion) against a fixed
value. The value can be numeric or alphanumeric (beginning with a letter).
To compare a question against a numeric value use Eq(QID, 5).
For non-numeric or subquestion comparisons use HASVAL.

Upon evaluation of formulas the answer values are substituted.
If the answer value is empty an expression whose name begins with
'MISSING_' and contains infomraiton on the (sub-)question ids
is substituted.
"""

import sympy
from sympy.parsing import sympy_parser
from sympy.core.add import Add
from sympy.core.mul import Mul
from sympy.core.power import Pow
from sympy.core.function import Function
from sympy.core.numbers import Number
from sympy.core.symbol import Symbol
from sympy.core.sympify import sympify
from sympy.logic.boolalg import ITE as ITE_Orig
from sympy.functions.elementary.complexes import Abs
from sympy import S
from sympy.core.relational import (Equality, StrictGreaterThan, 
                                   GreaterThan, StrictLessThan, LessThan)
from sympy.logic.boolalg import BooleanTrue, BooleanFalse, And, Or
from pprint import pprint

VAL = Function('VAL')
HASVAL = Function('HASVAL')
LEN = Function('LEN')


class ITE(ITE_Orig):
    """
    Override sympy.logic.boolalg.ITE to avoid a parsing problem.

    Without adding :func:`as_coeff_Mul` we get this error when parsing:
    "AttributeError: 'ITE' object has no attribute 'as_coeff_Mul'"
    """
    def as_coeff_Mul(self, rational=False):
        return S.One, self

    def _eval_power(self, expt):
        return None

    def as_base_exp(self):
        return self, S.One


local_dict = {
    'ITE': ITE,
    'VAL': VAL,
    'HASVAL': HASVAL,
}


def parse_recursive(expr, questions, response=None, errors=None,
                    substitutions=None, expected='Number', debug=False):
    """
    Parse a expression recursively while handling local names specially.

    Handle 'VAL' and 'HASVAL' specially.

    We check the validity of the expression against the questions and collect
    the ``errors``. If another type (numeric or boolean) is obtained than
    expected, we also add an error.

    The kwarg ``expected`` can be 'Number' or 'Boolean' and means that the
    evaluation of ``expr`` is expected to yield the respective type.
    If the expression is terminal one (Number, VAL, HASVAL or Symbol),
    then it must be of the exected type, or we add an error to ``errors``.

    If response is not None, we collect ``substitutions``, i.e., 2-tuples
    (expr, value), where value is taken from response.

    ``debug`` turns on debugging to stdout.
    """
    if errors is None:
        errors = []
    if substitutions is None:
        substitutions = []
    if expr.func in (Add, Mul, Pow, Abs):
        if debug:
            debug(expr.func.__name__, expr.args)
        if expected != 'Number':
            errors.append(str(expr) + ' is a Numeric expression, but no Number is expected')
        for arg in expr.args:
            parse_recursive(arg, questions, response=response, errors=errors,
                            substitutions=substitutions, expected='Number', debug=debug)
    elif expr.func in (Equality, StrictGreaterThan, GreaterThan, StrictLessThan, LessThan):
        if debug:
            debug(expr.func.__name__, expr.args)
        if expected != 'Boolean':
            errors.append(str(expr) + ' is a Boolean expression, but no Boolean is expected')
        for arg in expr.args:
            parse_recursive(arg, questions, response=response, errors=errors,
                            substitutions=substitutions, expected='Number', debug=debug)
    elif expr.func in (And, Or):
        if debug:
            debug(expr.func.__name__, expr.args)
        if expected != 'Boolean':
            errors.append(str(expr) + ' is a Boolean expression, but no Boolean is expected')
        for arg in expr.args:
            parse_recursive(arg, questions, response=response, errors=errors,
                            substitutions=substitutions, expected='Boolean', debug=debug)
    elif expr.func == ITE:
        if debug:
            debug(expr.func.__name__, expr.args)
        if expected != 'Number':
            errors.append(str(expr) + ' is a Numeric expression, but no Number is expected')
        for ind, arg in enumerate(expr.args):
            exp = 'Boolean' if ind == 0 else 'Number'
            parse_recursive(arg, questions, response=response, errors=errors,
                            substitutions=substitutions, expected=exp, debug=debug)
    elif expr.func.is_Number:
        if debug:
            debug('Number', expr)
        if expected != 'Number':
            errors.append(str(expr) + ' is a Number, but no Number was expected')
    elif str(expr.func) == 'VAL':
        if debug:
            debug('VAL', expr)
        subquestion = get_symbols(expr, errors, debug=debug)
        if debug:
            debug('VAL contains', subquestion)
        if len(subquestion) < 2 or len(subquestion) > 3:
            errors.append(str(expr) + ' VAL must have 2 or 3 arguments')
        elif not check_subquestion_exists(subquestion, questions):
            errors.append(str(expr) + ' refers to non-existent subquestion')
        elif expected != 'Number':
            errors.append(str(expr) + ' evaluates to Number, but no Number was expected')
        elif response:
            subs = get_subquestion_answer(response, questions, subquestion)
            if subs is None:
                subs = sympify('MISSING_' + '_'.join(subquestion))
            substitutions.append((expr, subs))
    elif str(expr.func) == 'HASVAL':
        if debug:
            debug('HASVAL', expr)
        if expected != 'Boolean':
            errors.append(str(expr) + ' evaluates to Boolean, but no Boolean was expected')
        subq_val = get_symbols(expr, errors, debug=debug)
        if debug:
            debug('HASVAL contains', subq_val)
        if len(subq_val) < 2 or len(subq_val) > 4:
            errors.append(str(expr) + ' HASVAL must have 2, 3 or 4 arguments')
        else:
            if len(subq_val) == 2:
                question_id = subq_val[0]
                value = subq_val[1]
                if not question_is_nonarray(questions, question_id):
                    errors.append(str(expr) + ' refers to non-existent question')
                elif response:
                    subs = compare_question_answer(response, question_id, value)
                    substitutions.append((expr, subs))
            else:  # comparison for a 1- or 2-dim subquestion
                if not check_subquestion_exists(subq_val[:-1], questions):
                    errors.append(str(expr) + ' refers to non-existent subquestion')
                elif response:
                    subquestion = subq_val[:-1]
                    value = subq_val[-1]
                    subs = compare_subquestion_answer(response, questions, subquestion, value)
                    substitutions.append((expr, subs))
    elif str(expr.func) == 'LEN':
        if debug:
            debug('LEN', expr)
        if expected == 'Boolean':
            errors.append(str(expr) + ' evaluates to a Number, but a Boolean was expected')
        subquestion = get_symbols(expr, errors, debug=debug)
        if len(subquestion) < 1 or len(subquestion) > 3:
            errors.append(str(expr) + ' LEN must have 1, 2 or 3 arguments')
        else:
            if len(subquestion) == 1:
                question_id = subquestion[0]
                if not question_is_nonarray(questions, question_id):
                    errors.append(str(expr) + ' refers to non-existent question')
                elif response:
                    answer = response[question_id]
                    if answer is None:
                        subs = 0
                    else:
                        subs = len(str(answer))
                    substitutions.append((expr, subs))
            else:
                if not check_subquestion_exists(subquestion, questions):
                    errors.append(str(expr) + ' refers to non-existent subquestion')
                elif response:
                    answer = get_subquestion_answer(response, questions, subquestion)
                    if answer is None:
                        subs = 0
                    else:
                        subs = len(str(answer))
                    substitutions.append((expr, subs))
    elif expr.func == Symbol:
        if debug:
            debug('Symbol', expr)
        if str(expr) not in questions:
            errors.append(str(expr) + ' is not a question id')
        else:
            question_type = get_question_type(str(expr), questions)
            if expected != question_type:
                errors.append(str(expr) +
                              ' refers to a question of type %s, but should be %s'
                              % (question_type, expected)
                )
            if response:
                subs = get_answer_expression(response, questions, str(expr))
                if subs is None:
                    subs = sympify('MISSING_' + str(expr))
                substitutions.append((expr, subs))
    elif expr.func in (BooleanTrue, BooleanFalse):
        if debug:
            debug('Symbol', expr)
        if expected != 'Boolean':
            errors.append(str(expr) + ' is Boolean, but no Boolean was expected')
    else:
        errors.append('Cannot handle expression (unknown func %s): ' % str(expr.func) + str(expr))
    return errors, set(substitutions)


def get_symbols(expr, errors, debug=False):
    if debug:
        debug('Getting symbols from', expr.args)
    params = []
    for arg in expr.args:
        if arg.func == Symbol:
            params.append(str(arg))
        else:
            errors.append(str(expr) + ' contains a non-symbol: ' + str(arg))
    return params


def question_is_nonarray(questions, question_id):
    """
    Return whether the question exists and has no subquestions.
    """
    if question_id not in questions:
        return False
    question = questions[question_id]
    if question[1] is not None or question[2] is not None:
        return False
    return True


def check_subquestion_exists(subquestion, questions):
    """
    Return whether ``subquestion`` exists in ``questions``.

    Check existnece of questions id, match of dimensionality and
    existence of subquestions id (or ids in case 2 dimensions).
    """
    question_id = subquestion[0]
    if question_id not in questions:
        return False
    question = questions[question_id]
    # get required dimensionality
    dim_expected = 0
    if question[1] is not None:
        dim_expected = 1
    if question[2] is not None:
        dim_expected = 2
    # get dimensionality
    dim = len(subquestion) - 1
    # compare dimensionality
    if dim_expected != dim or dim == 0:
        return False
    # check if subquestion ids exists
    status = (subquestion[1] in question[1])
    if dim == 2:
        status &= (subquestion[2] in question[2])
    #print(status, dim_expected, dim, subquestion, question)
    return status


def get_answer_expression(response, questions, question_id):
    """
    Return the answer to a question from ``response``.
    """
    answer = response[question_id]
    return map_answer_expr(questions, question_id, answer)


def compare_question_answer(response, question_id, value):
    """
    Return whether a question has the required ``value``.

    Return a sympy boolean.
    """
    answer = response[question_id]
    return str(answer) == str(value)


def get_subquestion_answer(response, questions, subquestion):
    """
    Return the answer to a subquestion from ``response``.
    """
    question_id = subquestion[0]
    answers = response[question_id]
    dim = len(subquestion) - 1
    for answer in answers:
        matched = True
        if subquestion[1] != answer[0]:
            matched = False
        if dim == 2 and subquestion[2] != answer[1]:
            matched = False
        if matched:
            if dim == 1:
                answer = answer[1]
            else:
                answer = answer[2]
            return map_answer_expr(questions, question_id, answer)


def compare_subquestion_answer(response, questions, subquestion, value):
    """
    Return whether a ``subquestion`` has the required ``value``.

    Return a sympy boolean. If ``value`` is None (an empty answer),
    the comparison is always false.
    """
    if value is None:
        return false
    answer = get_subquestion_answer(response, questions, subquestion)
    return str(answer) == str(value)


def get_question_type(question_id, questions):
    """
    Return 'Number' or 'Boolean' depending on the question's type.
    """
    question = questions[question_id]
    question_class = question[0]
    if question_class in ('Y'):
        return 'Boolean'
    return 'Number'


def map_answer_expr(questions, question_id, answer):
    """
    Map an answer value to a sympy expression.

    Depending on the the question class we return an appropriate sympy
    expression. This will be a Number, True, False, or a symbol.
    If the answer was empty, we do not return a sympy expression,
    but None, or if the question_type is 'Number', then 0.
    """
    question_type = get_question_type(question_id, questions)
    if question_type == 'Boolean':
        return True if answer == 'Y' else False
    if question_type == 'Number' and answer == '':
        return 0
    try:
        number = float(answer)
        return Number(number)
    except:  # text answer
        if answer == '' or answer is None:
            return None
        else:
            return sympy.symbols(str(answer))


def validate(formula, questions, debug=False):
    """
    Check if the symbols in ``formula`` match the ``questions``.

    ``formula`` must be a string and expected to be a formula
    obtained from the composition rules stated in the module header.

    Check if all question and subquestion identifiers do exist
    in ``questions``. Subquestion identifiers are 2-tuples or
    3-tuples (if the array dimension is 1 or 2, respectively),
    where the 1st entry is the question id and the 2nd and
    possibly 3rd entry are the subquestion ids (usually s.t.
    like 'SQ001'). It is also checked whether the type (numeric
    or boolean) matches with what is expected (the whole formula
    is expected to yield a numeric expression).
    """
    if debug:
        debug('# Validating', formula)
    try:
        expr = sympy_parser.parse_expr(formula, local_dict=local_dict, evaluate=False)
    except Exception as e:
        return ['Error in basic parsing of this formula: %s : %s' % (formula, str(e))]
    try:
        errors, _ = parse_recursive(expr, questions, debug=debug)
    except Exception as e:
        return ['Error in parse_recursive for this formula: %s : %s' % (formula, str(e))]
    return errors


def evaluate(formula, questions, response, debug=False, debug_subs=False):
    """
    Calculate the value of the ``formula`` using ``responses`` to ``questions``.

    Return expression, value, errors, where expression is obtained
    from substituting answers from the response with their values
    and value is the float content of expression (None if expression
    is not a number). The errors are strings describing what went wrong,
    either while parsing or while substituting.
    """
    if debug:
        debug('# Evaluating', formula)
    try:
        expression = sympy_parser.parse_expr(formula, local_dict=local_dict, evaluate=False)
    except Exception as e:
        return None, None, ['Error in basic parsing of this formula: %s : %s' % (formula, str(e))]
    try:
        errors, substitutions = parse_recursive(expression, questions, response=response, debug=debug)
    except Exception as e:
        return None, None, ['Error in parse_recursive (with response) for this formula: %s : %s' % (formula, str(e))]
    # make substitutions
    for substitution in substitutions:
        try:
            if debug_subs:
                debug('# Substituting {} --> {}'.format(
                    str(substitution[0]), str(substitution[1])))
            if substitution[1] is None:
                return None, None, ['Error while substituting >>None<< for >>%s<<' % str(substitution[0])]
            expression = expression.subs(*substitution, simplify=False)
            if debug_subs:
                debug('# New expression', expression)
        except Exception as e:
            return None, None, ["Error while substituting '{}' -> '{}' into"\
                                " this expression: '{}' --- ERROR detail: {}".format(
                                str(substitution[0]), str(substitution[1]),
                                str(expression), str(e))]
    # get numeric content
    try:
        value = float(str(expression.evalf()))
    except:
        value = None
    return str(expression), value, errors


def debug(*args):
    if args:
        arg0 = args[0]
        arg0_formatted = (arg0 + ':').ljust(22)
        args_ = args[1:]
        print(arg0_formatted, *args_)


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print('Running with sample data. If you want to use live data,')
        print('please give a survey_id as arg1 and a formula as arg2.')
        print('It will use the "last" response.')
        print('Command example:  python formulas.py 545919 "CIRES1a * 3"')
        print()
        from tests.samples import get_sample_questions
        questions = get_sample_questions()
        from tests.samples import get_sample_response
        response = get_sample_response()
        responses = ({1: response}, {1:{}})
        formula = 'CIGOVX3 + 1 + 1.0*ITE(CIGOVX4, 1, 0) + (-1) * VAL(CIGOVX, SQ001, SQ005)/7 + 0.5*VAL(CIGOVX2, SQ001, SQ002) + (-8) * ITE(HASVAL(CIGOVX1, SQ001, SQ002, AY),7,17) * 9'
        formula = 'CIGOVX3 + 1 + 1.0*ITE(CIGOVX4, 1, 0) + 0.5*VAL(CIGOVX2 & (1 < 2), SQ001, SQ002) + (-8) * ITE(HASVAL(CIGOVX1, SQ001, SQ002abc, AY),7,17) * 9'
        #formula = 'CIGOVX4 + 1 + (CIGOVX3<=-10) + ITE(Eq(CIGOVX3,10), 1, 0) + 1.0*ITE(CIGOVX4, 1, 0) + 0.5*VAL(CIGOVX2, SQ001, SQ002) + (-1) * VAL(CIGOVX, SQ001abc, log(SQ005))/7 + (-8) * ITE(HASVAL(CIGOVX1, SQ001, SQ002abc, AY),7,17) * log(9)'
        #formula = 'LOG(9) + 7'
        #formula = 'ITE(Eq(CIGOVX3,7),1,0)'
        #formula = 'Abs(-1)'
        #formula = 'LEN(CIGOVX3)'
        #formula = 'ITE(1 > 0, 5, 1.2 / (CIGOVX3 - 7))'
        #formula = '1.2 / (CIGOVX3 - 7)'
    else:
        try:
            survey_id = int(float(sys.argv[1]))
        except:
            print('Invalid survey_id')
            sys.exit(1)
        formula = sys.argv[2]
        from .questions import get_questions
        questions = get_questions(survey_id, debug=False)
        from .responses import get_responses
        responses = get_responses(survey_id, debug=False)

    errors = validate(formula, questions, debug=debug)
    if errors:
        print('VALIDATION ERRORS:')
        for error in errors:
            print(error)
    elif responses:
        resp, resp_meta = responses
        for response_id, response in resp.items():
            #pprint(resp)
            #pprint(resp_meta)
            expr, value, errors = evaluate(formula, questions, response,
                                           debug=debug, debug_subs=True)
            debug('# RESULT', expr, value)
            if errors:
                print('ERRORS:')
                for error in errors:
                    print(error)
    else:
        print('Sorry, no responses.')
