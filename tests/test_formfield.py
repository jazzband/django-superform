from django import forms
from django.test import TestCase
from django_superform import SuperForm, FormField


class AddressForm(forms.Form):
    street = forms.CharField()
    city = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.custom_attribute = kwargs.pop('custom_kwarg', None)
        super(AddressForm, self).__init__(*args, **kwargs)


class MultiAddressForm(SuperForm):
    address1 = FormField(AddressForm)
    address2 = FormField(AddressForm)


class RegistrationForm(SuperForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    address = FormField(AddressForm)
    address_custom_kwarg = FormField(AddressForm, kwargs={'custom_kwarg': True})
    address_initial = FormField(AddressForm, kwargs={
        'initial': {
            'street': 'Homebase 42',
            'city': 'Supertown'
        }
    })
    more_addresses = FormField(MultiAddressForm)


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

    def test_form_kwargs(self):
        superform = RegistrationForm()
        form = superform.forms['address_custom_kwarg']
        self.assertEqual(form.custom_attribute, True)

    def test_form_kwargs_initial(self):
        superform = RegistrationForm()
        form = superform.forms['address_initial']
        self.assertEqual(form['street'].value(), 'Homebase 42')
        self.assertEqual(form['city'].value(), 'Supertown')

    def test_initial_pass_through(self):
        superform = RegistrationForm(initial={
            'first_name': 'Patricia',
            'address': {'street': 'Default Road'}
        })
        form = superform.forms['address']
        self.assertEqual(superform['first_name'].value(), 'Patricia')
        self.assertEqual(superform['last_name'].value(), None)
        self.assertEqual(form['street'].value(), 'Default Road')
        self.assertEqual(form['city'].value(), None)

    def test_initial_pass_through_with_multiple_layers(self):
        superform = RegistrationForm(initial={
            'more_addresses': {
                'address1': {
                    'street': 'Fooway',
                    'city': 'Testcity'
                },
                'address2': {
                    'street': 'Barboulevard',
                }
            }
        })
        address1 = superform.forms['more_addresses'].forms['address1']
        address2 = superform.forms['more_addresses'].forms['address2']
        self.assertEqual(address1['street'].value(), 'Fooway')
        self.assertEqual(address1['city'].value(), 'Testcity')
        self.assertEqual(address2['street'].value(), 'Barboulevard')
        self.assertEqual(address2['city'].value(), None)
