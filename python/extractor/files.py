"""
Read and write files in 'results' directory.

Import indicator definitions and indicator descriptions.

Export extraction results (errors, indicator definitions, responses, indicator values).
"""

from os import path
import json


results_dir = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'results')


def get_indicator_definitions():
    filepath = path.join(results_dir, 'indicator_definitions.hjson')
    with open(filepath, 'r') as file:
        contents = file.read()
    return contents


def write_file(filename, contents):
    with open(path.join(results_dir, filename), 'w') as file:
        file.write(contents)


def export_full(results):
    write_file('full.json', json.dumps(results, indent=4, sort_keys=True))


def export_indicator_values(indicator_values):
    write_file('indicator_values.json', json.dumps(indicator_values, indent=4, sort_keys=True))


def get_indicator_descriptions():
    try:
        filepath = path.join(results_dir, 'indicator_descriptions.json')
        with open(filepath, 'r') as file:
            contents = file.read()
        return json.loads(contents)
    except Exception as err:
        print(str(err))


def get_response_dates(responses):
    response_dates = {}
    for response_id, response in responses.items():
        if response.get('Date'):
            response_dates[response_id] = response.get('Date')[:10]
    return response_dates


def export_visualization_data(results):
    """
    Export the visualization data file, ``visualization_data.json``.

    Collect one list per indicator which contains indicator values
    together with dates (from results where they are grouped by
    responses).
    """
    responses = results['responses']
    response_dates = get_response_dates(responses)
    indicator_descriptions = get_indicator_descriptions()
    results = results['results']
    # get a set of valid indicators (those with value not None)
    # for each response and put them in a list
    indicator_names_sets = [
        set([ind for ind, d in results[response_id].items() if d['value'] is not None])
    for response_id in results]
    # get common valid indicators (over all responses)
    valid_indicator_names = set.intersection(*indicator_names_sets)
    # collect information per indicator
    res = {}
    for ind_name in valid_indicator_names:
        try:
            title = indicator_descriptions[ind_name]['title']
        except:
            title = 'Missing title for indicator {}'.format(ind_name)
        try:
            desc = indicator_descriptions[ind_name]['desc']
        except:
            desc = 'Missing description for indicator {}'.format(ind_name)
        try:
            doc_page = indicator_descriptions[ind_name]['doc_page']
        except:
            doc_page = None
        data = []
        for response_id, inds in results.items():
            value = inds[ind_name]['value']
            date_ = response_dates[response_id]
            data.append({
                'date': date_,
                'value': value,
            })
        data.sort(key=lambda x: x['date'])
        data_new = []
        for m, data_point in enumerate(data):
            data_point['m'] = m + 1
            data_new.append(data_point)
        res[ind_name] = {
            'data': data_new,
            'title': title,
            'description': desc,
            'url': 'assets/data/PLOTINA_indicators.pdf#page=' + str(doc_page) if doc_page else None,
        }
    write_file('visualization_data.json', json.dumps(res, indent=4, sort_keys=True))


def export_all(results):
    export_full(results)
    indicator_values = results['results']
    export_indicator_values(indicator_values)
    export_visualization_data(results)
