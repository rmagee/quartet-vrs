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

Using the REST API
==================

You can access the VRS REST API as you would any standard REST API, over HTTP(S). Therefore, not only can you access
VRS in your code but you may also access VRS using your favorite tools such as Postman, SOAP UI, CURL, and others.

The two endpoints for QU4RTET VRS are defined below.

checkConnectivity
-----------------
The ``checkConnectivity`` method enables a check of connectivity with the QU4RTET Verification Service and returns
the appropriate HTTP status code. If the Requestor GLN (reqGLN) is not recognized, QU4RTET Verification Service will
respond with an HTTP 401 'Unauthorized' response. If the Requestor GLN (reqGLN) is not permitted to make requests,
the verification service will respond with an HTTP 403 'Forbidden' response.

The endpoint's signature is as follows:

.. code-block:: python

            http[s]://[host]:[port]/vrs/checkConnectivity?gtin=GTIN14&reqGLN=GLN13[&context=dscsaSaleableReturn]

For example:

.. code-block:: python

    https://someserver.qu4rtet.io/vrs/checkConnectivity?gtin=01234567890123&reqGLN=0123456789012

If the *gtin* and *reqGLN* are found in the QU4RTET open-source EPCIS System,
Then the following message will be returned:

.. code-block:: python

     # The 'GLN of Responder' will be a GS1 GLN-13 representing the entity verifying requests.
     {
        "responderGLN": "GLN of Responder"
     }

If the *gtin* and/or the *reqGLN* are not found then the response will return HTTP 401 Unauthorized status with no other
information.

verify
------
The ``verify`` method provides a verification of a Product Instance using the provided *GTIN14*, *Lot/Batch Number*,
and *Serial Number*. If any one of the aforementioned are not verified, the VRS will respond with an appropriate HTTP Status and
message.

The endpoint's signature is as follows:

.. code-block:: python

    http[s]://[host]:[port]/vrs/verify/gtin/{GTIN14}/lot/{LOT NUMBER]/ser/{SERIAL NUMBER}?exp={Expiry Date e.g. 190401}

For example:

.. code-block:: python

    https://someserver.qu4rtet.io/vrs/verify/gtin/01234567890123/lot/LOT456/ser/1ABCX1234?exp=220401

If the *GTIN14*, *Lot/Batch Number*, and *Serial Number* are verified, the following message will be returned:

.. code-block:: python

    {
        "verificationTimestamp": "2019-05-17T16:48:53.428Z",
        "responderGLN": "GLN of Responder",
        "data": {"verified": true},
        "corrUUID": ""
    }

Note the empty Correlation ID field ``corrUUID``. This field will only contain a value if the Correlation ID is
provided as part of the query parameters of the verify request. For example:

.. code-block:: python

     https://someserver.qu4rtet.io/vrs/verify/gtin/01234567890123/lot/LOT456/ser/1ABCX1234?exp=220401&corrUUID=21EC2020-3AEA-4069-A2DD-08002B30309D

In the above example the Correlation ID will be returned in the response.

.. code-block:: python

    {
        "verificationTimestamp": "2019-05-17T16:48:53.428Z",
        "responderGLN": "GLN of Responder",
        "data": {"verified": true},
        "corrUUID": "21EC2020-3AEA-4069-A2DD-08002B30309D"
    }

When the provide Product Instance Data cannot be verified, a message will be returned stating the reason the verification failed.

For example:

.. code-block:: python

    {
        "verificationTimestamp": "2019-05-17T16:48:53.428Z",
        "responderGLN": "GLN of Responder",
        "data": {
            "verified": false,
            "verificationFailureReason": "VERIFICATION_CODE_GTIN_SERIAL"
        },
        "corrUUID": "21EC2020-3AEA-4069-A2DD-08002B30309D"
    }
