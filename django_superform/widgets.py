from django import forms
from django.template import loader


class TemplateWidget(forms.Widget):
    """
    Template based widget. It renders the ``template_name`` set as attribute
    which can be overriden by the ``template_name`` argument to the
    ``__init__`` method.
    """

    field = None
    template_name = None
    value_context_name = None

    def __init__(self, *args, **kwargs):
        template_name = kwargs.pop('template_name', None)
        if template_name is not None:
            self.template_name = template_name
        super(TemplateWidget, self).__init__(*args, **kwargs)
        self.context_instance = None

    def get_context_data(self):
        return {}

    def get_context(self, name, value, attrs=None):
        context = {
            'name': name,
            'hidden': self.is_hidden,
            'required': self.is_required,
            # In our case ``value`` is the form or formset instance.
            'value': value,
        }
        if self.value_context_name:
            context[self.value_context_name] = value

        if self.is_hidden:
            context['hidden'] = True

        context.update(self.get_context_data())
        context['attrs'] = self.build_attrs(attrs)

        return context

    def render(self, name, value, attrs=None, **kwargs):
        template_name = kwargs.pop('template_name', None)
        if template_name is None:
            template_name = self.template_name
        context = self.get_context(name, value, attrs=attrs or {}, **kwargs)
        return loader.render_to_string(
            template_name,
            dictionary=context,
            context_instance=self.context_instance)


class FormWidget(TemplateWidget):
    template_name = 'superform/formfield.html'
    value_context_name = 'form'

    def value_from_datadict(self, data, files, name):
        return self.attrs['form_class'](data, files, prefix=name)

class FormSetWidget(TemplateWidget):
    template_name = 'superform/formsetfield.html'
    value_context_name = 'formset'

    def value_from_datadict(self, data, files, name):
        return self.attrs['formset_class'](data, files, prefix=name)
