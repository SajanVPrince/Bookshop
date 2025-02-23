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

class Review(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    review=models.TextField()