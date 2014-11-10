Fields
======

This is the class hierachy of all the available composite fields to be used in
a ``SuperForm``::

    + CompositeField
    |
    +-+ FormField
    | |
    | +-+ ModelFormField
    |   |
    |   +-- ForeignKeyFormField
    |
    +-+ FormSetField
      |
      +-+ ModelFormSetField
        |
        +-+ InlineFormSetField

``CompositeField``
------------------

.. autoclass:: django_superform.fields.CompositeField
    :members: get_prefix, get_initial, get_kwargs

``FormField``
-------------

.. autoclass:: django_superform.fields.FormField
    :members: get_form_class, get_form

``ModelFormField``
------------------

.. autoclass:: django_superform.fields.ModelFormField
    :members: get_instance, get_kwargs, shall_save, save

``ForeignKeyFormField``
-----------------------

.. autoclass:: django_superform.fields.ForeignKeyFormField

``FormSetField``
----------------

.. autoclass:: django_superform.fields.FormSetField

``ModelFormSetField``
---------------------

.. autoclass:: django_superform.fields.ModelFormSetField

``InlineFormSetField``
----------------------

.. autoclass:: django_superform.fields.InlineFormSetField
