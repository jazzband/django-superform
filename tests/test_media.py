from django import forms
from django.forms.formsets import formset_factory
from django.test import TestCase
from django_superform import SuperForm, FormSetField


class InputWithCSS(forms.TextInput):
    """A test widget with media directives."""

    class Media(object):
        css = {
            'all': ['http://example.com/email_widget_style.css'],
        }


class InputWithJS(forms.TextInput):
    """Another test widget with media directives."""

    class Media(object):
        js = ['http://example.com/check_username_available.js']


class EmailForm(forms.Form):
    email = forms.EmailField(widget=InputWithCSS)


EmailFormSet = formset_factory(EmailForm)


class FormWithNestedMedia(SuperForm):
    username = forms.CharField(widget=InputWithJS)
    emails = FormSetField(EmailFormSet)

    class Media(object):
        css = {
            'all': ['/static/all.css'],
            'print': ['/static/print.css'],
        }
        js = ['/static/1.js']


class FormMediaTests(TestCase):
    def test_aggregate_media(self):
        """Media gets aggregated, including from composites."""
        form = FormWithNestedMedia()

        expected_css = {
            'all': [
                'http://example.com/email_widget_style.css',
                '/static/all.css',
            ],
            'print': ['/static/print.css'],
        }
        expected_js = [
            'http://example.com/check_username_available.js',
            '/static/1.js',
        ]

        self.assertEqual(form.media._css, expected_css)
        self.assertEqual(form.media._js, expected_js)
