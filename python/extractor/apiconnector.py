"""
Access limesurvey using its JSON-API.

Tested with limesurvey2.62.0+170124.

Throws LimeSurveyAPIError.

Capabilities:

  * get_session_key is called transparently
  * there is only a single method `query` and you have
    to supply the API method's name and the params
    (in the correct order!)

Usage:

Instantiate :class:`LimeSurveyAPIConnection` with the API URL and
credentials and use its :method:`query`. Note that you have to
supply the query params in the order shown in the API docs and
therefore use an OrderedDict (at least fo >1 params).

Unfortunately, the API documentation is scarce. If unsure, which
paramter values make sense, look into the corresponding column
of the respective database table.

See also:

 * https://github.com/axnsantana/python-limesurvey-rc/blob/master/pylimerc.py
 * https://github.com/psychopenguin/limesurvey
"""

import json
from collections import OrderedDict
import requests


class LimeSurveyAPIError(Exception):
    """
    Error related to :class:`LimeSurveyAPIConnection`.

    :class:`LimeSurveyAPIConnection` is designed to only raise
    this error.
    """

    def __init__(self, detail_text):
        self.detail_text = detail_text

    def __repr__(self):
        return self.detail_text


class LimeSurveyAPIConnection():
    """
    Connection to a LimeSurvey instance using JSON-RPC.

    The session key is obtained transparently when calling `query`.
    """

    def __init__(self, base_url=None, username=None, password=None):
        """
        Define a connection, but do not yet connect.

        The base_url should look like 'https://survey.example.com/index.php',
        i.e., including '/index.php'.

        The API users should have superuser permissions.
        """
        if base_url is None:
            msg = 'Programming error: missing LimeSurvey API URL'
            raise LimeSurveyAPIError(msg)
        if username is None or password is None:
            msg = 'Programming error: called with insufficient credentials'
            raise LimeSurveyAPIError(msg)
        self.base_url = base_url + '/admin/remotecontrol'
        self.username = username
        self.password = password
        self.headers = {
            'content-type': 'application/json',
            'connection': 'Keep-Alive',
        }
        self.session_key = None

    def query(self, method, params=None, id='1', debug=False):
        """
        Send a query to LimeSurvey and return the result.

        On error throw a :class:`LimeSurveyAPIError`.

        If *params* is not None or a dict with one key, then in order
        to guarantee the right order, *params* must be an OrderedDict.

        Internally, if we have no session key yet, we first issue an
        additional RPC for that.

        Use debug=True to get the JSON string sent to the server on
        stdout.
        """
        if self.session_key is None:
            self.get_session_key()
        if params is None:
            params = OrderedDict()
        if len(params.keys()) > 1 and not isinstance(params, OrderedDict):
            msg = 'Programming error: Method {} called with >1'\
                  ' params ({}) not being an OrderedDict'
            raise LimeSurveyAPIError(msg.format(method, params))
        status, reply = self.__query(method, params, id, debug=debug)
        if status is False or reply.get('error') is not None:
            msg = 'Method "{}" failed with params "{}"'
            raise LimeSurveyAPIError(msg.format(method, params))
        else:
            return reply.get('result')

    def get_session_key(self):
        """
        Get a session key.

        Automatically used in :method:`query` and not needed separately.
        Can however also be used separately.
        """
        success, reply = self.__query('get_session_key',
                                      [self.username, self.password],
                                      1, 
                                      add_session_key=False)
        if success:
            try:
                self.session_key = reply['result']
                return self.session_key
            except:
                msg = 'Cannot connect (get_session_key returned unexpected data)'
                LimeSurveyAPIError(msg)
        else:
            msg = 'Cannot connect (get_session_key failed)'
            raise LimeSurveyAPIError(msg)

    def __query(self, method, params, id, add_session_key=True, debug=False):
        try:
            if add_session_key:
                params1 = OrderedDict({'sSessionKey': self.session_key})
                params1.update(params)
                params = params1
            query = json.dumps({'method': method,
                                'params': params,
                                'id': id})
            if debug:
                print(query)
            response = requests.post(self.base_url,
                                     headers=self.headers,
                                     data=query)
            reply = response.json()
            return True, reply
        except Exception as e:
            return False, None

    def close(self):
        """
        Close the connection through releasing the session key.

        Throw LimeSurveyAPIError.
        """
        success, reply = self.__query('release_session_key',
                                      self.session_key,
                                      1,
                                      add_session_key=False)
        error = False
        if not success:
            error = True
        else:
            try:
                errors = reply.get('errors')
                if errors is not None:
                    error = True
            except:
                error = True
        if error:
            msg = 'Cannot release session_key'
            raise LimeSurveyAPIError(msg)
