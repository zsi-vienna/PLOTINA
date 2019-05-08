# Setting up limesurvey

You will need a [limesurvey](https://www.limesurvey.org/) instance
with software version >=2.62.

In addition to being able to import and manage a survey you will need
a user account on this instance with the permission to use the JSON-API.

If you are administrator of the limesurvey instance, do the following:

Enable the JSON-API under 'Configuration' -> 'Global settings' -> 'Interfaces':

  * Choose 'RPC interface enabled': 'JSON-RPC'
  * Choose 'Publish API on /admin/remotecontrol': 'On'

Under 'Configuration' -> 'Manage Survey administrators'
create a user with permission 'Superadministrator'.

Note down the username and password of this user as well as the API-URL.
