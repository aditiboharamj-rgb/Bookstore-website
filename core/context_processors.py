from django.conf import settings
from .models import Category, Favorite
from .cart import Cart

def booknest_context(request):
    categories = Category.objects.all()[:12]
    cart = Cart(request)
    
    # Calculate favorite count
    if request.user.is_authenticated:
        fav_count = Favorite.objects.filter(user=request.user).count()
    else:
        if not request.session.session_key:
            request.session.create()
        fav_count = Favorite.objects.filter(session_key=request.session.session_key).count()

    return {
        'nav_categories': categories,
        'cart_count': len(cart),
        'cart_total': cart.get_total(),
        'fav_count': fav_count,
        'vapid_public_key': getattr(settings, 'VAPID_PUBLIC_KEY', ''),
        'developer_name': 'Aditi Bohara',
        'developer_url': 'https://aditibohara.com.np',
        'site_motto': 'Where every page brings you home.',
    }
