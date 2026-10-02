from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('categories/', views.category_list_view, name='category_list'),
    path('category/<slug:slug>/', views.category_list_view, name='category_detail'),
    path('book/<slug:slug>/', views.book_detail_view, name='book_detail'),
    path('search/', views.search_view, name='search'),
    
    # AI recommendations & Chat
    path('ai-recommendations/', views.ai_recommendations_view, name='ai_recommendations'),
    path('api/ai-chat/', views.ai_chat_api, name='ai_chat_api'),
    
    # Cart & Checkout
    path('cart/', views.cart_detail_view, name='cart_detail'),
    path('cart/add/<int:book_id>/', views.cart_add_view, name='cart_add'),
    path('cart/remove/<int:book_id>/', views.cart_remove_view, name='cart_remove'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order-confirmation/<str:order_number>/', views.order_confirmation_view, name='order_confirmation'),
    
    # Favorites & Reviews
    path('favorites/', views.favorites_view, name='favorites'),
    path('favorites/toggle/<int:book_id>/', views.toggle_favorite_view, name='toggle_favorite'),
    path('book/<int:book_id>/review/', views.add_review_view, name='add_review'),
    path('review/<int:review_id>/helpful/', views.review_helpful_view, name='review_helpful'),
    
    # Static & Policies
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('return-policy/', views.return_policy_view, name='return_policy'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    
    # PWA & Webpush
    path('manifest.json', views.manifest_view, name='manifest'),
    path('sw.js', views.service_worker_view, name='service_worker'),
    path('api/push/subscribe/', views.subscribe_push_view, name='subscribe_push'),
]
