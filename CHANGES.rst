Changelog
=========

0.2.0 (not released yet)
------------------------

* Initial values given to the ``__init__`` method of the super-form will get
  passed through to the nested forms.
  See: http://django-superform.readthedocs.org/en/latest/fields.html#formfield
* The ``empty_permitted`` argument for modelforms used in a ``ModelFormField``
  is set depending on the ``required`` attribute given to the field.

0.1.0
-----

* Initial release with proof of concept.
