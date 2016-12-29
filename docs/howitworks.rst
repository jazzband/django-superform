How it works
============

All super forms try to transparently handle the nested forms so that you can
still expect the form to work in all generic usecases, like using the form with
a class based view and similiar situations.

It might still be useful to understand what is happening under the hood though.
It will help to know what places to look into if something is not working for
you as expected.

So here is a description of the life cycle of a super form and its composite
fields.

On form instantiation
---------------------

When instantiating the form, the composite fields get initialized. The
initialization will instantiate the nested forms and formsets.

So when creating a super form instance like ``PersonForm()``, it will loop over
all composite fields and call their ``get_form()`` and ``get_formset`` methods.

These methods will instantiated the nested forms. The nested forms and formsets
will then be stored in the ``forms`` and ``formsets`` dictionaries on the super
form. Using the ``PersonForm`` from above this will be inspectable like this in
the code:

.. code:: python

    form = PersonForm()
    form.forms['social_accounts']  # This is an instance of SocialAccountsForm.
    form.formsets['addresses']     # This is a formset instance containing
                                   # multiple AddressForms.

Validating the form
-------------------

TODO: Refine.

Then when it gets to validation, the super form's ``full_clean()`` and
``is_valid()`` methods will clean and validate the nested forms/formsets as
well. So ``is_valid()`` will return ``False`` when the super form's fields are
valid but any of the nested forms/formsets is not.

Errors will be attached to ``form.errors``. For forms it will be a error dict,
for formsets it will be a list of the errors of the formset's forms.

Saving model forms
------------------

The super form's ``save()`` method will first save the model that it takes
care of. Then the nested forms and then the nested formsets. It will only
return the saved model from the super form, but none of the objects from
nested forms/formsets. This is to keep the API to the normal model forms the
same.

The ``commit`` argument is respected and passed down. So nothing is saved to
the DB if you don't want it to. In that case, django forms will get a
dynamically created ``save_m2m`` method that can be called later on to then
save all the related stuff. The super form hooks in there to also save the
nested forms and formsets then. And ofcourse it calls their ``save_m2m``
methods :)

In the template
---------------

TODO. How to use the composite bound fields. How to display errors.

In template you can get a bound field (like with django's normal form fields) with
{{ form.composite_field_name }}. Or you can get the real form instance with
``{{ form.forms.composite_field_name }}``, or the formset: ``{{
form.formsets.composite_field_name }}``.
