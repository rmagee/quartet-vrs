===================================
QU4RTET Verification Router Service
===================================

.. image:: https://gitlab.com/serial-lab/quartet_vrs/badges/master/coverage.svg
   :target: https://gitlab.com/serial-lab/quartet_vrs/pipelines
.. image:: https://gitlab.com/serial-lab/quartet_vrs/badges/master/build.svg
   :target: https://gitlab.com/serial-lab/quartet_vrs/commits/master
.. image:: https://badge.fury.io/py/quartet_vrs.svg
    :target: https://badge.fury.io/py/quartet_vrs

A GS1-compliant VRS interface for QU4RTET, the open-source EPCIS  platform.
===========================================================================

Documentation
-------------

The full documentation is at https://serial-lab.gitlab.io/quartet_vrs/

Quickstart
----------

Install quartet_vrs::

    pip install quartet_vrs

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'quartet_vrs.apps.QuartetVrsConfig',
        ...
    )

Add quartet_vrs's URL patterns:

.. code-block:: python

    from quartet_vrs import urls as quartet_vrs_urls


    urlpatterns = [
        ...
        url(r'^', include(quartet_vrs_urls)),
        ...
    ]

Features
--------

- REST API
- Open API Schema
- Implements the full Global Lightweight Messaging Standard v1.0.2
- Provides ``checkconnectivty`` endpoint.
- Provides ``verify`` endpoint.

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

