from django.db import models


class Series(models.Model):
    """
    Multiple posts can be grouped into a series.
    """

    title = models.CharField(max_length=50)


class Post(models.Model):
    """
    A blog post. I can be part of a series and can contain multiple images.
    """

    title = models.CharField(max_length=50)
    series = models.ForeignKey('Series', null=True, blank=True)


class Image(models.Model):
    post = models.ForeignKey('Post', related_name='images')

    name = models.CharField(max_length=50)
    position = models.PositiveIntegerField(default=0)

    # Is no ImageField to make testing easier.
    image_url = models.URLField()

    class Meta:
        ordering = ('position',)
