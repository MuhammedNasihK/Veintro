from django.db import models

# Create your models here.


from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=250,unique=True,blank=True,null=True)

    def __str__(self):
        return self.name
    

class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='brand_logo/',null=True,blank=True)

    def __str__(self):
        return self.name 
    


class Product(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE)
    added_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Attribute(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    

class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute,on_delete=models.CASCADE)
    value = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.attribute} - {self.value}"
    


class ProductVariant(models.Model):
    product = models.ForeignKey(Product,on_delete = models.CASCADE)
    colour = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    discount_price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    stock = models.PositiveIntegerField(default=0)
    attribute = models.ManyToManyField(AttributeValue,related_name='variants')

    
    

class Specification(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    spec = models.CharField(max_length=200)
    value = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.spec} - {self.value}"
    

class ProductImage(models.Model):
    variant = models.ForeignKey(ProductVariant,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_image/')