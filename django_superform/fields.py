from django.forms.models import inlineformset_factory

from .widgets import FormWidget, FormSetWidget


class BaseCompositeField(object):
    '''
    The ``BaseCompositeField`` takes care of keeping some kind of compatibility
    with the ``django.forms.Field`` class.
    '''

    widget = None
    show_hidden_initial = False

    # Tracks each time a FormSetField instance is created. Used to retain
    # order.
    creation_counter = 0

    def __init__(self, required=True, widget=None, label=None, help_text='',
                 localize=False):
        self.required = required
        self.label = label
        self.help_text = help_text

        widget = widget or self.widget
        if isinstance(widget, type):
            widget = widget()

        # Trigger the localization machinery if needed.
        self.localize = localize
        if self.localize:
            widget.is_localized = True

        # Let the widget know whether it should display as required.
        widget.is_required = self.required

        # We do not call self.widget_attrs() here as the original field is
        # doing it.

        self.widget = widget

        # Increase the creation counter, and save our local copy.
        self.creation_counter = BaseCompositeField.creation_counter
        BaseCompositeField.creation_counter += 1


class CompositeField(BaseCompositeField):
    '''
    Implements the base structure that is relevant for all composite fields.
    '''

    prefix_name = 'composite'

    def __init__(self, *args, **kwargs):
        super(CompositeField, self).__init__(*args, **kwargs)

        # Let the widget know about the field for easier complex renderings in
        # the template.
        self.widget.field = self

    def get_prefix(self, form, name):
        '''
        Return the prefix that is used for the formset.
        '''

        return '{form_prefix}{prefix_name}-{field_name}'.format(
            form_prefix=form.prefix + '-' if form.prefix else '',
            prefix_name=self.prefix_name,
            field_name=name)

    def get_kwargs(self, form, name):
        '''
        Return the keyword arguments that are used to instantiate the formset.
        '''

        kwargs = {
            'prefix': self.get_prefix(form, name)
        }
        kwargs.update(self.default_kwargs)
        return kwargs


class FormField(CompositeField):
    prefix_name = 'form'
    widget = FormWidget

    def __init__(self, form_class, kwargs=None, **field_kwargs):
        super(FormField, self).__init__(**field_kwargs)

        self.form_class = form_class
        if kwargs is None:
            kwargs = {}
        self.default_kwargs = kwargs

    def get_form_class(self, form, name):
        '''
        Return the form class that will be used for instantiation in
        ``get_form``. You can override this method in subclasses to change
        the behaviour of the given form class.
        '''

        return self.form_class

    def get_form(self, form, name):
        '''
        Get an instance of the form.
        '''

        kwargs = self.get_kwargs(form, name)
        form_class = self.get_form_class(form, name)
        composite_form = form_class(
            form.data if form.is_bound else None,
            form.files if form.is_bound else None,
            **kwargs)
        return composite_form


class ModelFormField(FormField):
    def get_instance(self, form, name):
        return None

    def get_kwargs(self, form, name):
        kwargs = super(ModelFormField, self).get_kwargs(form, name)
        instance = self.get_instance(form, name)
        kwargs.setdefault('instance', instance)
        return kwargs

    def shall_save(self, form, name, composite_form):
        if composite_form.empty_permitted and not composite_form.has_changed():
            return False
        return True

    def save(self, form, name, composite_form, commit):
        if self.shall_save(form, name, composite_form):
            return composite_form.save(commit=commit)
        return None


class ForeignKeyFormField(ModelFormField):
    def __init__(self, form_class, kwargs=None, field_name=None, blank=None,
                 **field_kwargs):
        super(ForeignKeyFormField, self).__init__(form_class, kwargs,
                                                  **field_kwargs)
        self.field_name = field_name
        self.blank = blank

    def get_kwargs(self, form, name):
        kwargs = super(ForeignKeyFormField, self).get_kwargs(form, name)
        if 'instance' not in kwargs:
            kwargs.setdefault('instance', self.get_instance(form, name))
        if 'empty_permitted' not in kwargs:
            if self.allow_blank(form, name):
                kwargs['empty_permitted'] = True
        return kwargs

    def get_field_name(self, form, name):
        return self.field_name or name

    def allow_blank(self, form, name):
        '''
        Allow blank determines if the form might be completely empty. If it's
        empty it will result in a None as the saved value for the ForeignKey.
        '''
        if self.blank is not None:
            return self.blank
        model = form._meta.model
        field = model._meta.get_field(self.get_field_name(form, name))
        return field.blank

    def get_form_class(self, form, name):
        form_class = self.form_class
        return form_class

    def get_instance(self, form, name):
        field_name = self.get_field_name(form, name)
        return getattr(form.instance, field_name)

    def save(self, form, name, composite_form, commit):
        # Support the ``empty_permitted`` attribute. This is set if the field
        # is ``blank=True`` .
        if composite_form.empty_permitted and not composite_form.has_changed():
            saved_obj = composite_form.instance
        else:
            saved_obj = super(ForeignKeyFormField, self).save(form, name,
                                                              composite_form,
                                                              commit)
        setattr(form.instance, self.get_field_name(form, name), saved_obj)
        if commit:
            form.instance.save()
        else:
            raise NotImplementedError(
                'ForeignKeyFormField cannot yet be used with non-commiting '
                'form saves.')
        return saved_obj


class FormSetField(CompositeField):
    '''
    First argument is a formset class that is instantiated by this
    FormSetField.

    You can pass the ``kwargs`` argument to specify kwargs values that
    are used when the ``formset_class`` is instantiated.
    '''

    prefix_name = 'formset'
    widget = FormSetWidget

    def __init__(self, formset_class, kwargs=None, **field_kwargs):
        super(FormSetField, self).__init__(**field_kwargs)

        self.formset_class = formset_class
        if kwargs is None:
            kwargs = {}
        self.default_kwargs = kwargs

    def get_formset_class(self, form, name):
        '''
        Return the formset class that will be used for instantiation in
        ``get_formset``. You can override this method in subclasses to change
        the behaviour of the given formset class.
        '''

        return self.formset_class

    def get_formset(self, form, name):
        '''
        Get an instance of the formset.
        '''

        kwargs = self.get_kwargs(form, name)
        formset_class = self.get_formset_class(form, name)
        formset = formset_class(
            form.data if form.is_bound else None,
            form.files if form.is_bound else None,
            **kwargs)
        return formset


class ModelFormSetField(FormSetField):
    def shall_save(self, form, name, formset):
        return True

    def save(self, form, name, formset, commit):
        if self.shall_save(form, name, formset):
            return formset.save(commit=commit)
        return None


class InlineFormSetField(ModelFormSetField):
    '''
    The ``InlineFormSetField`` helps when you want to use a inline formset.

    You can pass in either the keyword argument ``formset_class`` which is a
    ready to use formset that inherits from ``BaseInlineFormSet`` or was
    created by the ``inlineformset_factory``.

    The other option is to provide the arguments that you would usually pass
    into the ``inlineformset_factory``. The required arguments for that are:

    ``model``
        The model class which should be represented by the forms in the
        formset.
    ``parent_model``
        The parent model is the one that is referenced by the model in a
        foreignkey.
    ``form`` (optional)
        The model form that is used as a baseclass for the forms in the inline
        formset.

    You can use the ``kwargs`` keyword argument to pass extra arguments for the
    formset that are passed through when the formset is instantiated.

    All other not mentioned keyword arguments, like ``extra``, ``max_num`` etc.
    will be passed directly to the ``inlineformset_factory``.

    Example:

        class Gallery(models.Model):
            name = models.CharField(max_length=50)

        class Image(models.Model):
            gallery = models.ForeignKey(Gallery)
            image = models.ImageField(...)

        class GalleryForm(ModelFormWithFormSets):
            class Meta:
                model = Gallery
                fields = ('name',)

            images = InlineFormSetField(
                parent_model=Gallery,
                model=Image,
                extra=1)
    '''

    def __init__(self, parent_model=None, model=None, formset_class=None,
                 kwargs=None, **factory_kwargs):
        '''
        You need to either provide the ``formset_class`` or the ``model``
        argument.

        If the ``formset_class`` argument is not given, the ``model`` argument
        is used to create the formset_class on the fly when needed by using the
        ``inlineformset_factory``.
        '''

        # Make sure that all standard arguments will get passed through to the
        # parent's __init__ method.
        field_kwargs = {}
        for arg in ['required', 'widget', 'label', 'help_text', 'localize']:
            if arg in factory_kwargs:
                field_kwargs[arg] = factory_kwargs.pop(arg)

        self.parent_model = parent_model
        self.model = model
        self.formset_factory_kwargs = factory_kwargs
        super(InlineFormSetField, self).__init__(formset_class, kwargs=kwargs,
                                                 **field_kwargs)

    def get_model(self, form, name):
        return self.model

    def get_parent_model(self, form, name):
        if self.parent_model is not None:
            return self.parent_model
        return form._meta.model

    def get_formset_class(self, form, name):
        '''
        Either return the formset class that was provided as argument to the
        __init__ method, or build one based on the ``parent_model`` and
        ``model`` attributes.
        '''

        if self.formset_class is not None:
            return self.formset_class
        formset_class = inlineformset_factory(
            self.get_parent_model(form, name),
            self.get_model(form, name),
            **self.formset_factory_kwargs)
        return formset_class

    def get_kwargs(self, form, name):
        kwargs = super(InlineFormSetField, self).get_kwargs(form, name)
        kwargs.setdefault('instance', form.instance)
        return kwargs
