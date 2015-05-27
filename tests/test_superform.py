from django import forms
from django.forms.forms import ErrorDict, ErrorList
from django.forms.formsets import formset_factory
from django.test import TestCase
from django_superform import SuperForm, FormSetField


class EmailInput(forms.TextInput):
    """A test widget with media directives."""

    class Media(object):
        css = {
            'all': ['http://example.com/email_widget_style.css'],
        }


class UsernameInput(forms.TextInput):
    """Another test widget with media directives."""

    class Media(object):
        js = ['http://example.com/check_username_available.js']


class EmailForm(forms.Form):
    email = forms.EmailField(widget=EmailInput)


EmailFormSet = formset_factory(EmailForm)


class AccountForm(SuperForm):
    username = forms.CharField(widget=UsernameInput)
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
        self.assertIsInstance(form.errors['emails'], list)

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
        }
        form = AccountForm(data)

        expected_errors = [ErrorDict(
            {u'email': ErrorList([u'Enter a valid email address.'])})]

        # Django 1.4 has "e-mail" instead of "email"
        expected_14_errors = [ErrorDict(
            {u'email': ErrorList([u'Enter a valid e-mail address.'])})]

        self.assertFalse(form.is_valid())
        if form.errors['emails'] != expected_14_errors:
            self.assertEqual(form.errors['emails'], expected_errors)

    def test_aggregate_media(self):
        """Media gets aggregated, including from composites."""
        form = AccountForm()

        expected_js = UsernameInput.Media.js
        expected_css = EmailInput.Media.css

        self.assertEqual(form.media._css, expected_css)
        self.assertEqual(form.media._js, expected_js)
