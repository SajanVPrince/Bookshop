from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import *
from .models import *
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string


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

def sell(req):
    if 'user' in req.session:
        data=Sbook.objects.all()[::-1]
        if req.method=='POST':
            user=User.objects.get(username=req.session['user'])
            bk_name=req.POST['bk_name']
            ath_name=req.POST['ath_name']
            bk_price=req.POST['bk_price']
            bk_genres=req.POST['bk_genres']
            img=req.FILES['img']
            bk_dis=req.POST['bk_dis']
            data=Sbook.objects.create(user=user,sname=bk_name,sath_name=ath_name,sprice=bk_price,sbk_genres=bk_genres,simg=img,sdis=bk_dis)
            data.save()
            return redirect(sell)
        else:
            return render(req,'users/sell.html',{'data':data})
    else:
        return redirect(bk_login)
    
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

def view_sprod(req,id):
    data=Sbook.objects.get(pk=id)
    return render(req,'users/viewsprod.html',{'data':data})

def userpro(req):
    if 'user' in req.session:
        user = User.objects.get(username=req.session['user'])
        data1 = Userdtl.objects.filter(user=user)
        
        # Check if address form is being submitted
        if req.method == 'POST' and 'name' in req.POST:
            name = req.POST['name']
            phn = req.POST['phn']
            altphn = req.POST['altphn']
            pin = req.POST['pin']
            land = req.POST['land']
            adrs = req.POST['adrs']
            city = req.POST['city']
            state = req.POST['state']
            
            # Check if address already exists before saving
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
                # Create a new address if not already existing
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
        
        # Check if password change form is being submitted
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
        buy=Buys.objects.filter(user=user)
        return render (req,'users/myoders.html',{'data':buy})
    else:
        return redirect(bk_login)
    

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

            # Store the order data temporarily in the session
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
            req.session['order_data'] = order_data  # Store in session
            
            return redirect('order_success')  # Redirect to success page

        return render(req, 'users/buypage.html', {'prod': prod, 'saved_addresses': saved_addresses})
    else:
        return redirect('bk_login')


def buy_cart(request):
    if 'user' in request.session:
        user = User.objects.get(username=request.session['user'])
        cart = Cart.objects.filter(user=user)
        total_price = sum([item.product.ofr_price for item in cart])
        total_discount = sum([item.product.price - item.product.ofr_price for item in cart])
        saved_addresses = Userdtl.objects.filter(user=user)

        selected_address = None
        if request.method == 'POST':
            # Check if user selected an existing address or added a new one
            if 'address_id' in request.POST:
                selected_address = Userdtl.objects.get(id=request.POST['address_id'])
            elif 'fullname' in request.POST:
                # Handle the new address submission
                fullname = request.POST['fullname']
                address = request.POST['address']
                pincode = request.POST['pincode']
                city = request.POST['city']
                state = request.POST['state']
                phone = request.POST['phnum']
                altphone = request.POST['aphnum']
                landmark = request.POST['landmark']

                # Save the new address
                selected_address = Userdtl.objects.create(
                    user=user,
                    fullname=fullname,
                    address=address,
                    pincode=pincode,
                    city=city,
                    state=state,
                    phone=phone,
                    altphone=altphone,
                    landmark=landmark
                )

            # Store cart data and selected address in session for later use
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
                'total_discount': total_discount
            }
            request.session['order_data'] = order_data  # Store in session
            
            return redirect('order_success')  # Redirect to success page

        return render(request, 'users/checkout.html', {
            'cart': cart, 
            'total_price': total_price, 
            'total_discount': total_discount,
            'saved_addresses': saved_addresses,
        })
    else:
        return redirect('bk_login')

    
def cancel_order(req, id):
    if 'user' in req.session:
        order = Buys.objects.get(pk=id)
        order.delete()
        return redirect(view_odrs)
    else:
        return redirect(bk_login)
    
def view_booking_details(req, id):
    if 'user' in req.session:
        user = User.objects.get(username=req.session['user'])
        try:
            booking = Buys.objects.get(user=user, pk=id)  # Fetch a specific booking by ID
        except Buys.DoesNotExist:
            return redirect('some_error_page')  # Handle case where the booking is not found
        
        return render(req, 'users/viewbookingdetails.html', {'booking': booking})
    else:
        return redirect('bk_login')


def order_success(req):
    if 'order_data' in req.session:
        order_data = req.session['order_data']
        
        # Retrieve the user and address information
        user = User.objects.get(username=req.session['user'])
        selected_address_data = order_data['selected_address']
        
        # Check if the address already exists in the database
        existing_address = Userdtl.objects.filter(
            user=user,
            fullname=selected_address_data['fullname'],
            adress=selected_address_data['address'],
            city=selected_address_data['city'],
            state=selected_address_data['state'],
            pincode=selected_address_data['pincode'],
            phone=selected_address_data['phone'],
            altphone=selected_address_data['altphone'],
            landmark=selected_address_data['landmark']
        ).first()

        if not existing_address:
            # Save the new address if it does not exist
            selected_address = Userdtl.objects.create(
                user=user,
                fullname=selected_address_data['fullname'],
                adress=selected_address_data['address'],
                city=selected_address_data['city'],
                state=selected_address_data['state'],
                pincode=selected_address_data['pincode'],
                phone=selected_address_data['phone'],
                altphone=selected_address_data['altphone'],
                landmark=selected_address_data['landmark'],
            )
        else:
            # If the address already exists, use the existing one
            selected_address = existing_address

        # Process cart items and reduce stock
        for item in order_data['cart']:
            product = Books.objects.get(id=item['product'])
            Buys.objects.create(
                user=user,
                product=product,
                address=selected_address,
                # quantity=item['quantity'],
                # total_price=product.ofr_price * item['quantity']
            )
            # Reduce stock
            product.stock -= item['quantity']
            product.save()

        # Clear the cart
        Cart.objects.filter(user=user).delete()

        # Clear session data after completing the order
        del req.session['order_data']
        
        return render(req, 'users/ordersuccess.html')
    else:
        return redirect('home')

