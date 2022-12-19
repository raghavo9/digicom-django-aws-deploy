from django.db import models
from django.urls import reverse

#for auto slug setting
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=100,unique=True)
    slug = models.SlugField(max_length=50,unique=True)
    description = models.TextField(max_length=255,blank=True)
    cat_image = models.ImageField(upload_to='photos/categories',blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.category_name

    def get_url(self):
        return reverse('product_by_category',args=[self.slug])


@receiver(pre_save , sender = Category)
def category_slug_creator(sender, instance ,*args, **kwargs):
    if not instance.slug :
        instance.slug = slugify(instance.category_name)