.. _api:

REST API
********

Authentication
==============

.. http:post:: /login/authenticate
   
   Generate an 'auth_tkt' cookie to use with subsequent requests.

   :form username: (required) username
   :form password: (required) password
   :status 302: the redirect indicates successful authentication
   :status 400: missing form parameters
   :status 403: invalid username or password
   :resheader Set-Cookie: contains an 'auth_tkt' cookie on success


State
=====

.. http:get:: /api/v1/state

   Return the current environment state.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1/state
      Host: example.palette-software.net
      Cookie: auth_tkt=<value>

   **Example response**

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "OK",
	"state": "RUNNING"
      }

   :reqheader Cookie: the auth_tkt returned from authentication.
   :statuscode 200: OK
   :statuscode 403: authentication is required (any level)

Manage
======

.. http:post:: /api/v1/manage
      
   Control of the Tableau Server.

   :form action: (required) the desired action (see below)
   :type action: str
   :form sync: (optional) synchronous request
   :type sync: bool
   :reqheader Cookie: the auth_tkt returned from authentication.
   :statuscode 200: OK
   :statuscode 400: the required form parameter 'action' is missing.
   :statuscode 403: authentication is required (Manager or Super Admin)

   **Example response**

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "OK",
      }

   **Allowable actions:**

   * *start* - start the Tableau Server
   * *stop* - stop the Tableau Server
   * *restart* - restart the Tableau Server
   * *backup* - create a Tablea Server backup
   * *repair-license* - equivalent to 'tabadmin licenses --repair_service'
   * *ziplogs* - cleanup Tableau Server logs


Backups
=======

.. http:get:: /api/v1/backups

   Retrieve a limited list about all existing backups.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1/backups?limit=2
      Host: example.palette-software.net
      Cookie: auth_tkt=<value>

   **Example response**

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "OK",
        "backups": [
          {
            "id": 8,
            "uri": "file://hostname/path/to/tableau-backups/20150914_140501.tsbak",
            "size": 6594394,
            "creation-time": "2015-09-14T21:06:11.776708Z"
          },
          {
            "id": 7,
            "uri": "s3://bucket/tableau-backups/20150914_140327.tsbak",
            "size": 6594292,
            "creation-time": "2015-09-14T21:04:38.180478Z"
          }
        ]
      }

   :query desc: (optional) sort in descending order (default=True)
   :query limit: (optional) maximum number of backups to return.
   :reqheader Cookie: the auth_tkt returned from authentication.
   :statuscode 200: OK
   :statuscode 403: authentication is required (Readonly, Manager or Super Admin)

.. http:get:: /api/v1/backups/(int:backup_id)

   Retrieve the information about a particular backup.

   **Example request**:

   .. sourcecode:: http

      GET /api/v1/backups/8
      Host: example.palette-software.net
      Cookie: auth_tkt=<value>

   **Example response**

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "status": "OK",
        "id": 8,
        "uri": "file://hostname/path/to/tableau-backups/20150914_140501.tsbak",
        "size": 6594394,
        "creation-time": "2015-09-14T21:06:11.776708Z"
      }

   :reqheader Cookie: the auth_tkt returned from authentication.
   :statuscode 200: OK
   :statuscode 403: authentication is required (Readonly, Manager or Super Admin)
   :statuscode 404: the requested backup does not exist.
