"""
This is awesome. And needs more documentation.

To bring some light in the big number of classes in this file:

First there are:

* ``SuperForm``
* ``SuperModelForm``

They are the forms that you probably want to use in your own code. They are
direct base classes of ``django.forms.Form`` and ``django.forms.ModelForm``
and have the formset functionallity of this module backed in. They are ready
to use. Subclass them and be happy.

Then there are:

* ``SuperFormMixin``
* ``SuperModelFormMixin``

These are the mixins you can use if you don't want to subclass from
``django.forms.Form`` for whatever reason. The ones with Base at the beginning
don't have a metaclass attached. The ones without the Base in the name have
the relevant metaclass in place that handles the search for
``FormSetField``s.


Here is an example on how you can use this module::

    from django import forms
    from django_superform import SuperModelForm, FormSetField
    from .forms import CommentFormSet


    class PostForm(SuperModelForm):
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
    >>> form.composite_fields['comments']
    <CommetFormSet: ...>

Or in the template::

    {{ form.as_p }}

    {{ form.composite_fields.comments.management_form }}
    {% for fieldset_form in form.composite_fields.comments %}
        {{ fieldset_form.as_p }}
    {% endfor %}

You're welcome.

"""

from functools import reduce
from django import forms
from django.forms.forms import DeclarativeFieldsMetaclass, ErrorDict, ErrorList
from django.forms.models import ModelFormMetaclass
import six
import copy

from .fields import CompositeField

try:
    from collections import OrderedDict
except ImportError:
    from django.utils.datastructures import SortedDict as OrderedDict


class DeclerativeCompositeFieldsMetaclass(type):
    """
    Metaclass that converts FormField and FormSetField attributes to a
    dictionary called `composite_fields`. It will also include all composite
    fields from parent classes.
    """

    def __new__(mcs, name, bases, attrs):
        # Collect composite fields from current class.
        current_fields = []
        for key, value in list(attrs.items()):
            if isinstance(value, CompositeField):
                current_fields.append((key, value))
                attrs.pop(key)
        current_fields.sort(key=lambda x: x[1].creation_counter)
        attrs['declared_composite_fields'] = OrderedDict(current_fields)

        new_class = super(DeclerativeCompositeFieldsMetaclass, mcs).__new__(
            mcs, name, bases, attrs)

        # Walk through the MRO.
        declared_fields = OrderedDict()
        for base in reversed(new_class.__mro__):
            # Collect fields from base class.
            if hasattr(base, 'declared_composite_fields'):
                declared_fields.update(base.declared_composite_fields)

            # Field shadowing.
            for attr, value in base.__dict__.items():
                if value is None and attr in declared_fields:
                    declared_fields.pop(attr)

        new_class.base_composite_fields = declared_fields
        new_class.declared_composite_fields = declared_fields

        return new_class


class SuperFormMetaclass(
        DeclerativeCompositeFieldsMetaclass,
        DeclarativeFieldsMetaclass):
    """
    Metaclass for :class:`~django_superform.forms.SuperForm`.
    """


class SuperModelFormMetaclass(
        DeclerativeCompositeFieldsMetaclass,
        ModelFormMetaclass):
    """
    Metaclass for :class:`~django_superform.forms.SuperModelForm`.
    """


class SuperFormMixin(object):
    """
    The base class for all super forms. It does not inherit from any other
    classes, so you are free to mix it into any custom form class you have. You
    need to use it together with ``SuperFormMetaclass``, like this:

    .. code:: python

        from django_superform import SuperFormMixin
        from django_superform import SuperFormMetaclass
        import six

        class MySuperForm(six.with_metaclass(
                SuperFormMetaclass,
                SuperFormMixin,
                MyCustomForm)):
            pass

    The goal of a superform is to behave just like a normal django form but is
    able to take composite fields, like
    :class:`~django_superform.fields.FormField` and
    :class:`~django_superform.fields.FormSetField`.

    Cleaning, validation, etc. should work totally transparent. See the
    :ref:`Quickstart Guide <quickstart>` for how superforms are used.
    """

    def __init__(self, *args, **kwargs):
        super(SuperFormMixin, self).__init__(*args, **kwargs)
        self._init_composite_fields()

    def __getitem__(self, name):
        """
        Returns a ``django.forms.BoundField`` for the given field name. It also
        returns :class:`~django_superform.boundfield.CompositeBoundField`
        instances for composite fields.
        """
        if name not in self.fields and name in self.composite_fields:
            field = self.composite_fields[name]
            return field.get_bound_field(self, name)
        return super(SuperFormMixin, self).__getitem__(name)

    def add_composite_field(self, name, field):
        """
        Add a dynamic composite field to the already existing ones and
        initialize it appropriatly.
        """
        self.composite_fields[name] = field
        self._init_composite_field(name, field)

    def get_composite_field_value(self, name):
        """
        Return the form/formset instance for the given field name.
        """
        field = self.composite_fields[name]
        if hasattr(field, 'get_form'):
            return self.forms[name]
        if hasattr(field, 'get_formset'):
            return self.formsets[name]

    def _init_composite_field(self, name, field):
        if hasattr(field, 'get_form'):
            form = field.get_form(self, name)
            self.forms[name] = form
        if hasattr(field, 'get_formset'):
            formset = field.get_formset(self, name)
            self.formsets[name] = formset

    def _init_composite_fields(self):
        """
        Setup the forms and formsets.
        """
        # The base_composite_fields class attribute is the *class-wide*
        # definition of fields. Because a particular *instance* of the class
        # might want to alter self.composite_fields, we create
        # self.composite_fields here by copying base_composite_fields.
        # Instances should always modify self.composite_fields; they should not
        # modify base_composite_fields.
        self.composite_fields = copy.deepcopy(self.base_composite_fields)
        self.forms = OrderedDict()
        self.formsets = OrderedDict()
        for name, field in self.composite_fields.items():
            self._init_composite_field(name, field)

    def full_clean(self):
        """
        Clean the form, including all formsets and add formset errors to the
        errors dict. Errors of nested forms and formsets are only included if
        they actually contain errors.
        """
        super(SuperFormMixin, self).full_clean()
        for field_name, composite in self.forms.items():
            composite.full_clean()
            if not composite.is_valid() and composite._errors:
                self._errors[field_name] = ErrorDict(composite._errors)
        for field_name, composite in self.formsets.items():
            composite.full_clean()
            if not composite.is_valid() and composite._errors:
                self._errors[field_name] = ErrorList(composite._errors)

    @property
    def media(self):
        """
        Incooperate composite field's media.
        """
        media_list = []
        media_list.append(super(SuperFormMixin, self).media)
        for composite_name in self.composite_fields.keys():
            form = self.get_composite_field_value(composite_name)
            media_list.append(form.media)
        return reduce(lambda a, b: a + b, media_list)


class SuperModelFormMixin(SuperFormMixin):
    """
    Can be used in with your custom form subclasses like this:

    .. code:: python

        from django_superform import SuperModelFormMixin
        from django_superform import SuperModelFormMetaclass
        import six

        class MySuperForm(six.with_metaclass(
                SuperModelFormMetaclass,
                SuperModelFormMixin,
                MyCustomModelForm)):
            pass
    """

    def save(self, commit=True):
        """
        When saving a super model form, the nested forms and formsets will be
        saved as well.

        The implementation of ``.save()`` looks like this:

        .. code:: python

            saved_obj = self.save_form()
            self.save_forms()
            self.save_formsets()
            return saved_obj

        That makes it easy to override it in order to change the order in which
        things are saved.

        The ``.save()`` method will return only a single model instance even if
        nested forms are saved as well. That keeps the API similiar to what
        Django's model forms are offering.

        If ``commit=False`` django's modelform implementation will attach a
        ``save_m2m`` method to the form instance, so that you can call it
        manually later. When you call ``save_m2m``, the ``save_forms`` and
        ``save_formsets`` methods will be executed as well so again all nested
        forms are taken care of transparantly.
        """
        saved_obj = self.save_form(commit=commit)
        self.save_forms(commit=commit)
        self.save_formsets(commit=commit)
        return saved_obj

    def _extend_save_m2m(self, name, composites):
        additional_save_m2m = []
        for composite in composites:
            if hasattr(composite, 'save_m2m'):
                additional_save_m2m.append(composite.save_m2m)

        if not additional_save_m2m:
            return

        def additional_saves():
            for save_m2m in additional_save_m2m:
                save_m2m()

        # The save() method was called before save_forms()/save_formsets(), so
        # we will already have save_m2m() available.
        if hasattr(self, 'save_m2m'):
            _original_save_m2m = self.save_m2m
        else:
            def _original_save_m2m():
                return None

        def augmented_save_m2m():
            _original_save_m2m()
            additional_saves()

        self.save_m2m = augmented_save_m2m
        setattr(self, name, additional_saves)

    def save_form(self, commit=True):
        """
        This calls Django's ``ModelForm.save()``. It only takes care of
        saving this actual form, and leaves the nested forms and formsets
        alone.

        We separate this out of the
        :meth:`~django_superform.forms.SuperModelForm.save` method to make
        extensibility easier.
        """
        return super(SuperModelFormMixin, self).save(commit=commit)

    def save_forms(self, commit=True):
        saved_composites = []
        for name, composite in self.forms.items():
            field = self.composite_fields[name]
            if hasattr(field, 'save'):
                field.save(self, name, composite, commit=commit)
                saved_composites.append(composite)

        self._extend_save_m2m('save_forms_m2m', saved_composites)

    def save_formsets(self, commit=True):
        """
        Save all formsets. If ``commit=False``, it will modify the form's
        ``save_m2m()`` so that it also calls the formsets' ``save_m2m()``
        methods.
        """
        saved_composites = []
        for name, composite in self.formsets.items():
            field = self.composite_fields[name]
            if hasattr(field, 'save'):
                field.save(self, name, composite, commit=commit)
                saved_composites.append(composite)

        self._extend_save_m2m('save_formsets_m2m', saved_composites)


class SuperModelForm(six.with_metaclass(SuperModelFormMetaclass,
                                        SuperModelFormMixin, forms.ModelForm)):
    """
    The ``SuperModelForm`` works like a Django ``ModelForm`` but has the
    capabilities of nesting like :class:`~django_superform.forms.SuperForm`.

    Saving a ``SuperModelForm`` will also save all nested model forms as well.
    """


class SuperForm(six.with_metaclass(SuperFormMetaclass,
                                   SuperFormMixin, forms.Form)):
    """
    The base class for all super forms. The goal of a superform is to behave
    just like a normal django form but is able to take composite fields, like
    :class:`~django_superform.fields.FormField` and
    :class:`~django_superform.fields.FormSetField`.

    Cleaning, validation, etc. should work totally transparent. See the
    :ref:`Quickstart Guide <quickstart>` for how superforms are used.
    """
