from django.db import models
from category.models import Category
from django.urls import reverse

#for auto slug setting
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Create your models here.


class Product(models.Model):
    product_name    = models.CharField(max_length=200, unique=True)
    slug            = models.SlugField(max_length=200, unique=True)
    description     = models.TextField(max_length=500, blank=True)
    brand           = models.TextField(max_length=500, blank=True)
    price           = models.IntegerField(default=0)
    mrp_price       = models.IntegerField(default=0)
    url_height      = models.PositiveIntegerField(default = 150)
    url_width       = models.PositiveIntegerField(default = 75)
    images          = models.ImageField(upload_to='photos/products',height_field='url_height', width_field='url_width')
    stock           = models.IntegerField()
    is_available    = models.BooleanField(default=True)
    category        = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.product_name

    def get_url(self):
        return reverse('product_details',args=[self.category.slug,self.slug])


variation_category_choice = (
    ('color','color'),
    ('size','size'),
)
    

class VariationManager(models.Manager):

    def colors(self):
        return super(VariationManager , self).filter(variation_category = 'color' , is_active = True)

    def sizes(self):
        return super(VariationManager , self).filter(variation_category = 'size' , is_active = True)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value     = models.CharField(max_length=100)
    is_active           = models.BooleanField(default=True)
    created_date        = models.DateTimeField(auto_now=True)

    object = VariationManager()

    def __str__(self):
        return self.variation_value

@receiver(pre_save , sender = Product)
def category_slug_creator(sender, instance ,*args, **kwargs):
    if not instance.slug :
        instance.slug = slugify(instance.product_name)