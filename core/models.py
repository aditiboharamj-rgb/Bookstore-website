import io
import os
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator, MaxValueValidator
from PIL import Image

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default="bi-book", help_text="Bootstrap/FontAwesome icon identifier or emoji")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='authors/', blank=True, null=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cover_image = models.ImageField(upload_to='books/covers/', blank=True, null=True)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    pages = models.PositiveIntegerField(default=300)
    language = models.CharField(max_length=50, default="English")
    publication_date = models.DateField(null=True, blank=True)
    
    # Flags
    is_bestseller = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_book_of_the_week = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Inventory
    stock = models.PositiveIntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            
        # Pillow optimization layer: Compress and optimize book covers without jitter
        if self.cover_image:
            try:
                img = Image.open(self.cover_image)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Resize if unnecessarily large (max 1000px height)
                max_size = (800, 1100)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=85, optimize=True)
                output.seek(0)
                
                filename = os.path.basename(self.cover_image.name)
                name_without_ext = os.path.splitext(filename)[0]
                self.cover_image = ContentFile(output.read(), name=f"{name_without_ext}.jpg")
            except Exception:
                pass

        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 4.8  # Default high rating if no reviews yet

    @property
    def review_count(self):
        return self.reviews.count()

    def __str__(self):
        return self.title


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=150)
    customer_avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    helpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer_name} on {self.book.title} ({self.rating}★)"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='favorites')
    session_key = models.CharField(max_length=100, blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book', 'session_key')
        ordering = ['-created_at']

    def __str__(self):
        return f"Fav: {self.book.title}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=32, unique=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=5.00)
    payment_method = models.CharField(max_length=50, default="Cash on Delivery")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.order_number} - {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.book.title}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Msg from {self.name}: {self.subject}"


class PushSubscription(models.Model):
    endpoint = models.TextField(unique=True)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Push Sub: {self.endpoint[:40]}..."
