from django.urls import path
from . import views

urlpatterns = [
    path('login',views.bk_login, name='bk_login'),
    path('logout',views.bk_logout , name='logout'),
    path('register',views.register , name='register'),
    path('verifyotp',views.verify_otp, name='verify_otp'),
    path('resend',views.resend_otp, name='resend_otp'),
    path('forget',views.forgetpassword , name='forgetpassword'),
    path('reset',views.resetpassword , name='resetpassword'),
    path('verify_otp_reg',views.verify_otp_reg, name='verify_otp_reg'),
    path('resend_otp_reg',views.resend_otp_reg, name='resend_otp_reg'),
    

    # ----Admin---

    path('adminpro',views.adminpro),
    path('adhome',views.adhome),
    path('dramasbk',views.sdrama),
    path('lovesbk',views.slove),
    path('fantacysbk',views.sfantacy),
    path('scifisbk',views.sscifi),
    path('othersbk',views.sothers),
    path('delete_sdrama/<id>',views.delete_sdrama),
    path('delete_slove/<id>',views.delete_slove),
    path('delete_sfantacy/<id>',views.delete_sfantacy),
    path('delete_sscifi/<id>',views.delete_sscifi),
    path('delete_sothers/<id>',views.delete_sothers),
    path('edit_sdrama/<id>',views.edit_sdrama),
    path('edit_slove/<id>',views.edit_slove),
    path('edit_sfantacy/<id>',views.edit_sfantacy),
    path('edit_sscifi/<id>',views.edit_sscifi),
    path('edit_sothers/<id>',views.edit_sothers),
    path('viewuser',views.view_user),
    path('deleteuser/<id>',views.delete_user),
    path('viewreview',views.view_review),
    path('deletereview/<id>',views.delete_review),
    path('viewbuy',views.view_buy),
    path('viewbookingdetails',views.viewbookingdetails),




    # ---USER----
    path('',views.bk_home),
    path('home',views.bk_home),
    path('dramabk',views.drama),
    path('lovebk',views.love),
    path('fantacybk',views.fantacy),
    path('scifibk',views.scifi),
    path('otherbk',views.others),
    path('viewprod/<id>',views.view_prod),
    path('userpro',views.userpro ,name='userpro'),
    path('viewcart',views.viewcart),
    path('add_to_cart/<pid>',views.add_to_cart),
    path('delete_cart/<id>',views.delete_cart),
    path('favbk/<bid>',views.addfav),
    path('viewfav',views.viewfav),
    path('deletefavs/<int:pk>', views.deletefavs, name='deletefavs'),
    path('search', views.search_view, name='search'),
    path('viewoders',views.view_odrs),
    path('product_buy/<id>',views.product_buy, name='product_buy'),
    path('checkout', views.buy_cart, name='buy_cart'),
    path('cancel_oder/<id>',views.cancel_order),
    path('view_details/<id>',views.view_booking_details),
    path('ordersucces',views.order_success , name='order_success'),

    
# ----------------Footer------------------

    path('about',views.about),
    path('faq',views.faq),
    path('service',views.services),
    path('privacy',views.privacy),



]