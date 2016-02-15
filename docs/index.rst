django-superform: nest all the forms!
=====================================

A ``SuperForm`` lets you nest other forms and formsets inside a form. That way
handling multiple forms on one page gets *super* easy and you can finally use
forms for complex scenarios without driving insane.

This is how a nested form looks:

.. code-block:: python

    from django import forms
    from django.forms import formset_factory
    from django_superform import SuperForm, FormField, FormSetField

    class EmailForm(forms.Form):
        email = forms.EmailField()

    class AddressForm(forms.Form):
        street = forms.CharField()
        city = forms.CharField()

    class UserProfile(SuperForm):
        username = forms.CharField(max_length=50)
        address = FormField(AddressForm)
        emails = FormSetField(formset_factory(EmailForm))

``django-superform`` also works well with model forms and inline model form sets.

After you have :doc:`installed <install>` django-superform, continue with
the :doc:`quickstart guide <quickstart>` to see how to use it in your project.

**Contents:**

.. toctree::
    :maxdepth: 2

    install
    quickstart
    forms
    fields
    howitworks
    changelog

:ref:`genindex` | :ref:`modindex` | :ref:`search`
