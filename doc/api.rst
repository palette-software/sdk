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
      
