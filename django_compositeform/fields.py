from django.forms.models import inlineformset_factory


class FormSetField(object):
    '''
    First argument is a formset class that is instantiated by this
    FormSetField.

    You can pass the ``kwargs`` argument to specify kwargs values that
    are used when the ``formset_class`` is instantiated.
    '''

    # Tracks each time a FormSetField instance is created. Used to retain
    # order.
    creation_counter = 0

    def __init__(self, formset_class, kwargs=None):
        self.formset_class = formset_class
        if kwargs is None:
            kwargs = {}
        self.default_kwargs = kwargs

        # Increase the creation counter, and save our local copy.
        self.creation_counter = FormSetField.creation_counter
        FormSetField.creation_counter += 1

    def get_formset_class(self, form, name):
        '''
        Return the formset class that will be used for instantiation in
        ``get_formset``. You can override this method in subclasses to change
        the behaviour of the given formset class.
        '''

        return self.formset_class

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

        kwargs = {
            'prefix': self.get_formset_prefix(form, name)
        }
        kwargs.update(self.default_kwargs)
        return kwargs

    def get_formset(self, form, name):
        '''
        Get an instance of the formset.
        '''

        kwargs = self.get_formset_kwargs(form, name)
        formset_class = self.get_formset_class(form, name)
        formset = formset_class(
            form.data if form.is_bound else None,
            form.files if form.is_bound else None,
            **kwargs)
        return formset


class InlineFormSetField(FormSetField):
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
        if (formset_class, parent_model, model) == (None, None, None):
            raise ValueError(
                'You must either provide the formset_class attribute or '
                'parent_model and model.')
        if (
                formset_class is not None and
                (parent_model is not None or model is not None)):
            raise ValueError(
                'You must not provide the formset_class argument and '
                'parent_model/model.')

        if not formset_class:
            self.parent_model = parent_model
            self.model = model
            formset_class = inlineformset_factory(
                self.parent_model,
                self.model,
                **factory_kwargs)
        super(InlineFormSetField, self).__init__(formset_class, kwargs=kwargs)

    def get_formset_kwargs(self, form, name):
        kwargs = super(InlineFormSetField, self).get_formset_kwargs(form, name)
        kwargs.setdefault('instance', form.instance)
        return kwargs

    def save(self, form, name, formset, commit):
        return formset.save(commit=commit)
