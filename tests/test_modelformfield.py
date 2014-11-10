from django import forms
from django.test import TestCase
from django_superform import SuperModelForm, ModelFormField

from .models import Series, Post, Image


class UseFirstModelFormField(ModelFormField):
    def get_instance(self, form, name):
        try:
            return self.form_class._meta.model._default_manager.all()[0]
        except IndexError:
            return None


class SeriesForm(forms.ModelForm):
    class Meta:
        model = Series
        fields = ('title',)


class PostForm(SuperModelForm):
    series = ModelFormField(SeriesForm)

    class Meta:
        model = Post
        fields = ('title',)


class UnrequiredSeriesPostForm(SuperModelForm):
    series = ModelFormField(SeriesForm, required=False)

    class Meta:
        model = Post
        fields = ('title',)


class UseExistingSeriesPostForm(SuperModelForm):
    existing_series = UseFirstModelFormField(SeriesForm)

    class Meta:
        model = Post
        fields = ('title',)


class FormFieldTests(TestCase):
    def test_is_in_composite_fields(self):
        superform = PostForm()
        self.assertTrue('series' in superform.composite_fields)

    def test_is_in_forms_attr(self):
        superform = PostForm()
        self.assertTrue('series' in superform.forms)
        self.assertTrue(isinstance(superform.forms['series'], SeriesForm))

    def test_form_prefix(self):
        superform = PostForm()
        form = superform.forms['series']
        self.assertEqual(form.prefix, 'form-series')

    def test_form_save(self):
        superform = PostForm({
            'title': 'New blog post',
            'form-series-title': 'Unrelated series',
        })
        superform.save()

        self.assertEqual(Series.objects.count(), 1)
        series = Series.objects.get()

        self.assertEqual(series.title, 'Unrelated series')

        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.get()
        self.assertEqual(post.title, 'New blog post')

        # The relation between post and series IS NOT done by the
        # ModelFormField. It only takes care of nesting. The relation can be
        # handled with the ModelFormField subclasses like ForeignKeyFormField.
        self.assertEqual(post.series, None)

    def test_override_get_instance(self):
        existing_series = Series.objects.create(title='Existing series')

        superform = UseExistingSeriesPostForm()
        self.assertEqual(superform.forms['existing_series'].instance,
                         existing_series)
        self.assertEqual(superform.forms['existing_series']['title'].value(),
                         'Existing series')

    def test_save_existing_instance(self):
        existing_series = Series.objects.create(title='Existing series')

        superform = UseExistingSeriesPostForm({
            'title': 'Blog post',
            'form-existing_series-title': 'Changed name',
        })
        superform.save()

        changed_series = Series.objects.get()
        self.assertEqual(changed_series.pk, existing_series.pk)
        self.assertEqual(changed_series.title, 'Changed name')

    def test_required(self):
        form = PostForm({
            'title': 'New blog post',
            'form-series-title': '',
        })
        form.full_clean()

        self.assertFalse(form.is_valid())
        self.assertTrue('required' in str(form.errors['series']['title']))

        # Test when key is not in data.
        form = PostForm({
            'title': 'New blog post',
        })
        form.full_clean()

        self.assertFalse(form.is_valid())
        self.assertTrue('required' in str(form.errors['series']['title']))

    def test_not_required(self):
        form = UnrequiredSeriesPostForm({
            'title': 'New blog post',
            'form-series-title': '',
        })
        form.full_clean()

        self.assertTrue(form.is_valid())

        form.save()
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Series.objects.count(), 0)
