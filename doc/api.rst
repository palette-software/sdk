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
      Content-Type: text/javascript

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

**Allowable actions:**

* *start* - start the Tableau Server
* *stop* - stop the Tableau Server
* *restart* - restart the Tableau Server
* *repair-license* - equivalent to 'tabadmin licenses --repair_service'
* *ziplogs* - cleanup Tableau Server logs
   
