from django.forms.forms import BoundField


class CompositeBoundField(BoundField):
    """
    This is an emulation of the BoundField that is returned if you call
    ``form['field_name']`` for an ordinary django field.

    The ``CompositeBoundField`` has the purpose of providing the same interface
    to other libraries that use a ``BoundField`` instance for rendering.
    """

    # __init__, no changes required
    # __str__, no changes required

    def __iter__(self):
        """
        Iterates over the composite field. For ``FormSetField``s this will
        return form instances. For ``FormField``s this will return bound form
        fields.
        """
        for item in self.form.get_composite_field_value(self.name):
            yield item

    # __len__, no changes required

    def __getitem__(self, item):
        """
        Allow named access to the form fields and forms contained in the
        composite fields. For ``FormField``s you get a bound field, for
        ``FormSetField`` you can use and integer index lookup for a specific
        form.
        """
        composite_item = self.form.get_composite_field_value(self.name)
        return composite_item[item]

    def __bool__(self):
        """
        Never evaluate the bound field as False. This is necessary since
        otherwise python will fallback to the __len__ implementation of the
        object. However this might return 0 for a ``CompositeBoundField`` since
        it might contain zero forms in the given formset.
        """
        return True

    # Python 2's __bool__ is called __nonzero__.
    __nonzero__ = __bool__

    @property
    def errors(self):
        """
        Returns an ErrorList for this field, either the errors of the contained
        formset or of the inlined form.
        """
        # TODO: We could make this work and return the forms/formsets errors.
        return self.form.error_class()

    # as_widget, no changes required

    def as_text(self, attrs=None, **kwargs):
        # Not supported. This does not make sense for a CompositeField.
        raise NotImplementedError

    def as_textarea(self, attrs=None, **kwargs):
        # Not supported. This does not make sense for a CompositeField.
        raise NotImplementedError

    def as_hidden(self, attrs=None, **kwargs):
        """
        Returns a string of HTML for representing this as multiple
        <input type="hidden">.
        """
        # TODO: This might make sense. But we don't support it yet.
        raise NotImplementedError

    @property
    def data(self):
        """
        Returns the data for this BoundField, or None if it wasn't given.
        """
        # Not supported. This does not make sense for a CompositeField.
        return None

    def value(self):
        """
        Returns the form/formset for this BoundField. This is passed into the
        call for ``self.widget.render`` in the ``as_widget`` method.
        """
        return self.form.get_composite_field_value(self.name)

    # label_tag, no changes required
    # auto_id, no changes required
    # id_for_label, no changes required
