from django.db import models
from admin_panel.models import *
from django.conf import settings


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='wishlist')
    product_variant = models.ForeignKey('admin_panel.ProductVariant',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','product_variant')

    def __str__(self):
        return f"{self.user.email} - {self.product_variant.product.name}"
    

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    primary_mobile_number = models.CharField(max_length=14,null=True,blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/',null=True,blank=True)

    def __str__(self):
        return f"{self.user.email}'s Profile"
    

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    full_name = models.CharField(max_length=250)
    mobile_number = models.CharField(max_length=14)
    pincode = models.CharField(max_length=10)
    flat = models.CharField(max_length=250,verbose_name="Flat, House no., Building, Company, Apartment")
    area = models.CharField(max_length=250,verbose_name="Area, Street, Sector, Village")
    landmark = models.CharField(max_length=250,blank=True,null=True)
    city = models.CharField(max_length=250,verbose_name='Town/City')
    state = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username}-{self.city}"
    


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    variant = models.ForeignKey('admin_panel.ProductVariant',on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)




class Order(models.Model):
    STATUS_CHOICE = (
        ('Pending','Pending'),
        ('Shipped','Shipped'),
        ('Delivered','Delivered'),
        ('Cancelled','Cancelled')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    # Address -->

    full_name = models.CharField(max_length=250)
    mobile_number = models.CharField(max_length=14)
    pincode = models.CharField(max_length=10)
    flat = models.CharField(max_length=250,verbose_name="Flat, House no., Building, Company, Apartment")
    area = models.CharField(max_length=250,verbose_name="Area, Street, Sector, Village")
    landmark = models.CharField(max_length=250,blank=True,null=True)
    city = models.CharField(max_length=250,verbose_name='Town/City')
    state = models.CharField(max_length=100)

    total_amount = models.DecimalField(max_digits=12,decimal_places=2)
    status = models.CharField(choices=STATUS_CHOICE,default='Pending')
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.email} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant,on_delete=models.CASCADE)

    product_name = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=12,decimal_places=2)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=15,decimal_places=2)


    def total_price(self):
        return f"{self.quantity} X {self.variant.product.name} (Order #{self.order.pk})"

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('Pending',"Pending"),
        ('Success',"Success"),
        ('Failed',"Failed")
    )

    order = models.OneToOneField(Order,on_delete=models.CASCADE)
    razorpay_payment_link_id = models.CharField(max_length=250)
    razorpay_payment_id = models.CharField(max_length=200)
    payment_status = models.CharField(max_length=100,choices=PAYMENT_STATUS)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    payment_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for order #{self.order.pk} - {self.payment_status}"
    
