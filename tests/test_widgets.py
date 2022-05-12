from django.test import TestCase
from django_superform.widgets import TemplateWidget


class TemplateWidgetTests(TestCase):
    def test_it_takes_template_name_argument(self):
        widget = TemplateWidget(template_name="foo.html")
        self.assertEqual(widget.template_name, "foo.html")

    def test_it_puts_hidden_variable_in_context(self):
        widget = TemplateWidget()

        widget_context = widget.get_context("foo", None)
        self.assertEqual(widget_context["hidden"], False)

        class HiddenWidget(TemplateWidget):
            is_hidden = True

        hidden_widget = HiddenWidget()

        hidden_widget_context = hidden_widget.get_context("foo", None)
        self.assertEqual(hidden_widget_context["hidden"], True)

    def test_it_recognizes_value_context_name(self):
        class DifferentValueNameWidget(TemplateWidget):
            value_context_name = "strange_name"

        value = object()
        widget = DifferentValueNameWidget()
        context = widget.get_context("foo", value)

        self.assertTrue(context["strange_name"] is value)

        # The name 'value' is always available, regardless of the
        # value_context_name.
        self.assertTrue(context["value"] is value)

    def test_it_renders_template_from_attribute(self):
        class TemplateAttributeWidget(TemplateWidget):
            template_name = "_print_name.html"

        widget = TemplateAttributeWidget()
        with self.assertTemplateUsed("_print_name.html"):
            result = widget.render(name="A_NAME", value=None, attrs=None)
            self.assertEqual(result.strip(), "A_NAME")

    def test_it_render_takes_template_name_argument(self):
        class TemplateAttributeWidget(TemplateWidget):
            template_name = "_foo.html"

        widget = TemplateAttributeWidget()
        with self.assertTemplateUsed("_print_name.html"):
            with self.assertTemplateNotUsed("_foo.html"):
                result = widget.render(
                    name="A_NAME",
                    value=None,
                    attrs=None,
                    template_name="_print_name.html",
                )
                self.assertEqual(result.strip(), "A_NAME")
