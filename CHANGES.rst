Changelog
=========

0.3.1
-----

* ``SuperForm.composite_fields`` dict is not longer shared between form
  instances. Every new form instances get's a deep copy. So changes to it
  won't leak into other instances of the same form class.

0.3.0
-----

* `#11`_: Fix ``CompositeBoundField`` to allow direct access to nested form
  fields via ``form['nested_form']['field']``.
* Support for Django's Media handling in nested forms. See `#3`_ and `#5`_.
* Do not populate errorlist representations without any errors of nested
  formsets into the errors of the super form. See `#5`_ for details.

.. _#3: https://github.com/gregmuellegger/django-superform/issues/3
.. _#5: https://github.com/gregmuellegger/django-superform/pull/5
.. _#11: https://github.com/gregmuellegger/django-superform/issues/11

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
