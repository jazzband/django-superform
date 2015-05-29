Changelog
=========

0.3.0 (in development)
----------------------

* Support for Django's Media handling in nested forms. See `#3`_ and `#5`_.

.. _#3: https://github.com/gregmuellegger/django-superform/issues/3
.. _#5: https://github.com/gregmuellegger/django-superform/pull/5

0.2.0
-----

* Django 1.8 support.
* Initial values given to the ``__init__`` method of the super-form will get
  passed through to the nested forms.
* The ``empty_permitted`` argument for modelforms used in a ``ModelFormField``
  is set depending on the ``required`` attribute given to the field.

0.1.0
-----

* Initial release with proof of concept.
