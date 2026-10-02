from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Category, Author, Book, Review, Favorite, Order, OrderItem, ContactMessage, PushSubscription

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'book_count', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['created_at']

    def book_count(self, obj):
        return obj.books.count()
    book_count.short_description = "Total Books"


@admin.register(Author)
class AuthorAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'books_written']
    search_fields = ['name', 'bio']
    prepopulated_fields = {'slug': ('name',)}

    def books_written(self, obj):
        return obj.books.count()
    books_written.short_description = "Books Authored"


class ReviewInline(TabularInline):
    model = Review
    extra = 0
    fields = ['customer_name', 'rating', 'comment', 'helpful_count', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Book)
class BookAdmin(ModelAdmin):
    list_display = ['title', 'author', 'category', 'price', 'discount_price', 'stock', 'is_bestseller', 'is_new_arrival', 'is_book_of_the_week', 'is_featured']
    list_filter = ['category', 'is_bestseller', 'is_new_arrival', 'is_book_of_the_week', 'is_featured', 'language']
    search_fields = ['title', 'author__name', 'isbn', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['price', 'discount_price', 'stock', 'is_bestseller', 'is_new_arrival', 'is_book_of_the_week', 'is_featured']
    inlines = [ReviewInline]


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ['customer_name', 'book', 'rating', 'helpful_count', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['customer_name', 'comment', 'book__title']


@admin.register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ['book', 'user', 'session_key', 'created_at']
    list_filter = ['created_at']
    search_fields = ['book__title', 'user__username']


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['book', 'quantity', 'price']


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ['order_number', 'full_name', 'email', 'phone', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'full_name', 'email', 'phone']
    list_editable = ['status']
    inlines = [OrderItemInline]


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_read']


@admin.register(PushSubscription)
class PushSubscriptionAdmin(ModelAdmin):
    list_display = ['endpoint', 'user', 'created_at']
    search_fields = ['endpoint', 'user__username']
