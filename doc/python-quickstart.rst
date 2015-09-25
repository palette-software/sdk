.. _python-quickstart:

Quickstart
==========

Installation
------------

::

   sudo -H pip install http://downloads.palette-software.com/sdk/palette-0.0.0.tar.gz

Create a file name ~/.palette with the following information:

.. code-block:: ini

   [Credentials]
   username = <username>
   password = <password>

where `<username>` and `<password>` are replace with the corresponding values.

.. warning::

   Ensure that the `~/.palette` file is only accessibly by the owner e.g. has file mode 0600 on Unix.

Usage
-----

.. code-block:: python

   import palette
   server = palette.connect('https://example.palette-software.net')

The resulting `server` object is an instance of ``PaletteServer`` which is
the basis for the entire SDK.

See the :ref:`python-api` for further information.

Logging
-------

The API logs information to a standard Python logger named `palette`.

.. code-block:: python

   import logging
   logger = logging.getLogger('palette')
   logger.addHandler(logging.StreamHandler())
   logger.setLevel(logging.DEBUG)

The above sample code will log everything that the 'palette' package does to
standard error, including printing the data sent and received by the web API.
