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
        template_name = kwargs.pop("template_name", None)
        if template_name is not None:
            self.template_name = template_name
        super(TemplateWidget, self).__init__(*args, **kwargs)
        self.context_instance = None

    def get_context_data(self):
        return {}

    def get_context(self, name, value, attrs=None):
        context = super().get_context(name, value, attrs)
        if self.value_context_name:
            context["widget"][self.value_context_name] = value

        context.update(self.get_context_data())

        return context

    def render(self, name, value, attrs=None, renderer=None, **kwargs):
        template_name = kwargs.pop("template_name", None)
        if template_name is None:
            template_name = self.template_name
        context = self.get_context(name, value, attrs=attrs or {}, **kwargs)
        return loader.render_to_string(
            template_name,
            context=context["widget"],
        )


class FormWidget(TemplateWidget):
    template_name = "superform/formfield.html"
    value_context_name = "form"


class FormSetWidget(TemplateWidget):
    template_name = "superform/formsetfield.html"
    value_context_name = "formset"
