=====
Usage
=====

To use quartet_vrs in a project, add it to your `INSTALLED_APPS`:

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
