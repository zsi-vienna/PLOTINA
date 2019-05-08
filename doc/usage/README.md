# PLOTINA GEP assessment tool: Installation and usage

The PLOTINA tool for assessing gender equality plans over time
allows to enter and visualize data to assess GEPs.

The following instructions are for technical personnel, i.e.,
system administrators or advanced users who are not afraid of the
command line and know how to put content on a webserver.

Please take the following steps if you want to use the PLOTINA tool
(cf. [architecture.svg](architecture.svg)):

  * Prepare a limesurvey instance. For details cf.
    [limesurvey.md](limesurvey.md) .

  * Import the limesurvey and invite a colleague having the statistical
    information related to gender equality to fill in the survey.
    For details cf. [survey.md](survey.md).

  * When the colleague has finished, export the results using
    the python scripts. This will give you a JSON file containing
    all information required for the visualization. For details
    cf. [exporting.md](exporting.md).

  * Put the JSON file (visualization_data.json) together with the
    visualization code on a webserver. For details cf.
    [visualization.md](visualization.md).

  Whenever you want to add updated data, create a new token for a survey
  participant and repeat the last two steps.

  You can change the survey structure as well as the indicators to be
  shown in the visualization, but you cannot display data points
  together in one visualization which correspond to different sets of
  indicators.
