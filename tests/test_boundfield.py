from django import forms
from django.forms.forms import BoundField
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


NameFormSet = formset_factory(NameForm, extra=3)


class AccountForm(SuperForm):
    username = forms.CharField()
    emails = FormSetField(EmailFormSet)
    multiple_names = FormSetField(NameFormSet)
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

    def test_it_iterates_over_form_fields(self):
        form = AccountForm()
        composite_bf = form['nested_form']
        for nested_bf in composite_bf:
            self.assertTrue(isinstance(nested_bf, BoundField))
            self.assertEqual(nested_bf.name, 'name')

    def test_it_iterates_over_formset_forms(self):
        form = AccountForm()
        composite_bf = form['multiple_names']
        for nested_form in composite_bf:
            self.assertTrue(isinstance(nested_form, NameForm))

    def test_it_allows_key_access_to_form_fields(self):
        form = AccountForm()
        composite_f = form['nested_form']
        nested_bf = composite_f['name']
        self.assertTrue(isinstance(nested_bf, BoundField))
        self.assertEqual(nested_bf.name, 'name')

    def test_it_raises_keyerror_for_nonexistent_form_field(self):
        form = AccountForm()
        composite_bf = form['nested_form']
        with self.assertRaises(KeyError):
            composite_bf['nope']
        # Also raises KeyError when using an integer lookup.
        with self.assertRaises(KeyError):
            composite_bf[0]

    def test_it_allows_index_access_to_formset_forms(self):
        form = AccountForm(initial={
            'emails': [
                {'email': 'foo@example.com'},
                {'email': 'bar@example.com'},
            ]
        })
        composite_bf = form['emails']

        form1 = composite_bf[0]
        self.assertTrue(isinstance(form1, EmailForm))
        self.assertEqual(form1.initial, {'email': 'foo@example.com'})

        form2 = composite_bf[1]
        self.assertTrue(isinstance(form2, EmailForm))
        self.assertEqual(form2.initial, {'email': 'bar@example.com'})

    def test_it_raises_indexerror_for_nonexistent_formset_forms(self):
        form = AccountForm()
        composite_bf = form['emails']
        with self.assertRaises(IndexError):
            composite_bf[0]
        # Raises TypeError when using a string lookup as an integer is a hard
        # requirement.
        with self.assertRaises(TypeError):
            composite_bf['name']
