"""
Retrieve responses from a limesurvey.

The main function for external use is :func:`get_responses`.
It returns the responses for a survey in a suitable data structure,
see :func:`parse_raw_responses` for details.
"""

from collections import OrderedDict
from .limesurvey import get_completed_raw_responses


def get_responses(survey_id, debug=False):
    """
    Return survey responses in a format useful for our purposes.

    If responses cannot be retrieved and parsed, return None.
    """
    raw_responses = get_completed_raw_responses(survey_id, debug=debug)
    if raw_responses:
        return parse_raw_responses(raw_responses)


def parse_raw_responses(raw_responses):
    """
    Convert responses to a format useful for our purposes.

    Separate response data from response metadata.
    Return both as dictionaries where the keys are the response_ids
    (of type int).

    :param raw_responses: list of raw responses as obtained from
                          :func:`limesurvey.get_completed_raw_responses`
    :returns: 2-tuple (responses, resp_meta)
    :rtype: tuple

    :Example:

    responses might be a dict like this:
     {
         271: {'AY1': 'B5',
               'AY2': 'A1',
               'ICT1': [('SQ001', '6'), ('SQ002', '7'), ('SQ003', '3')],
               'ICT2': [('SQ001', 'SQ001', '91'), ('SQ001', 'SQ002', '99'),
                        ('SQ002', 'SQ001', '73'), ('SQ001', 'SQ002', '11')]
              },
         272: {'AY1': 'B6',
     .......

    :Example:

    resp_meta might be a dict like this:
     {
         271: {'datestamp': '2016-02-18 11:48:15',
               'id': 271,
               'lastpage': 3,
               'startdate': '2016-02-18 11:47:50',
               'startlanguage': 'en',
               'submitdate': '2016-02-18 11:48:15'},
     .......
    """
    responses = {}
    resp_meta = {}
    for raw_response in raw_responses:
        response_id = list(raw_response.keys())[0]
        resp_attrs = raw_response[response_id]
        response, meta = parse_response_attributes(resp_attrs)
        responses[int(float(response_id))] = response
        resp_meta[int(float(response_id))] = meta
    return responses, resp_meta


def parse_response_attributes(resp_attrs):
    """
    Collect data from a single response in a suitable format.
    """
    blacklist = ('datestamp', 'id', 'lastpage', 'refurl', 'token',
                 'startdate', 'startlanguage', 'submitdate')
    res = {}
    meta = {}
    for field, value in resp_attrs.items():
        if field in blacklist:
            meta[field] = value
        else:
            #print(field, value)
            qid, sqid1, sqid2 = parse_field(field)
            #print(qid, sqid1, sqid2)
            # prepare val to be stored in res
            if sqid1 == None and sqid2 == None:
                val = value
            elif sqid2 == None:
                val = (sqid1, value)
            else:
                val = (sqid1, sqid2, value)
            if qid not in res:
                if isinstance(val, tuple):
                    res[qid] = [val]
                else:
                    res[qid] = val
            else:
                if isinstance(val, tuple):
                    res[qid].append(val)
                else:
                    print('ERROR while parsing responses: This should not occur:', field, value, qid, sqid1, sqid2)
    return res, meta                    


def parse_field(field):
    """
    Parse a non-meta key from the response attributes dict.

    The non-meta keys correspond to (sub-)question titles ((s)qid).
    If the field name contains no brackets ('[', ']'), a qid without
    subquestions is meant. Otherwise one or two sqids are within the
    brackets: two if there is a '_' (separating them) within the
    brackets, and one otherwise.

    Return (qid, sqid1, sqid2) where sqid2 (subquestion_id in dim1)
    or sqid2 and sqid1 may be None, i.e., we have these possibilities:

      * some_qid, None, None
      * some_qid, some_sqid1, None
      * some_qid, some_sqid1, some_sqid2
    """
    if not '[' in field:
        return field, None, None
    if not '_' in field:
        qid, sqid1 = field.split('[', 1)
        return qid, sqid1.rstrip(']'), None
    qid, sqids = field.split('[', 1)
    sqids = sqids.rstrip(']')
    sqid1, sqid2 = sqids.split('_', 1)
    return qid, sqid1, sqid2


def get_response_ids_submitdates(resp_meta, debug=False):
    """
    Return a dict mapping response ids to submitdates.

    response ids are of type int, submitdates of type str.

    :param resp_meta: dict mapping response ids to a dict
                      with meta information,
                      cf. :func:`get_responses`
    """
    res = {}
    for id, meta_info in resp_meta.items():
        submitdate = meta_info.get('submitdate', 'Unknown')
        res[id] = submitdate
    return res


if __name__ == '__main__':
    import sys
    from pprint import pprint
    if len(sys.argv) < 2:
        print('Please give a survey_id as arg1.')
        sys.exit(1)
    try:
        survey_id = int(float(sys.argv[1]))
    except:
        print('Invalid survey_id')
        sys.exit(1)
    res = get_responses(survey_id, debug=True)
    if res:
        responses, resp_meta = res
        pprint(responses)
        pprint(resp_meta)
    else:
        print('Sorry, no responses or inexistent survey.')
