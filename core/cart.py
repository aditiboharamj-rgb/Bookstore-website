from decimal import Decimal
from .models import Category, Book

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, book_id, quantity=1, override_quantity=False):
        book_id_str = str(book_id)
        if book_id_str not in self.cart:
            self.cart[book_id_str] = {'quantity': 0}
        
        if override_quantity:
            self.cart[book_id_str]['quantity'] = quantity
        else:
            self.cart[book_id_str]['quantity'] += quantity
            
        if self.cart[book_id_str]['quantity'] <= 0:
            self.remove(book_id)
        else:
            self.save()

    def remove(self, book_id):
        book_id_str = str(book_id)
        if book_id_str in self.cart:
            del self.cart[book_id_str]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        del self.session['cart']
        self.save()

    def __iter__(self):
        book_ids = self.cart.keys()
        books = Book.objects.filter(id__in=book_ids).select_related('author', 'category')
        cart_copy = self.cart.copy()

        for book in books:
            cart_copy[str(book.id)]['book'] = book

        for item in cart_copy.values():
            if 'book' in item:
                price = item['book'].discount_price if item['book'].discount_price else item['book'].price
                item['price'] = price
                item['total_price'] = price * item['quantity']
                yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_subtotal(self):
        subtotal = Decimal('0.00')
        book_ids = self.cart.keys()
        books = {b.id: (b.discount_price if b.discount_price else b.price) for b in Book.objects.filter(id__in=book_ids)}
        for book_id, item in self.cart.items():
            if int(book_id) in books:
                subtotal += books[int(book_id)] * item['quantity']
        return subtotal

    def get_delivery_fee(self):
        if len(self) == 0:
            return Decimal('0.00')
        # Free delivery over Rs. 1500
        if self.get_subtotal() >= Decimal('1500.00'):
            return Decimal('0.00')
        return Decimal('100.00')

    def get_total(self):
        return self.get_subtotal() + self.get_delivery_fee()
