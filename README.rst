The buggie bug database
=======================

buggie is a bug database designed for use as an example with the "Introduction
to RESTful-ish Web Services" presentation


Preparation
-----------

Run the following on Linux/OSX::
  virtualenv env_buggie
  source env_buggie/bin/activate
  pip install -R requirements.txt

Run the following on Windows::
  virtualenv env_buggie
  test_env\Scripts\activate
  pip install -R requirements.txt



Running the Dev Server
----------------------

Run the following::

  python runapp.py


Interfacing with the API
------------------------

Using httpie (installed with deps)::

  http get http://127.0.0.1:5000/users

You should get:

.. code-block:: bash

  $ http GET http://127.0.0.1:5000/users
  HTTP/1.0 200 OK
  Content-Length: 93
  Content-Type: text/html; charset=utf-8
  Date: Tue, 27 May 2014 19:47:34 GMT
  Server: Werkzeug/0.9.4 Python/2.7.5

  [{"username": "joebob", "timezone": -6, "active": true, "id": 1, "email": "joebob@nowor.ky"}]
