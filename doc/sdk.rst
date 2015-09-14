.. _sdk:

Python SDK
**********

The Python SDK is currently the only SDK officially supported by Palette 
Software.
Of course, the :ref:`api` may be called directly from any language.

.. _python-quickstart:

Quickstart
==========

.. _python-api-reference:

API Reference
=============

.. autofunction:: palette.connect

The ``palette`` module
----------------------

.. autoclass:: palette.PaletteServer
   :members:

``palette.backup``
------------------

.. autoclass:: palette.backup.Backup
   :members:
   :exclude-members: from_json

Exception classes (``palette.error``)
-------------------------------------

.. automodule:: palette.error
   :members:
