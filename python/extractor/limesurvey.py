"""
Provide a limesurvey instance and accessors for questions and responses.
"""

import json
import base64
from os import path, pardir
from collections import OrderedDict
from pprint import pprint
from .apiconnector import LimeSurveyAPIConnection


def get_ls_instance():
    dir_path = path.join(path.dirname(path.abspath(__file__)), pardir)
    with open(path.join(dir_path, 'config.json'), 'r') as creds_file:
        lsconf = json.load(creds_file)

    ls_instance = LimeSurveyAPIConnection(
        base_url=lsconf['lsurl'],
        username=lsconf['username'],
        password=lsconf['password']
    )
    return ls_instance


def get_raw_questions(survey_id, debug=False):
    """
    Return a raw list of questions for a specific survey.

    :param survey_id: the specific survey's ID
    :param debug: set True for printing the query
    :return: a dict containing all questions asked in the survey
    """
    questions = ls_instance.query('list_questions',
                                  OrderedDict([('iSurveyID', survey_id), ]),
                                  debug=debug)
    if not isinstance(questions, list):
        print(questions.get('status'))
        questions = []
    return questions


def get_completed_raw_responses(survey_id, debug=False, debug_conn=False):
    """
    Retrieve all completed responses of a survey - if there are any.

    .. note:: May return None.

    :param ls_instance: a LimeSurvey instance, cf. :mod:`limesurvey`
    :param survey_id: the specific survey's id
    :type survey_id: str or int
    :param debug: enable debugging query results
    :type debug: bool
    :param debug_conn: enable LS API connection debugging
    :type debug_conn: bool
    :returns: list of completed raw responses, or None
    :rtype: list or None
    """
    # check for summary - summary is only given if there are results
    # (incl. incomplete responses)
    summary = ls_instance.query('get_summary',
                                OrderedDict([
                                    ('iSurveyID', str(survey_id)),
                                    ('sStatname', 'all'),
                                ]),
                                debug=debug)
    if debug:
        print('_'*60, 'Summary')
        pprint(summary)
    if summary:
        if int(float(str(summary.get('completed_responses', 0)))) > 0:
            responses = ls_instance.query(
                'export_responses',
                OrderedDict([
                    ('iSurveyID', survey_id),
                    ('sDocumentType', 'json'),
                    ('sLanguageCode', 'en'),
                    ('sCompletionStatus', 'all'),
                    ('sHeadingType', 'short'),
                    ('sResponseType', 'short'),
                    ('aFields', None),
                ]),
                debug=debug)
            # LS results are returned as base64 encoded string
            result_json_utf8 = base64.b64decode(responses)
            result_json = result_json_utf8.decode('utf-8')
            result = json.loads(result_json)
            return result.get('responses')


ls_instance = get_ls_instance()
