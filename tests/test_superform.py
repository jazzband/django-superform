from django import forms
from django.forms.forms import ErrorList
from django.forms.formsets import formset_factory
from django.test import TestCase
from django_superform import SuperForm, FormSetField


class EmailForm(forms.Form):
    email = forms.EmailField()


EmailFormSet = formset_factory(EmailForm)


class AccountForm(SuperForm):
    username = forms.CharField()
    emails = FormSetField(EmailFormSet)


class SuperFormTests(TestCase):
    def test_declared_composite_fields(self):
        self.assertEqual(list(AccountForm.base_fields.keys()), ['username'])
        self.assertTrue(hasattr(AccountForm, 'composite_fields'))
        self.assertEqual(list(AccountForm.composite_fields.keys()), ['emails'])
        field = AccountForm.composite_fields['emails']
        self.assertIsInstance(field, FormSetField)

        self.assertFalse(hasattr(AccountForm, 'formsets'))

    def test_fields_in_instantiated_forms(self):
        form = AccountForm()

        self.assertTrue(hasattr(form, 'composite_fields'))
        self.assertTrue(hasattr(form, 'formsets'))

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

        data = self.formset_data.copy()
        data['formset-emails-INITIAL_FORMS'] = 1
        form = AccountForm(data)
        self.assertEqual(form.is_valid(), False)
        self.assertTrue(form.errors['username'])
        self.assertTrue(form.errors['emails'])
        self.assertIsInstance(form.errors['emails'], ErrorList)
