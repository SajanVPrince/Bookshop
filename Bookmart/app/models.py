from django.db import models
from django.contrib.auth.models import *

class Books(models.Model):
    bk_id=models.TextField()
    name=models.TextField()
    ath_name=models.TextField()
    bk_genres=models.TextField()
    price=models.IntegerField()
    ofr_price=models.IntegerField()
    stock=models.IntegerField()
    img=models.FileField()
    dis=models.TextField()


class Userdtl(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    phone=models.IntegerField()
    fullname=models.TextField()
    city=models.TextField()
    state=models.TextField()
    altphone=models.IntegerField()
    landmark=models.TextField()
    adress=models.TextField()
    pincode=models.IntegerField()

class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Books,on_delete=models.CASCADE)


class Favorite(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Books,on_delete=models.CASCADE)


class Buys(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Books,on_delete=models.CASCADE)
    address=models.ForeignKey(Userdtl,on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

class Buy(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Canceled', 'Canceled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Books, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=50, 
        choices=STATUS_CHOICES, 
        default='Pending'
    )
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return f"{self.product.name} ({self.status})"
    

class Order(models.Model):
    buy = models.OneToOneField(Buy, on_delete=models.SET_NULL, null=True, blank=True)  # # Link Order to Buy
    customer_name = models.CharField(max_length=100)

    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Allows null values
    email = models.EmailField()
    address = models.TextField(blank=True, null=True)  # Allows null values
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order by {self.customer_name} on {self.created_at}"
    

class Review(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    review=models.TextField()