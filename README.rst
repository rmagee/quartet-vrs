=============================
quartet_vrs
=============================

.. image:: https://gitlab.com/serial-lab/quartet_vrs/badges/master/coverage.svg
   :target: https://gitlab.com/serial-lab/quartet_vrs/pipelines
.. image:: https://gitlab.com/serial-lab/quartet_vrs/badges/master/build.svg
   :target: https://gitlab.com/serial-lab/quartet_vrs/commits/master
.. image:: https://badge.fury.io/py/quartet_vrs.svg
    :target: https://badge.fury.io/py/quartet_vrs

A GS1-compliant VRS interface for the open-source EPCIS QU4RTET platform.

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

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

