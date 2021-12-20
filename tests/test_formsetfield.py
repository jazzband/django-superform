from django.forms.models import modelformset_factory
from django.template import Context, Template
from django.test import TestCase
from django_superform import SuperModelForm, ModelFormSetField, InlineFormSetField

from .models import Post, Image


ImageFormSet = modelformset_factory(Image, fields=["name"])


class PostForm(SuperModelForm):
    class Meta:
        model = Post
        fields = ["title"]

    images_inlineformset = InlineFormSetField(Post, Image, fields=["name"])
    images_modelformset = ModelFormSetField(ImageFormSet)

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.formsets["images_modelformset"].queryset = self.instance.images.all()


class TestFormSetField(TestCase):
    def test_inline_formset_field(self):
        post = Post.objects.create()
        _ = [post.images.create(name="image1"), post.images.create(name="image2")]
        form = PostForm(instance=post)
        t = Template("{{ form.images_inlineformset }}")
        c = Context({"form": form})
        assert 'value="image1"' in t.render(c)
        assert 'value="image2"' in t.render(c)

    def test_model_formset_field(self):
        post = Post.objects.create()
        _ = [post.images.create(name="image1"), post.images.create(name="image2")]
        form = PostForm(instance=post)
        t = Template("{{ form.images_modelformset }}")
        c = Context({"form": form})
        assert 'value="image1"' in t.render(c)
        assert 'value="image2"' in t.render(c)
