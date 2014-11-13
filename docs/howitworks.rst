TODO: This document is quite raw. Needs improvement.

Form class needs to subclass from :class:`~django_superform.forms.SuperForm`
or :class:`~django_superform.forms.SuperModelForm`.

During instantiation:
* composite fields get initialized
* The fields ``get_form`` and ``get_formsets`` methods are called which
  instantiate the nested form/formset. They get the same data/files that are
  passed into the super form. Initial values are passed through. EXAMPLE.
* Those get attached into ``form.forms`` and ``form.formsets``.

In template you can get a bound field (like with django's normal form fields) with
{{ form.composite_field_name }}. Or you can get the real form instance with
``{{ form.forms.composite_field_name }}``, or the formset: ``{{
form.formsets.composite_field_name }}``.

Then when it gets to validation, the super form's ``full_clean()`` and
``is_valid()`` methods will clean and validate the nested forms/formsets as
well. So ``is_valid()`` will return ``False`` when the super form's fields are
valid but any of the nested forms/formsets is not.

Errors will be attached to ``form.errors``. For forms it will be a error dict,
for formsets it will be a list of the errors of the formset's forms.

On saving ``SuperModelForm``
----------------------------

The super form's ``save()`` method will first save the model that it takes
care of. Then the nested forms and then the nested formsets. It will only
return the saved model from the super form, but none of the objects from
nested forms/formsets. This is to keep the API to the normal model forms the
same.

The ``commit`` argument is respected and passed down. So nothing is saved to
the DB if you don't want it to. In that case, django forms will get a
dynamically created ``save_m2m`` method that can be called later on to then
save all the related stuff. The super form hooks in there to also save the
nested forms and formsets then (TODO: check, really?). And ofcourse it calls
their ``save_m2m`` methods :)

