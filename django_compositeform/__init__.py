'''
This is awesome. And needs more documentation.

To bring some light in the big number of classes in this file:

First there are:

* ``FormWithFormSets``
* ``ModelFormWithFormSets``

They are the forms that you probably want to use in your own code. They are
direct base classes of ``django.forms.Form`` and ``django.forms.ModelForm``
and have the formset functionallity of this module backed in. They are ready
to use. Subclass them and be happy.

Then there are:

* ``BaseFormSetMixin``
* ``BaseModelFormSetMixin``
* ``FormSetMixin``
* ``ModelFormSetMixin``

These are the mixins you can use if you don't want to subclass from
``django.forms.Form`` for whatever reason. The ones with Base at the beginning
don't have a metaclass attached. The ones without the Base in the name have
the relevant metaclass in place that handles the search for
``FormSetField``s.


Here is an example on how you can use this module::

    from django import forms
    from django_compositeform import ModelFormWithFormSets, FormSetField
    from .forms import CommentFormSet


    class PostForm(ModelFormWithFormSets):
        title = forms.CharField()
        text = forms.CharField()
        comments = FormSetField(CommentFormSet)

    # Now you can use the form in the view:

    def post_form(request):
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                obj = form.save()
                return HttpResponseRedirect(obj.get_absolute_url())
        else:
            form = PostForm()
        return render_to_response('post_form.html', {
            'form',
        }, context_instance=RequestContext(request))

And yes, thanks for asking, the ``form.is_valid()`` and ``form.save()`` calls
transparantly propagate to the defined comments formset and call their
``is_valid()`` and ``save()`` methods. So you don't have to do anything
special in your view!

Now to how you can access the instantiated formsets::

    >>> form = PostForm()
    >>> form.formsets['comments']
    <CommetFormSet: ...>

Or in the template::

    {{ form.as_p }}

    {{ form.formsets.comments.management_form }}
    {% for fieldset_form in form.formsets.comments %}
        {{ fieldset_form.as_p }}
    {% endfor %}

You're welcome.

'''

import six
from django import forms
from django.forms.forms import DeclarativeFieldsMetaclass
from django.forms.models import ModelFormMetaclass
from django.utils.datastructures import SortedDict


class FormSetField(object):
    # Tracks each time a FormSetField instance is created. Used to retain
    # order.
    creation_counter = 0

    def __init__(self, formset_class):
        self.formset_class = formset_class

        # Increase the creation counter, and save our local copy.
        self.creation_counter = FormSetField.creation_counter
        FormSetField.creation_counter += 1

    def get_formset_prefix(self, form, name):
        '''
        Return the prefix that is used for the formset.
        '''

        return '{form_prefix}formset-{formset_name}'.format(
            form_prefix=form.prefix + '-' if form.prefix else '',
            formset_name=name)

    def get_formset_kwargs(self, form, name):
        '''
        Return the keyword arguments that are used to instantiate the formset.
        '''

        return {
            'prefix': self.get_formset_prefix(form, name)
        }

    def get_formset(self, form, name):
        '''
        Get an instance of the formset.
        '''

        formset = self.formset_class(
            form.data if form.is_bound else None,
            form.files if form.is_bound else None,
            **self.get_formset_kwargs(form, name))
        return formset


def get_declared_formset_fields(bases, attrs):
    """
    Create a list of formset field instances from the passed in 'attrs', plus
    any similar fields on the base classes (in 'bases').
    """
    formsets = [
        (field_name, attrs.pop(field_name))
        for field_name, obj in list(six.iteritems(attrs))
        if isinstance(obj, FormSetField)]

    formsets.sort(key=lambda x: x[1].creation_counter)

    # If this class is subclassing another Form, add that Form's formsets.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of formsets.
    for base in bases[::-1]:
        if hasattr(base, 'formset_fields'):
            formsets = list(six.iteritems(base.formset_fields)) + formsets

    return SortedDict(formsets)


class DeclerativeFormSetFieldMetaclass(type):
    """
    Metaclass that converts FormSetField attributes to a dictionary called
    'formset_fields', taking into account parent class 'formset_fields' as
    well.
    """

    def __new__(cls, name, bases, attrs):
        attrs['formset_fields'] = get_declared_formset_fields(bases, attrs)
        new_class = super(DeclerativeFormSetFieldMetaclass, cls).__new__(
            cls, name, bases, attrs)
        return new_class


class FormSetMixinMetaclass(
        DeclerativeFormSetFieldMetaclass,
        DeclarativeFieldsMetaclass):
    def __new__(cls, name, bases, attrs):
        attrs['formset_fields'] = get_declared_formset_fields(bases, attrs)
        return DeclarativeFieldsMetaclass.__new__(cls, name, bases, attrs)


class ModelFormSetMixinMetaclass(
        DeclerativeFormSetFieldMetaclass,
        ModelFormMetaclass):
    def __new__(cls, name, bases, attrs):
        attrs['formset_fields'] = get_declared_formset_fields(bases, attrs)
        return ModelFormMetaclass.__new__(cls, name, bases, attrs)


class BaseFormSetMixin(object):
    '''
    The goal is to provide a mixin that makes handling of formsets on forms
    really easy.

    It should allow something like::

        >>> class MyForm(FormSetMixin, forms.Form):
        ...     name = forms.CharField()
        ...     links = FormsetField(formset=LinkFormSet)
        ...
        >>> myform = MyForm()
        >>> isinstance(myform.formsets['links'], LinkFormSet)
        True

    Cleaning, validation, etc should work totally transparent.
    '''

    def __init__(self, *args, **kwargs):
        super(BaseFormSetMixin, self).__init__(*args, **kwargs)
        self._init_formsets()

    def _init_formsets(self):
        '''
        Setup the formsets.
        '''
        self.formsets = {}
        for name, field in self.formset_fields.items():
            formset = field.get_formset(self, name)
            self.formsets[name] = formset

    def full_clean(self):
        '''
        Clean the form, including all formsets and add formset errors to the
        errors dict.
        '''
        super(BaseFormSetMixin, self).full_clean()
        formset_errors = {}
        for key, formset in self.formsets.items():
            formset.full_clean()
            if not formset.is_valid():
                formset_errors[key] = formset.errors
        if formset_errors:
            self._errors['formsets'] = formset_errors


class FormSetMixin(BaseFormSetMixin):
    __metaclass__ = DeclerativeFormSetFieldMetaclass


class BaseModelFormSetMixin(BaseFormSetMixin):
    def save(self, commit=True):
        '''
        If ``commit=False`` django's modelform implementation will attach a
        ``save_m2m`` method to the form instance, so that you can call it
        manually later. When you call ``save_m2m``, the ``save_formsets``
        method will be executed as well.
        '''

        saved_obj = super(BaseModelFormSetMixin, self).save(commit=commit)
        self.save_formsets(commit=commit)
        return saved_obj

    def save_formsets(self, commit=True):
        '''
        Save all formsets. If ``commit=False``, it will modify the form's
        ``save_m2m()`` so that it also calls the formsets' ``save_m2m()``
        methods.
        '''

        for name, formset in self.formsets.items():
            formset.save(commit=commit)

        # Add the formsets' save_m2m() methods to the one that got attached to
        # the form.
        if not commit:
            formsets_save_m2m = []
            for name, formset in self.formsets.items():
                formsets_save_m2m.append(formset.save_m2m)

            def save_formsets_m2m():
                for formset_save_m2m in formsets_save_m2m:
                    formset_save_m2m()
            self.save_formsets_m2m = save_formsets_m2m

            form = self

            # The save() method was called before save_formsets(), so we will
            # already have save_m2m() available.
            _original_save_m2m = self.save_m2m
            def save_m2m_and_formsets_m2m():
                _original_save_m2m()
                form.save_formsets_m2m()

            self.save_m2m = save_m2m_and_formsets


class ModelFormSetMixin(BaseModelFormSetMixin):
    __metaclass__ = DeclerativeFormSetFieldMetaclass


class ModelFormWithFormSets(ModelFormSetMixin, forms.ModelForm):
    __metaclass__ = ModelFormSetMixinMetaclass


class FormWithFormSets(FormSetMixin, forms.Form):
    __metaclass__ = FormSetMixinMetaclass
