from django import forms
from django.forms.forms import ErrorList
from django.forms.formsets import formset_factory
from django.test import TestCase
from django_superform import SuperForm, FormField


class AddressForm(forms.Form):
    street = forms.CharField()
    city = forms.CharField()


class RegistrationForm(SuperForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    address = FormField(AddressForm)


class FormFieldTests(TestCase):
    def test_is_in_composite_fields(self):
        superform = RegistrationForm()
        self.assertTrue('address' in superform.composite_fields)

    def test_is_in_forms_attr(self):
        superform = RegistrationForm()
        self.assertTrue('address' in superform.forms)
        self.assertTrue(isinstance(superform.forms['address'], AddressForm))

    def test_form_prefix(self):
        superform = RegistrationForm()
        form = superform.forms['address']
        self.assertEqual(form.prefix, 'form-address')

    def test_field_name(self):
        superform = RegistrationForm()
        boundfield = superform.forms['address']['street']
        self.assertEqual(boundfield.html_name, 'form-address-street')

        superform = RegistrationForm(prefix='registration')
        boundfield = superform.forms['address']['street']
        self.assertEqual(boundfield.html_name, 'registration-form-address-street')
