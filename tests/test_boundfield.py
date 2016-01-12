from django import forms
from django.forms.formsets import formset_factory
from django.test import TestCase
from django_superform import FormField
from django_superform import FormSetField
from django_superform import SuperForm
from django_superform.boundfield import CompositeBoundField


class EmailForm(forms.Form):
    email = forms.EmailField()


EmailFormSet = formset_factory(EmailForm, extra=0)


class NameForm(forms.Form):
    name = forms.CharField()


class AccountForm(SuperForm):
    username = forms.CharField()
    emails = FormSetField(EmailFormSet)
    nested_form = FormField(NameForm)


class CompositeBoundFieldTests(TestCase):
    def test_it_is_nonzero_for_empty_formsets(self):
        form = AccountForm()
        bf = form['emails']
        self.assertTrue(isinstance(bf, CompositeBoundField))
        self.assertEqual(len(bf), 0)
        self.assertEqual(bool(bf), True)

    def test_it_is_nonzero_for_filled_formsets(self):
        form = AccountForm(initial={
            'emails': [{'email': 'admin@example.com'}]
        })
        bf = form['emails']
        self.assertTrue(isinstance(bf, CompositeBoundField))
        self.assertEqual(len(bf), 1)
        self.assertEqual(bool(bf), True)

    def test_it_is_nonzero_for_forms(self):
        form = AccountForm()
        bf = form['nested_form']
        self.assertTrue(isinstance(bf, CompositeBoundField))
        self.assertEqual(bool(bf), True)
