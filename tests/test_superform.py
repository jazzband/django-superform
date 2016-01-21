import django
from django import forms
from django.forms.forms import ErrorDict, ErrorList
from django.forms.formsets import formset_factory
from django.test import TestCase
from django_superform import FormField
from django_superform import FormSetField
from django_superform import SuperForm


class EmailForm(forms.Form):
    email = forms.EmailField()


EmailFormSet = formset_factory(EmailForm)


class NameForm(forms.Form):
    name = forms.CharField()


class AccountForm(SuperForm):
    username = forms.CharField()
    emails = FormSetField(EmailFormSet)
    nested_form = FormField(NameForm)


class SubclassedAccountForm(AccountForm):
    nested_form_2 = FormField(NameForm)


class SuperFormTests(TestCase):
    def test_base_composite_fields(self):
        self.assertEqual(list(AccountForm.base_fields.keys()), ['username'])

        self.assertTrue(hasattr(AccountForm, 'base_composite_fields'))
        self.assertEqual(list(AccountForm.base_composite_fields.keys()), ['emails', 'nested_form'])
        self.assertTrue(hasattr(SubclassedAccountForm, 'base_composite_fields'))
        self.assertEqual(list(SubclassedAccountForm.base_composite_fields.keys()), ['emails', 'nested_form', 'nested_form_2'])

        field = AccountForm.base_composite_fields['emails']
        self.assertIsInstance(field, FormSetField)

        field = AccountForm.base_composite_fields['nested_form']
        self.assertIsInstance(field, FormField)

        self.assertFalse(hasattr(AccountForm, 'forms'))
        self.assertFalse(hasattr(AccountForm, 'formsets'))

    def test_fields_in_instantiated_forms(self):
        form = AccountForm()

        self.assertTrue(hasattr(form, 'composite_fields'))
        self.assertTrue(hasattr(form, 'forms'))
        self.assertTrue(hasattr(form, 'formsets'))

        self.assertEqual(list(form.forms.keys()), ['nested_form'])
        nested_form = form.forms['nested_form']
        self.assertIsInstance(nested_form, NameForm)

        self.assertEqual(list(form.formsets.keys()), ['emails'])
        formset = form.formsets['emails']
        self.assertIsInstance(formset, EmailFormSet)


class FormSetsInSuperFormsTests(TestCase):
    def setUp(self):
        self.formset_data = {
            'formset-emails-INITIAL_FORMS': 0,
            'formset-emails-TOTAL_FORMS': 1,
            'formset-emails-MAX_NUM_FORMS': 3,
        }

    def test_prefix(self):
        form = AccountForm()
        formset = form.formsets['emails']
        self.assertEqual(formset.prefix, 'formset-emails')

    def test_validation(self):
        data = self.formset_data.copy()
        form = AccountForm(data)
        self.assertEqual(form.is_valid(), False)
        self.assertTrue(form.errors['username'])
        self.assertFalse('emails' in form.errors)

        self.assertTrue(form.errors['nested_form'])
        self.assertTrue(form.errors['nested_form']['name'])
        self.assertIsInstance(form.errors['nested_form'], ErrorDict)

        data = self.formset_data.copy()
        data['formset-emails-INITIAL_FORMS'] = 1
        form = AccountForm(data)
        self.assertEqual(form.is_valid(), False)
        self.assertTrue(form.errors['username'])
        self.assertTrue(form.errors['emails'])
        self.assertIsInstance(form.errors['emails'], ErrorList)

    def test_empty_form_has_no_errors(self):
        """Empty forms have no errors."""
        form = AccountForm()

        self.assertFalse(form.is_valid())
        self.assertFalse(form.errors)

    def test_formset_errors(self):
        """Formset errors get propagated properly."""
        data = {
            'formset-emails-INITIAL_FORMS': 0,
            'formset-emails-TOTAL_FORMS': 1,
            'formset-emails-MAX_NUM_FORMS': 3,
            'formset-emails-0-email': 'foobar',
            'username': 'TestUser',
            'form-nested_form-name': 'Some Name',
        }
        form = AccountForm(data)

        if django.VERSION >= (1, 5):
            expected_errors = ErrorList([
                ErrorDict({
                    u'email': ErrorList([u'Enter a valid email address.'])
                })
            ])
        else:
            # Fix for Django 1.4
            expected_errors = ErrorList([
                ErrorDict({
                    u'email': ErrorList([u'Enter a valid e-mail address.'])
                })
            ])

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['emails'], expected_errors)
