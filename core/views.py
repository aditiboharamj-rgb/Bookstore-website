import json
import random
import uuid
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator

from .models import Category, Author, Book, Review, Favorite, Order, OrderItem, ContactMessage, PushSubscription
from .cart import Cart

# 1. Home View
def home_view(request):
    bestsellers = Book.objects.filter(is_bestseller=True).select_related('author', 'category')[:8]
    new_arrivals = Book.objects.filter(is_new_arrival=True).select_related('author', 'category')[:8]
    nepali_books = Book.objects.filter(category__slug='nepali-literature').select_related('author', 'category')[:8]
    children_books = Book.objects.filter(category__slug='childrens-book').select_related('author', 'category')[:8]
    
    book_of_the_week = Book.objects.filter(is_book_of_the_week=True).select_related('author', 'category').first()
    if not book_of_the_week and bestsellers.exists():
        book_of_the_week = bestsellers.first()
        
    categories = Category.objects.all()[:10]
    happy_reviews = Review.objects.filter(rating__gte=4).select_related('book', 'user')[:12]
    
    return render(request, 'core/home.html', {
        'bestsellers': bestsellers,
        'new_arrivals': new_arrivals,
        'nepali_books': nepali_books,
        'children_books': children_books,
        'book_of_the_week': book_of_the_week,
        'categories': categories,
        'happy_reviews': happy_reviews,
    })



# 2. Categories & Exploration Grid View
def category_list_view(request, slug=None):
    current_category = None
    books = Book.objects.all().select_related('author', 'category')
    categories = Category.objects.all()

    if slug:
        current_category = get_object_or_404(Category, slug=slug)
        books = books.filter(category=current_category)

    # Search filter within category
    q = request.GET.get('q', '').strip()
    if q:
        books = books.filter(
            Q(title__icontains=q) | 
            Q(author__name__icontains=q) | 
            Q(category__name__icontains=q) |
            Q(description__icontains=q)
        )

    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        books = books.order_by('price')
    elif sort_by == 'price_high':
        books = books.order_by('-price')
    elif sort_by == 'title_asc':
        books = books.order_by('title')
    elif sort_by == 'bestseller':
        books = books.filter(is_bestseller=True)
    else:
        books = books.order_by('-created_at')

    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        books = books.filter(price__gte=min_price)
    if max_price:
        books = books.filter(price__lte=max_price)

    # Featured Books for sidebar spotlight
    featured_books = Book.objects.filter(is_featured=True)[:4]

    # Pagination
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/categories.html', {
        'current_category': current_category,
        'categories': categories,
        'page_obj': page_obj,
        'books': page_obj.object_list,
        'featured_books': featured_books,
        'search_query': q,
        'sort_by': sort_by,
    })


# 3. Book Detail View
def book_detail_view(request, slug):
    book = get_object_or_404(Book.objects.select_related('author', 'category'), slug=slug)
    reviews = book.reviews.all().order_by('-created_at')
    related_books = Book.objects.filter(category=book.category).exclude(id=book.id)[:4]

    # Check if favorited
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, book=book).exists()
    elif request.session.session_key:
        is_favorited = Favorite.objects.filter(session_key=request.session.session_key, book=book).exists()

    return render(request, 'core/book_detail.html', {
        'book': book,
        'reviews': reviews,
        'related_books': related_books,
        'is_favorited': is_favorited,
    })


# 4. Search View
def search_view(request):
    q = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    author_q = request.GET.get('author', '')
    
    books = Book.objects.all().select_related('author', 'category')
    
    if q:
        books = books.filter(
            Q(title__icontains=q) | 
            Q(author__name__icontains=q) | 
            Q(category__name__icontains=q) | 
            Q(description__icontains=q) |
            Q(isbn__icontains=q)
        )

    if category_slug:
        books = books.filter(category__slug=category_slug)

    if author_q:
        books = books.filter(author__name__icontains=author_q)

    # Pagination
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    return render(request, 'core/search.html', {
        'query': q,
        'page_obj': page_obj,
        'books': page_obj.object_list,
        'categories': categories,
        'total_results': books.count(),
    })


# 5. AI Book Recommendation View
def ai_recommendations_view(request):
    recommended_books = []
    user_mood = request.GET.get('mood', '')
    favorite_genre = request.GET.get('genre', '')
    reading_pace = request.GET.get('pace', '')
    query_theme = request.GET.get('theme', '')

    all_books = list(Book.objects.all().select_related('author', 'category'))

    if user_mood or favorite_genre or query_theme:
        filtered = []
        for b in all_books:
            score = 0
            if favorite_genre and (favorite_genre.lower() in b.category.name.lower()):
                score += 3
            if query_theme and (query_theme.lower() in b.title.lower() or query_theme.lower() in b.description.lower()):
                score += 4
            if user_mood == 'inspiring' and b.category.slug in ['self-help', 'personal-development', 'history']:
                score += 2
            elif user_mood == 'escapist' and b.category.slug in ['fantasy', 'fiction', 'romance']:
                score += 2
            elif user_mood == 'thrilling' and b.category.slug in ['mystery-and-thriller', 'science-and-technology']:
                score += 2
            elif user_mood == 'academic' and b.category.slug in ['academic-and-educational', 'science-and-technology']:
                score += 2
            
            if score > 0:
                filtered.append((score, b))
                
        filtered.sort(key=lambda x: x[0], reverse=True)
        recommended_books = [item[1] for item in filtered[:6]]

    if not recommended_books and all_books:
        # Fallback to rich curated mix
        recommended_books = random.sample(all_books, min(len(all_books), 6))

    categories = Category.objects.all()

    return render(request, 'core/ai_recommendations.html', {
        'recommended_books': recommended_books,
        'categories': categories,
        'selected_mood': user_mood,
        'selected_genre': favorite_genre,
        'selected_pace': reading_pace,
        'query_theme': query_theme,
    })


# 6. AI Interactive Chat Assistant Endpoint
@require_POST
def ai_chat_api(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip().lower()
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    books = Book.objects.all().select_related('author', 'category')
    matched = []
    
    for book in books:
        if any(term in book.title.lower() or term in book.description.lower() or term in book.category.name.lower() or term in book.author.name.lower() for term in user_message.split()):
            matched.append({
                'title': book.title,
                'author': book.author.name,
                'category': book.category.name,
                'price': str(book.discount_price or book.price),
                'url': f"/book/{book.slug}/",
                'cover': book.cover_image.url if book.cover_image else '/static/images/default_cover.svg'
            })

    if not matched:
        # Provide suggestions
        random_books = random.sample(list(books), min(len(books), 3))
        matched = [{
            'title': b.title,
            'author': b.author.name,
            'category': b.category.name,
            'price': str(b.discount_price or b.price),
            'url': f"/book/{b.slug}/",
            'cover': b.cover_image.url if b.cover_image else '/static/images/default_cover.svg'
        } for b in random_books]
        reply_text = f"I've tailored these enchanting reads from our literary vault for you:"
    else:
        reply_text = f"Based on your thought '{user_message}', here are exceptional curated recommendations you'll love:"

    return JsonResponse({
        'reply': reply_text,
        'books': matched[:4]
    })


# 7. Cart Views
def cart_detail_view(request):
    cart = Cart(request)
    return render(request, 'core/cart.html', {
        'cart': cart,
        'subtotal': cart.get_subtotal(),
        'delivery_fee': cart.get_delivery_fee(),
        'total': cart.get_total(),
    })


def cart_add_view(request, book_id):
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    quantity = int(request.POST.get('quantity', 1))
    override = request.POST.get('override') == 'true'
    cart.add(book_id=book.id, quantity=quantity, override_quantity=override)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'subtotal': str(cart.get_subtotal()),
            'total': str(cart.get_total()),
            'message': f"'{book.title}' added to your reading basket!"
        })
    
    messages.success(request, f"'{book.title}' added to cart.")
    return redirect('core:cart_detail')


def cart_remove_view(request, book_id):
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    cart.remove(book_id)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'subtotal': str(cart.get_subtotal()),
            'total': str(cart.get_total())
        })
        
    messages.info(request, f"Removed '{book.title}' from your basket.")
    return redirect('core:cart_detail')


# 8. Checkout & Order Confirmation Views
def checkout_view(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your basket is empty. Discover books to proceed!")
        return redirect('core:category_list')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        payment_method = request.POST.get('payment_method', 'Cash on Delivery')

        order_number = f"BN-{uuid.uuid4().hex[:8].upper()}"
        order = Order.objects.create(
            order_number=order_number,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            postal_code=postal_code,
            total_amount=cart.get_total(),
            delivery_fee=cart.get_delivery_fee(),
            payment_method=payment_method,
            status='PENDING'
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                book=item['book'],
                quantity=item['quantity'],
                price=item['price']
            )

        cart.clear()
        return redirect('core:order_confirmation', order_number=order.order_number)

    return render(request, 'core/checkout.html', {
        'cart': cart,
        'subtotal': cart.get_subtotal(),
        'delivery_fee': cart.get_delivery_fee(),
        'total': cart.get_total(),
    })


def order_confirmation_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'core/order_confirmation.html', {
        'order': order
    })


# 9. Favorites & Reviews Section
def favorites_view(request):
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user).select_related('book', 'book__author', 'book__category')
    else:
        if not request.session.session_key:
            request.session.create()
        favorites = Favorite.objects.filter(session_key=request.session.session_key).select_related('book', 'book__author', 'book__category')

    return render(request, 'core/favorites.html', {
        'favorites': favorites
    })


@require_POST
def toggle_favorite_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    if request.user.is_authenticated:
        fav = Favorite.objects.filter(user=request.user, book=book).first()
        if fav:
            fav.delete()
            favorited = False
            msg = f"Removed '{book.title}' from your favorites."
        else:
            Favorite.objects.create(user=request.user, book=book)
            favorited = True
            msg = f"Saved '{book.title}' to your favorites."
        count = Favorite.objects.filter(user=request.user).count()
    else:
        fav = Favorite.objects.filter(session_key=session_key, book=book).first()
        if fav:
            fav.delete()
            favorited = False
            msg = f"Removed '{book.title}' from your favorites."
        else:
            Favorite.objects.create(session_key=session_key, book=book)
            favorited = True
            msg = f"Saved '{book.title}' to your favorites."
        count = Favorite.objects.filter(session_key=session_key).count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'favorited': favorited,
            'fav_count': count,
            'message': msg
        })
    messages.info(request, msg)
    return redirect('core:favorites')


@require_POST
def add_review_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    customer_name = request.POST.get('customer_name', 'Kind Reader')
    rating = int(request.POST.get('rating', 5))
    comment = request.POST.get('comment', '')

    review = Review.objects.create(
        book=book,
        user=request.user if request.user.is_authenticated else None,
        customer_name=customer_name,
        rating=rating,
        comment=comment,
        customer_avatar=request.FILES.get('customer_avatar')
    )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': "Thank you for sharing your reading reflection!",
            'average_rating': book.average_rating,
            'review_count': book.review_count,
        })

    messages.success(request, "Your book review has been published!")
    return redirect('core:book_detail', slug=book.slug)


@require_POST
def review_helpful_view(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.helpful_count += 1
    review.save()
    return JsonResponse({
        'success': True,
        'helpful_count': review.helpful_count
    })


# 10. About Us Page
def about_view(request):
    authors = Author.objects.all()[:8]
    return render(request, 'core/about.html', {
        'authors': authors
    })


# 11. Contact Us Page
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        messages.success(request, "Thank you for reaching out! Our literary curators will get back to you promptly.")
        return redirect('core:contact')

    return render(request, 'core/contact.html')


# 12. Return Policy & Privacy Policy Pages
def return_policy_view(request):
    return render(request, 'core/return_policy.html')


def privacy_policy_view(request):
    return render(request, 'core/privacy_policy.html')


# 13. PWA & VAPID Push Notification API
@require_POST
def subscribe_push_view(request):
    try:
        data = json.loads(request.body)
        endpoint = data.get('endpoint')
        keys = data.get('keys', {})
        p256dh = keys.get('p256dh')
        auth = keys.get('auth')

        if endpoint and p256dh and auth:
            PushSubscription.objects.update_or_create(
                endpoint=endpoint,
                defaults={
                    'p256dh': p256dh,
                    'auth': auth,
                    'user': request.user if request.user.is_authenticated else None
                }
            )
            return JsonResponse({'status': 'subscribed'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid payload'}, status=400)


def service_worker_view(request):
    response = render(request, 'core/sw.js', content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    return response


def manifest_view(request):
    manifest_data = {
        "name": "Book Nest - Literary Sanctuary",
        "short_name": "Book Nest",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#FBF7F2",
        "theme_color": "#C2410C",
        "icons": [
            {
                "src": "/static/images/icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/static/images/icon-512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    return JsonResponse(manifest_data)
