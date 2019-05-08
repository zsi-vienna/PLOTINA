from pprint import pprint
from collections import defaultdict, OrderedDict
from .limesurvey import get_raw_questions


def get_questions(survey_id, debug=False):
    raw_questions = get_raw_questions(survey_id)
    if debug:
        print('_' * 40, 'raw questions')
        pprint(raw_questions)
    return parse_questions(raw_questions, debug=debug)


def parse_questions(raw_questions, debug=False):
    """
    Get a mapping of question titles (qid) to details.
    """
    questions = {}
    p_c, c_p = get_question_relations(raw_questions, debug=debug)
    # 1st loop for parent questions only
    for question in raw_questions:
        qid = str(question['qid'])
        if qid in c_p and c_p[qid] == '0':
            q_class = question['type']
            title = question['title']
            questions[qid] = [q_class, None, None, title]
    # 2nd loop for subquestions only
    for question in raw_questions:
        qid = str(question['qid'])
        if c_p[qid] != '0':
            title = question['title']
            scale_id = str(question['scale_id'])
            parent_id = str(question['parent_qid'])
            if scale_id == '0':
                if questions[parent_id][1] is None:
                    questions[parent_id][1] = [title]
                else:
                    questions[parent_id][1].append(title)
            if scale_id == '1':
                if questions[parent_id][2] is None:
                    questions[parent_id][2] = [title]
                else:
                    questions[parent_id][2].append(title)
    res = {questions[qid][3]: tuple(questions[qid][:3]) for qid in questions}
    if debug:
        print('_' * 40, 'suitably restructured question data')
        pprint(res)
    return res


def get_question_relations(raw_questions, debug=False):
    """
    Return 2 dicts: 1) parent to childs, 2) child to parent.
    """
    q_parent_childs = defaultdict(list)
    q_child_parent = {}
    for question in raw_questions:
        child_id = str(question['qid'])
        parent_id = str(question['parent_qid'])
        q_parent_childs[parent_id].append(child_id)
        q_child_parent[child_id] = parent_id
    if debug:
        print('_' * 40, 'parent_childs')
        pprint(q_parent_childs)
        print('_' * 40, 'child_parent')
        pprint(q_child_parent)
    return q_parent_childs, q_child_parent


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Please give a survey_id as arg1.')
        sys.exit(1)
    try:
        survey_id = int(float(sys.argv[1]))
    except:
        print('Invalid survey_id')
        sys.exit(1)
    qs = get_questions(survey_id, debug=True)
    pprint(qs)
