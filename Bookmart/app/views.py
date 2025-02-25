from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import *
from .models import *
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
import razorpay
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from django.urls import reverse


def bk_login(req):
    if 'user' in req.session:
        return redirect(userpro)
    if 'shop' in req.session:
        return redirect(adminpro)
    if req.method=='POST':
        uname=req.POST['uname']
        password=req.POST['password']
        data=authenticate(username=uname,password=password)
        if data:
            if data.is_superuser:
                login(req,data)
                req.session['shop']=uname
                return redirect(adhome)
            else:
                login(req,data)
                req.session['user']=uname
                req.session['user1']= data.id
                return redirect(bk_home)
        else:
            messages.warning(req,"Invalid uname or password")
            return redirect(bk_login)
    else:
        return render(req,'login.html')

def bk_logout(req):
    req.session.flush()          
    logout(req)
    return redirect(bk_login)


def register(req):
    if req.method == 'POST':
        fname = req.POST['fname']
        email = req.POST['email']
        password = req.POST['password']
        if User.objects.filter(email=email).exists():
            messages.warning(req, "Email already registered")
            return redirect('register')
        otp = get_random_string(length=6, allowed_chars='0123456789')
        req.session['otp'] = otp
        req.session['email'] = email
        req.session['fname'] = fname
        req.session['password'] = password
        send_mail(
            'Your OTP Code',
            f'Your OTP is: {otp}',
            settings.EMAIL_HOST_USER, [email]
        )
        messages.success(req, "OTP sent to your email")
        return redirect('verify_otp_reg')
    return render(req, 'register.html')

def verify_otp_reg(req):
    if req.method == 'POST':
        entered_otp = req.POST['otp'] 
        stored_otp = req.session.get('otp')
        email = req.session.get('email')
        fname = req.session.get('fname')
        password = req.session.get('password')
        if entered_otp == stored_otp:
            user = User.objects.create_user(first_name=fname,email=email,password=password,username=email)
            user.is_verified = True
            user.save()      
            messages.success(req, "Registration successful! You can now log in.")
            send_mail('User Registration Succesfull', 'Account Created Succesfully And Welcome To Bookmart', settings.EMAIL_HOST_USER, [email])
            return redirect('login')
        else:
            messages.warning(req, "Invalid OTP. Try again.")
            return redirect('verify_otp_reg')

    return render(req, 'verify_oto_reg.html')

def resend_otp_reg(req):
    email = req.session.get('email')
    if email:
        otp = get_random_string(length=6, allowed_chars='0123456789')
        req.session['otp'] = otp
        
        send_mail(
            'Your New OTP Code',
            f'Your OTP is: {otp}',
            settings.EMAIL_HOST_USER, [email]
        )
        messages.success(req, "OTP resent to your email")
    
    return redirect('verify_otp_reg')
        
def forgetpassword(req):
    if req.method == 'POST':
        email = req.POST['email']
        try:
            user = User.objects.get(email=email)
            otp = get_random_string(length=6, allowed_chars='0123456789')
            req.session['otp'] = otp
            req.session['email'] = email
            send_mail('Password Reset OTP', f'Your OTP is: {otp}', settings.EMAIL_HOST_USER, [email])
            messages.success(req, "OTP sent to your email")
            return redirect('verify_otp')
        except User.DoesNotExist:
            messages.warning(req, "Email not found")
            return redirect('forgetpassword')
    return render(req, 'forgetpassword.html')

def verify_otp(req):
    if req.method == 'POST':
        otp = req.POST['otp']
        if otp == req.session.get('otp'):
            return redirect('resetpassword')
        else:
            messages.warning(req, "Invalid OTP")
            return redirect('verify_otp')
    return render(req, 'verify_otp.html')

def resend_otp(req):  
    email = req.session.get('email')
    if email:
        otp = get_random_string(length=6, allowed_chars='0123456789')
        req.session['otp'] = otp
        send_mail('Password Reset OTP', f'Your OTP is: {otp}', settings.EMAIL_HOST_USER, [email])
        messages.success(req, "OTP resent to your email")
    return redirect('verify_otp')

def resetpassword(req):
    if req.method == 'POST':
        password = req.POST['password']  
        email = req.session.get('email')
        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            messages.success(req, "Password reset successfully")
            return redirect('login')
        except User.DoesNotExist:
            messages.warning(req, "Error resetting password")
            return redirect('resetpassword')
    return render(req, 'resetpassword.html')


def search_view(request):
    query = request.GET.get('q', '') 
    if query:
        results = Books.objects.filter(name__icontains=query) # Case-insensitive search
    else:
        results = [] 
        results1 = []
    return render(request, 'users/search.html', {'results': results, 'query': query})

# -----ADMIN----

def adminpro(req):
    return render(req,'admin/adminprofile.html')

def adhome(req):
    if req.method=='POST':
        name=req.POST['name']
        ath_name=req.POST['ath_name']
        price=req.POST['price']
        ofr_price=req.POST['ofr_price']
        bk_genres=req.POST['bk_genres']
        img=req.FILES['img']
        dis=req.POST['dis']
        stock=req.POST['stock']
        data=Books.objects.create(name=name,ath_name=ath_name,price=price,ofr_price=ofr_price,bk_genres=bk_genres,img=img,dis=dis,stock=stock)
        data.save()
        return redirect(adhome)
    else:
        return render(req,'admin/admin.html')
    
def sdrama(req):
    data=Books.objects.filter(bk_genres='drama')[::-1]
    return render(req,'admin/books/sdrama.html',{'data':data})

def slove(req):
    data=Books.objects.filter(bk_genres='love')[::-1]
    return render(req,'admin/books/slove.html',{'data':data})

def sfantacy(req):
    data=Books.objects.filter(bk_genres='fantasy')[::-1]
    return render(req,'admin/books/sfantacy.html',{'data':data})

def sscifi(req):
    data=Books.objects.filter(bk_genres='sci-fi')[::-1]
    return render(req,'admin/books/sscifi.html',{'data':data})

def sothers(req):
    data=Books.objects.filter(bk_genres='others')[::-1]
    return render(req,'admin/books/sothers.html',{'data':data})   

def delete_sdrama(req,id):
    book=Books.objects.get(pk=id)
    book.delete()
    return redirect(sdrama) 

def delete_slove(req,id):
    book=Books.objects.get(pk=id)
    book.delete()
    return redirect(slove) 

def delete_sscifi(req,id):
    book=Books.objects.get(pk=id)
    book.delete()
    return redirect(sscifi) 

def delete_sfantacy(req,id):
    book=Books.objects.get(pk=id)
    book.delete()
    return redirect(sfantacy) 

def delete_sothers(req,id):
    book=Books.objects.get(pk=id)
    book.delete()
    return redirect(sothers) 
    

def edit_sdrama(req, id):
    if 'shop' in req.session:
        data = Books.objects.get(pk=id)
        if req.method == 'POST':
            bk_name = req.POST['bk_name']
            ath_name = req.POST['ath_name']
            bk_price = req.POST['bk_price']
            bk_ofr_price = req.POST['bk_ofr_price']
            bk_genres = req.POST['bk_genres']
            img = req.FILES.get('img') 
            bk_dis = req.POST['bk_dis']
            stock = req.POST['stock']
            data.name = bk_name
            data.ath_name = ath_name
            data.price = bk_price
            data.ofr_price = bk_ofr_price
            data.bk_genres = bk_genres
            data.dis = bk_dis
            data.stock = stock
            if img:
                data.img = img
            data.save() 
            return redirect(sdrama)  
        else:
            return render(req, 'admin/dramaedit.html', {'data': data})
    else:
        return redirect('bk_login')

def edit_slove(req, id):
    if 'shop' in req.session:
        data = Books.objects.get(pk=id)
        if req.method == 'POST':
            bk_name = req.POST['bk_name']
            ath_name = req.POST['ath_name']
            bk_price = req.POST['bk_price']
            bk_ofr_price = req.POST['bk_ofr_price']
            bk_genres = req.POST['bk_genres']
            img = req.FILES.get('img') 
            bk_dis = req.POST['bk_dis']
            stock = req.POST['stock']
            data.name = bk_name
            data.ath_name = ath_name
            data.price = bk_price
            data.ofr_price = bk_ofr_price
            data.bk_genres = bk_genres
            data.dis = bk_dis
            data.stock = stock
            if img:
                data.img = img
            data.save() 
            return redirect(slove)  
        else:
            return render(req, 'admin/loveedit.html', {'data': data})
    else:
        return redirect('bk_login')  
    
def edit_sfantacy(req, id):
    if 'shop' in req.session:
        data = Books.objects.get(pk=id)
        if req.method == 'POST':
            bk_name = req.POST['bk_name']
            ath_name = req.POST['ath_name']
            bk_price = req.POST['bk_price']
            bk_ofr_price = req.POST['bk_ofr_price']
            bk_genres = req.POST['bk_genres']
            img = req.FILES.get('img') 
            bk_dis = req.POST['bk_dis']
            stock = req.POST['stock']
            data.name = bk_name
            data.ath_name = ath_name
            data.price = bk_price
            data.ofr_price = bk_ofr_price
            data.bk_genres = bk_genres
            data.dis = bk_dis
            data.stock = stock
            if img:
                data.img = img
            data.save() 
            return redirect(sfantacy)  
        else:
            return render(req, 'admin/fantacyedit.html', {'data': data})
    else:
        return redirect('bk_login')

def edit_sscifi(req, id):
    if 'shop' in req.session:
        data = Books.objects.get(pk=id)
        if req.method == 'POST':
            bk_name = req.POST['bk_name']
            ath_name = req.POST['ath_name']
            bk_price = req.POST['bk_price']
            bk_ofr_price = req.POST['bk_ofr_price']
            bk_genres = req.POST['bk_genres']
            img = req.FILES.get('img') 
            bk_dis = req.POST['bk_dis']
            stock = req.POST['stock']
            data.name = bk_name
            data.ath_name = ath_name
            data.price = bk_price
            data.ofr_price = bk_ofr_price
            data.bk_genres = bk_genres
            data.dis = bk_dis
            data.stock = stock
            if img:
                data.img = img
            data.save() 
            return redirect(sscifi)  
        else:
            return render(req, 'admin/scifiedit.html', {'data': data})
    else:
        return redirect('bk_login')
    
def edit_sothers(req, id):
    if 'shop' in req.session:
        data = Books.objects.get(pk=id)
        if req.method == 'POST':
            bk_name = req.POST['bk_name']
            ath_name = req.POST['ath_name']
            bk_price = req.POST['bk_price']
            bk_ofr_price = req.POST['bk_ofr_price']
            bk_genres = req.POST['bk_genres']
            img = req.FILES.get('img') 
            bk_dis = req.POST['bk_dis']
            stock = req.POST['stock']
            data.name = bk_name
            data.ath_name = ath_name
            data.ofr_price = bk_ofr_price
            data.bk_genres = bk_genres
            data.dis = bk_dis
            data.stock = stock
            if img:
                data.img = img
            data.save() 
            return redirect(sothers)  
        else:
            return render(req, 'admin/othersedit.html', {'data': data})
    else:
        return redirect('bk_login')
    
def view_user(req):
    if 'shop' in req.session:
        data=User.objects.all()
        return render(req,'admin/users.html',{'data':data})
    else:
        return redirect(bk_login)
    
def delete_user(req,id):
    user=User.objects.get(pk=id)
    user.delete()
    return redirect(view_user)

def view_review(req):
    if 'shop' in req.session:
        data=Review.objects.all()
        return render(req,'admin/review.html',{'data':data})
    else:
        return redirect(bk_login)
    
def delete_review(req,id):
    review=Review.objects.get(pk=id)
    review.delete()
    return redirect(view_review)

def view_buy(req):
    if 'shop' in req.session:
        data=Buy.objects.all()
        return render(req,'admin/buy.html',{'data':data})
    else:
        return redirect(bk_login)
    
def viewbookingdetails(request, buy_id):
    buy = get_object_or_404(Buy, id=buy_id)
    return render(request, 'admin/viewbookingdetails.html', {'buy': buy})

def delete_booking(request, buy_id):
    buy = Buy.objects.get(pk=buy_id)
    buy.delete()
    return redirect(view_buy)


def update(req):
    if req.method == "POST":
        for key, value in req.POST.items():
            if key.startswith('status_'):
                buy_id = key.split('_')[1]
                try:
                    buy = Buy.objects.get(id=buy_id)
                    if buy.status != value:
                        buy.status = value
                        buy.save()
                        # Create or update the associated order
                        order, created = Order.objects.get_or_create(buy=buy)
                        order.customer_name = buy.user.username
                        order.phone_number = buy.user.userprofile.phone_number if hasattr(buy.user, 'userprofile') else "N/A"
                        order.email = buy.user.email if buy.user.email else "N/A"
                        order.address = buy.user.userprofile.address if hasattr(buy.user, 'userprofile') else "N/A"
                        order.save()

                        # Add success message
                        messages.success(req, f"Order {buy_id} status updated to {value}.")
                    else:
                        messages.info(req, f"Order {buy_id} status is already {value}.")
                except Buy.DoesNotExist:
                    messages.error(req, f"Order {buy_id} not found.")
        return redirect(update)

    # Fetch Buy objects and their associated Orders
    buys = Buy.objects.all().order_by('-date')
    combined_data = []

    for buy in buys:
        order = Order.objects.filter(buy=buy).first()  # Get the correct order linked to this Buy
        
        # Ensure there's always an order linked to Buy
        if not order:
            order = Order.objects.create(
                buy=buy,
                customer_name=buy.user.username,
                phone_number=buy.user.userprofile.phone_number if hasattr(buy.user, 'userprofile') else "N/A",
                email=buy.user.email if buy.user.email else "N/A",
                address=buy.user.userprofile.address if hasattr(buy.user, 'userprofile') else "N/A",
            )

        combined_data.append({'buy': buy, 'order': order})

    return render(req, 'admin/update.html', {'combined_data': combined_data})

def create_order(request, buy_id):
    try:
        # Get the Buy object using the buy_id
        buy = Buy.objects.get(id=buy_id)
    except Buy.DoesNotExist:
        messages.error(request, "The specified order could not be found.")
        return redirect(update)

    # Check if an Order already exists for this Buy
    order = Order.objects.filter(buy=buy).first()

    if order:
        # If an order already exists, notify the user and do not create a duplicate order
        messages.info(request, f"An order already exists for {buy.product.name}. No duplicate created.")
    else:
        # If no order exists, create a new Order
        try:
            # Get user details from the userprofile (or provide default values if profile is missing)
            user_profile = buy.user.userprofile if hasattr(buy.user, 'userprofile') else None
            phone_number = user_profile.phone_number if user_profile else "N/A"
            address = user_profile.address if user_profile else "N/A"
            email = buy.user.email if buy.user.email else "N/A"
            
            # Create new order linked to this Buy
            order = Order.objects.create(
                buy=buy,
                customer_name=buy.user.username,
                phone_number=phone_number,
                email=email,
                address=address,
            )
            messages.success(request, f"Order for {buy.product.name} created successfully!")
        except Exception as e:
            messages.error(request, f"Error occurred while creating the order: {str(e)}")
            return redirect(update)

    return redirect(update)


# ---USER------


def bk_home(req):
    data=Books.objects.filter(bk_genres='drama')[::-1][:4]
    data1=Books.objects.filter(bk_genres='sci-fi')[::-1][:4]
    data2=Books.objects.filter(bk_genres='love')[::-1][:4]
    data3=Books.objects.filter(bk_genres='fantasy')[::-1][:4]
    data5=Books.objects.filter(bk_genres='others')[::-1][:4]
    if 'user' in req.session:
        if req.method=='POST':
            user=User.objects.get(username=req.session['user'])
            review=req.POST['review']
            data4=Review.objects.create(user=user,review=review)
            data4.save()
            messages.success(req,"Thanks for your complements")
    
    rev=Review.objects.all()[::-1]
    return render(req,'users/home.html',{'data':data,'data1':data1,'data2':data2,'data3':data3,'data5':data5,'data4':rev})

def drama(req):
    data=Books.objects.filter(bk_genres='drama')[::-1]
    return render(req,'users/books/drama.html',{'data':data})

def love(req):
    data=Books.objects.filter(bk_genres='love')[::-1]
    return render(req,'users/books/love.html',{'data':data})

def fantacy(req):
    data=Books.objects.filter(bk_genres='fantasy')[::-1]
    return render(req,'users/books/fantacy.html',{'data':data})

def scifi(req):
    data=Books.objects.filter(bk_genres='sci-fi')[::-1]
    return render(req,'users/books/sci-fi.html',{'data':data})

def others(req):
    data=Books.objects.filter(bk_genres='others')[::-1]
    return render(req,'users/books/others.html',{'data':data})

def view_prod(req,id):
    data=Books.objects.get(pk=id)
    return render(req,'users/viewprod.html',{'data':data})

def userpro(req):
    if 'user' in req.session:
        user = User.objects.get(username=req.session['user'])
        data1 = Userdtl.objects.filter(user=user)
        
        if req.method == 'POST' and 'name' in req.POST:
            name = req.POST['name']
            phn = req.POST['phn']
            altphn = req.POST['altphn']
            pin = req.POST['pin']
            land = req.POST['land']
            adrs = req.POST['adrs']
            city = req.POST['city']
            state = req.POST['state']
            
            existing_address = Userdtl.objects.filter(
                user=user,
                fullname=name,
                phone=phn,
                altphone=altphn,
                pincode=pin,
                landmark=land,
                adress=adrs,
                city=city,
                state=state
            ).first()

            if not existing_address:
                data = Userdtl.objects.create(
                    user=user,
                    fullname=name,
                    phone=phn,
                    pincode=pin,
                    landmark=land,
                    adress=adrs,
                    city=city,
                    state=state,
                    altphone=altphn
                )
                data.save()
            return redirect(userpro)
        elif req.method == 'POST' and 'oldpass' in req.POST:
            old_pass = req.POST['oldpass']
            new_pass = req.POST['newpass']
            if user.check_password(old_pass):
                user.set_password(new_pass)
                user.save()
                messages.success(req, "Password changed successfully")
                return redirect(userpro)
            else:
                messages.warning(req, "Old password is incorrect")
                return redirect(userpro)
        
        else:
            return render(req, 'users/userprofile.html', {'data': user, 'data1': data1})
    
    else:
        return redirect('bk_login')

    
def change_pass(req):
    if 'user' in req.session:
        if req.method=='POST':
            user=User.objects.get(username=req.session['user'])
            old_pass=req.POST['oldpass']
            new_pass=req.POST['newpass']
            if user.check_password(old_pass):
                user.set_password(new_pass)
                user.save()
                messages.success(req,"Password changed successfully")
                return redirect(userpro)
            else:
                messages.warning(req,"Old password is incorrect")
                return redirect(change_pass)
        else:
            return render(req,'users/changepass.html')
    else:
        return redirect(bk_login)
    
def add_to_cart(req,pid):
    if 'user' in req.session:
        prod=Books.objects.get(pk=pid)
        user=User.objects.get(username=req.session['user'])
        data=Cart.objects.create(user=user,product=prod)
        data.save()
        return redirect(viewcart)
    else:
        return redirect(bk_login)

    
def viewcart(req):
    if 'user' in req.session:
        user = User.objects.get(username=req.session['user'])
        cart = Cart.objects.filter(user=user)
        total_price = sum([item.product.ofr_price for item in cart])
        total_discount = sum([item.product.price - item.product.ofr_price for item in cart]) 
        return render(req, 'users/cart.html', {
            'data': cart, 
            'total_price': total_price,
            'total_discount': total_discount
        })
    else:
        return redirect('bk_login')
    
def delete_cart(req,id):
    cart=Cart.objects.get(pk=id)
    cart.delete()
    return redirect(viewcart)

def addfav(req,bid):
    if 'user' in req.session:
        prod=Books.objects.get(pk=bid)
        user=User.objects.get(username=req.session['user'])
        data=Favorite.objects.create(user=user,product=prod)
        data.save()
        return redirect(viewfav)
    else:
        return redirect(bk_login)
    
def viewfav(req):
    if 'user' in req.session:
        user=User.objects.get(username=req.session['user'])
        data=Favorite.objects.filter(user=user)
        return render(req,'users/favorite.html',{'fav':data})
    else:
        return redirect (bk_login)

def deletefavs(request, pk):
    if request.user.is_authenticated:
        user = request.user
        favorite = get_object_or_404(Favorite, user=user, product__pk=pk)
        favorite.delete()
        return redirect(viewfav)
    else:
        return redirect('login')


def view_odrs(req):
    if 'user' in req.session:
        user=User.objects.get(username=req.session['user'])
        buy=Buy.objects.filter(user=user)
        return render (req,'users/myoders.html',{'data':buy})
    else:
        return redirect(bk_login)
    

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

def product_buy(req, id):
    if 'user' in req.session:
        user = User.objects.get(username=req.session['user'])
        saved_addresses = Userdtl.objects.filter(user=user)
        prod = None
        try:
            prod = Books.objects.get(pk=id)
        except Books.DoesNotExist:
            return redirect('home')
        if req.method == 'POST':
            if 'address_id' in req.POST:
                selected_address_id = req.POST['address_id']
                user_address = Userdtl.objects.get(id=selected_address_id)
            else:
                fullname = req.POST['fullname']
                address = req.POST['adress']
                pincode = req.POST['pincode']
                city = req.POST['city']
                state = req.POST['state']
                phone = req.POST['phone']
                altphone = req.POST['altphone']
                landmark = req.POST['landmark']
                
                user_address = Userdtl.objects.create(
                    user=user,
                    phone=phone,
                    fullname=fullname,
                    city=city,
                    state=state,
                    altphone=altphone,
                    landmark=landmark,
                    adress=address,
                    pincode=pincode
                )
                user_address.save()
            order = Buy.objects.create(
                user=user,
                product=prod,
                quantity=1,
                status='Pending',  
            )

            order_amount = int(prod.ofr_price * 100)  
            order_currency = "INR"
            order_receipt = f"order_rcpt_{order.id}"

            razorpay_order = razorpay_client.order.create({
                "amount": order_amount,
                "currency": order_currency,
                "receipt": order_receipt,
                "payment_capture": 1
            })
            order.razorpay_order_id = razorpay_order['id']
            order.save()
            order_data = {
                'cart': [{'product': prod.id, 'quantity': 1}],
                'selected_address': {
                    'fullname': user_address.fullname,
                    'address': user_address.adress,
                    'city': user_address.city,
                    'state': user_address.state,
                    'pincode': user_address.pincode,
                    'phone': user_address.phone,
                    'altphone': user_address.altphone,
                    'landmark': user_address.landmark,
                },
                'total_price': prod.ofr_price,
                'total_discount': prod.price - prod.ofr_price
            }
            req.session['order_data'] = order_data
            return redirect(reverse('create_razorpay_order', args=[order.id]))

        return render(req, 'users/buypage.html', {'prod': prod, 'saved_addresses': saved_addresses})

    else:
        return redirect('bk_login')


def create_razorpay_order(request, buy_id):
    buy = get_object_or_404(Buy, id=buy_id)
    
    order_amount = int(buy.product.ofr_price * 100)  
    razorpay_order = razorpay_client.order.create({
        "amount": order_amount,
        "currency": "INR",
        "receipt": f"order_rcpt_{buy.id}",
        "payment_capture": 1
    })

    buy.razorpay_order_id = razorpay_order['id']
    buy.save()
    display_amount = order_amount / 100

    return render(request, 'users/payment.html', {
        'order_id': razorpay_order['id'],
        'amount': display_amount,  
        'key': settings.RAZORPAY_KEY_ID,
    })

def buy_cart(request):
    # Ensure the user is logged in
    user = User.objects.get(username=request.session['user'])
    
    # Get the user's cart
    cart = Cart.objects.filter(user=user)
    # In your view
    total_price = sum([item.product.ofr_price for item in cart])
    total_discount = sum([item.product.price - item.product.ofr_price for item in cart])

    # Multiply the total_price in the view
    total_price_in_paise = total_price * 100


    # Get the saved addresses of the user
    saved_addresses = Userdtl.objects.filter(user=user)

    # If no saved addresses, prompt the user to add one
    if not saved_addresses:
        return render(request, 'users/checkout.html', {
            'cart': cart,
            'total_price': total_price,
            'total_discount': total_discount,
            'saved_addresses': saved_addresses,
            'address_message': 'Please add an address in your profile before proceeding with the order.'
        })

    # Handling POST request to select an address and proceed
    if request.method == 'POST':
        selected_address = None
        
        # Check if an address has been selected
        if 'address_id' in request.POST:
            selected_address = Userdtl.objects.get(id=request.POST['address_id'])
        
        # If no address is selected, show an error message
        if not selected_address:
            return render(request, 'users/checkout.html', {
                'cart': cart,
                'total_price': total_price,
                'total_discount': total_discount,
                'saved_addresses': saved_addresses,
                'address_message': 'Please select an existing address to proceed with your order.'
            })
        
        # Proceed with creating the Buy model instance for each product in the cart
        buy_instances = []  # Store created Buy instances to check the result

        for item in cart:
            # Create a Buy instance for each product in the cart
            buy_instance = Buy(
                user=user,
                product=item.product,
                quantity=1,  # Assuming quantity of 1 for each item in the cart
                status='Pending',
                razorpay_order_id=None,  # This will be updated with Razorpay order ID later
                payment_status='Pending'
            )
            buy_instance.save()  # Save each Buy instance
            buy_instances.append(buy_instance)  # Add to the list to check if anything was created

        # If no Buy instances were created, return an error
        if not buy_instances:
            return render(request, 'users/checkout.html', {
                'cart': cart,
                'total_price': total_price,
                'total_discount': total_discount,
                'saved_addresses': saved_addresses,
                'address_message': 'No items in your cart to proceed with the order.'
            })

        # Clear the cart after order creation
        cart.delete()

        # Create Razorpay Order
        razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

        # Create the Razorpay order
        razorpay_order = razorpay_client.order.create({
            'amount': int(total_price * 100),  # Amount should be in paise
            'currency': 'INR',
            'payment_capture': '1'
        })

        razorpay_order_id = razorpay_order['id']

        # Update the order with the Razorpay order ID
        for buy_instance in buy_instances:
            buy_instance.razorpay_order_id = razorpay_order_id
            buy_instance.save()

        # Store order data in session for confirmation page (optional)
        order_data = {
            'cart': list(cart.values()),
            'selected_address': {
                'fullname': selected_address.fullname,
                'address': selected_address.adress,
                'city': selected_address.city,
                'state': selected_address.state,
                'pincode': selected_address.pincode,
                'phone': selected_address.phone,
                'altphone': selected_address.altphone,
                'landmark': selected_address.landmark,
            },
            'total_price': total_price,
            'total_discount': total_discount,
            'razorpay_order_id': razorpay_order_id
        }
        request.session['order_data'] = order_data

        # Redirect to the Razorpay payment page
        return redirect(f'/checkout/payment/{razorpay_order_id}/')

    # Rendering the checkout page with available addresses
    return render(request, 'users/checkout.html', {
        'cart': cart, 
        'total_price': total_price, 
        'total_discount': total_discount,
        'saved_addresses': saved_addresses,
        'address_message': None  # No error message when the page is first loaded
    })
def razorpay_payment(request, order_id):
    # Fetch all Buy objects with the same razorpay_order_id
    buys = Buy.objects.filter(razorpay_order_id=order_id)
    
    if not buys.exists():
        return redirect(bk_home)  # If no orders found, redirect home or show error
    
    # Calculate the total price for all items in the cart
    total_price = sum([buy.product.ofr_price * buy.quantity for buy in buys])
    total_discount = sum([buy.product.price - buy.product.ofr_price for buy in buys])

    # User details
    user = buys.first().user
    name = user.username
    email = user.email

    # Razorpay key ID from settings
    razorpay_key_id = settings.RAZORPAY_KEY_ID

    return render(request, 'users/razorpay_payment.html', {
        'name': name,
        'email': email,
        'total_price': total_price,
        'total_discount': total_discount,
        'razorpay_order_id': order_id,
        'razorpay_key_id': razorpay_key_id,
    })

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

def payment_success(request):
    if request.method == "POST":
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_signature = request.POST.get("razorpay_signature")

        try:
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature
            }
            razorpay_client.utility.verify_payment_signature(params_dict)
            buy = Buy.objects.get(razorpay_order_id=razorpay_order_id)
            buy.payment_status = "Paid"
            buy.save()

            buy.payment_id = razorpay_payment_id
            buy.save()

            messages.success(request, "Payment successful! Your order is now confirmed.")
            
            return redirect('order_success', buy_id=buy.id)

        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed! Please try again.")
            return redirect('order_failed')  

    return JsonResponse({"error": "Invalid request"}, status=400)
    
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

def cancel_order(request, buy_id):
    if 'user' in request.session:
        try:
            buy = Buy.objects.get(id=buy_id)
            product = buy.product

            if buy.status == "Pending":
                buy.status = "Canceled"
                buy.save()

                product.stock += buy.quantity
                product.save()
                if buy.payment_status == "Paid":
                    try:
                        refund = razorpay_client.payment.refund(buy.payment_id)
                        messages.success(request, "Order canceled successfully and refund initiated.")
                    except razorpay.errors.RazorpayError as e:
                        messages.error(request, f"Error while processing the refund: {str(e)}")
                else:
                    messages.success(request, "Order canceled successfully.")

            else:
                messages.warning(request, "You cannot cancel an order that is already shipped or delivered.")

        except Buy.DoesNotExist:
            messages.warning(request, "Order not found.")
            return redirect(view_odrs)  

        return redirect(view_odrs)  

    else:
        return redirect('bk_login')
    
def delete_order(request, order_id):
    try:
        order = Buy.objects.get(id=order_id)
        order.delete()
        return redirect(view_odrs)  
    except Buy.DoesNotExist:
        return redirect(view_odrs)
    
def view_booking_details(req, id):
    if 'user' in req.session:
        user = User.objects.get(username=req.session['user'])
        try:
            booking = Buy.objects.get(user=user, pk=id) 
        except Buy.DoesNotExist:
            return redirect('some_error_page') 
        
        return render(req, 'users/viewbookingdetails.html', {'booking': booking})
    else:
        return redirect('bk_login')


def order_success(request, buy_id):
    # Retrieve the successful buy order
    buy = Buy.objects.get(id=buy_id)

    return render(request, 'users/order_success.html', {
        'buy': buy,
    })

# ------------------------Footer------------------------------

def about(req):
    return render(req,'footer/about.html')

def faq(req):
    return render(req,'footer/faq.html')

def services(req):
    return render(req,'footer/our_services.html')

def privacy(req):
    return render(req,'footer/privacy.html')
