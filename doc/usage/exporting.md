# Data export (preparing the visualization)

You find the python scripts in directory 'python'.
The files in this directory are meant to extract the data
required for visualization from a survey running on
a LimeSurvey instance.

The LimeSurvey instance has to have an enabled JSON-RPC API.


## Setup

Prepare a virtualenv with python >= 3.4:

    virtualenv -ppython3 plotina
    cd plotina
    source bin/activate

Get the source:

    mkdir repo
    cd repo
    git clone https://gitlab.zsi.at/web/plotina.git .
    cd python
    pip install -r requirements.txt

Put limesurvey API credentials into 'config.json'
(use 'config.json__sample' as template).


## Testing

Next you can run a number of tests to check functionality:

Unittests:

    python -m tests.test_formulas

Formula parsing (with debug output):

    python -m extractor.formulas

Check limesurvey connection:

    python -m extractor.limesurvey

Check if the questions of a survey are correctly retrieved
(needs a survey_id and produces some output):

    python -m extractor.questions <SURVEY_ID>

Check if the responses of a survey are correctly retrieved
(needs a survey_id and produces some output):

    python -m extractor.responses <SURVEY_ID>

Check if the indicators are correctly checked for a survey:

    python -m extractor.indicators <SURVEY_ID> <FORMULA>

<FORMULA> could f.i. be

    "IND1: VAL(CIREC1, Proj1, F)*7"

which means the value of subquestion "Proj1" (Y-scale) and
subquestion "F" (X-scale) of question "CIREC1" times 7 is
being defined as indicator "IND1".


## Extraction

To extract data start the server like this:

    python -m extractor.server <SURVEY_ID> <PORT>

<PORT> is the TCP port number on which the server will run, f.i. 8000.

Ensure that the user running the above python command has write
permissions in directory 'python/results' and on all files therein.

Before using the webserver in the next step, please check that
python/results/indicator_descriptions.json contains information
for all indicators to be displayed in the visualization. The title
and description are mandatory, while doc_page is the page number
in the PLOTINA indicator manual, which obviously does not contain
your self-defined indicators and thus can have a value of null.

Next use the webinterface at:

    http://127.0.0.1:<PORT>

You will see a text field where you can paste the indicator formulas.
If you haven't changed indicators, you can use the default definitions.
See [indicators.md](indicators.md) for an explanation on how to define
indicators.

The validity of the indicator definitions will be checked upon submit.
If there were errors they are displayed below the form.

When you have entered valid indicators you will see a list of response
ids (provided you have at least one completed response in the limesurvey)
together with a datetime. Select those responses which you want to appear
in the visualization. The visualization will display the time development
of indicators, so you will want to select more than one response.
Note: The datetime displayed besides the response_id refers to the instant
when the response was entered into LimeSurvey, not to the instant of
validity of the entered statistical data (which is part of the survey
itself, namely in the first question).

The next view may take a few minutes to generate. It shows you the
results, in particular the errors which occurred when trying to
evaluate the indicator formulas. With the default indicators no error
should occur. If an error occurred, this means that not all indicators
have been calculated correctly and you must go back and change the formulas
or take care that questions (if you have changed them) have been answered,
because missing values can also lead to errors.

The results are not only displayed, but also written to files, namely in
directory 'python/results'. From there you will need 'visualization_data.json'
for the visualization. You also find 'indicator_definitions.json' there,
which contains the default version of the indicators. If you have changed
the indicators and want them to be displayed by default, you can change this
file.
