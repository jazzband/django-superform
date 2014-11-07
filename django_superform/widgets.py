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
            'True': True,
            # In our case ``value`` is the form or formset instance.
            'value': value,
        }
        if self.value_context_name:
            context[self.value_context_name] = value

        # True is injected in the context to allow stricter comparisons
        # for widget attrs. See #25.
        if self.is_hidden:
            context['hidden'] = True

        context.update(self.get_context_data())
        context['attrs'] = self.build_attrs(attrs)

        for key, attr in context['attrs'].items():
            if attr == 1:
                # 1 == True so 'key="1"' will show up only as 'key'
                # Casting to a string so that it doesn't equal to True
                # See #25.
                if not isinstance(attr, bool):
                    context['attrs'][key] = str(attr)

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


class FormSetWidget(TemplateWidget):
    template_name = 'superform/formsetfield.html'
    value_context_name = 'formset'
