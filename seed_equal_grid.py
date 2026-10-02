import os
import django
import urllib.request
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore_project.settings')
django.setup()

from core.models import Category, Author, Book
from django.core.files.base import ContentFile

new_books_data = [
    {
        'title': 'The Psychology of Money',
        'author_name': 'Morgan Housel',
        'category_name': 'Self Help',
        'category_slug': 'self-help',
        'price': Decimal('850.00'),
        'discount_price': Decimal('720.00'),
        'is_bestseller': True,
        'is_new_arrival': False,
        'description': 'Timeless lessons on wealth, greed, and happiness. Doing well with money isn’t necessarily about what you know. It’s about how you behave.',
        'cover_url': 'https://covers.openlibrary.org/b/isbn/9780857197689-L.jpg',
        'isbn': '9780857197689'
    },
    {
        'title': 'The Alchemist',
        'author_name': 'Paulo Coelho',
        'category_name': 'Fiction',
        'category_slug': 'fiction',
        'price': Decimal('650.00'),
        'discount_price': Decimal('550.00'),
        'is_bestseller': True,
        'is_new_arrival': False,
        'description': 'A magical story of Santiago, an Andalusian shepherd boy who yearns to travel in search of a worldly treasure.',
        'cover_url': 'https://covers.openlibrary.org/b/isbn/9780062315007-L.jpg',
        'isbn': '9780062315007'
    },
    {
        'title': 'Yellowface',
        'author_name': 'R.F. Kuang',
        'category_name': 'Mystery and Thriller',
        'category_slug': 'mystery-and-thriller',
        'price': Decimal('950.00'),
        'discount_price': Decimal('820.00'),
        'is_bestseller': False,
        'is_new_arrival': True,
        'description': 'A razor-sharp, satirical thriller about diversity, racism, and cultural appropriation in the publishing industry.',
        'cover_url': 'https://covers.openlibrary.org/b/isbn/9780063250833-L.jpg',
        'isbn': '9780063250833'
    },
    {
        'title': 'Tomorrow, and Tomorrow, and Tomorrow',
        'author_name': 'Gabrielle Zevin',
        'category_name': 'Romance',
        'category_slug': 'romance',
        'price': Decimal('980.00'),
        'discount_price': Decimal('850.00'),
        'is_bestseller': False,
        'is_new_arrival': True,
        'description': 'A modern exhilarating masterpiece about two friends who come together in creative partnership and video game design.',
        'cover_url': 'https://covers.openlibrary.org/b/isbn/9780593321201-L.jpg',
        'isbn': '9780593321201'
    },
    {
        'title': 'The Midnight Library',
        'author_name': 'Matt Haig',
        'category_name': 'Fantasy',
        'category_slug': 'fantasy',
        'price': Decimal('890.00'),
        'discount_price': Decimal('750.00'),
        'is_bestseller': True,
        'is_new_arrival': True,
        'description': 'Between life and death there is a library, and within that library, the shelves go on forever. Every book provides a chance to try another life.',
        'cover_url': 'https://covers.openlibrary.org/b/isbn/9780525559474-L.jpg',
        'isbn': '9780525559474'
    },
    {
        'title': 'Deep Work',
        'author_name': 'Cal Newport',
        'category_name': 'Personal Development',
        'category_slug': 'personal-development',
        'price': Decimal('920.00'),
        'discount_price': Decimal('780.00'),
        'is_bestseller': False,
        'is_new_arrival': True,
        'description': 'Rules for focused success in a distracted world. Deep work is the ability to focus without distraction on cognitively demanding tasks.',
        'cover_url': 'https://covers.openlibrary.org/b/isbn/9781455586691-L.jpg',
        'isbn': '9781455586691'
    },
    {
        'title': 'Steve Jobs',
        'author_name': 'Walter Isaacson',
        'category_name': 'Science and Technology',
        'category_slug': 'science-and-technology',
        'price': Decimal('1350.00'),
        'discount_price': Decimal('1150.00'),
        'is_bestseller': True,
        'is_new_arrival': False,
        'description': 'The exclusive biography of Steve Jobs, based on more than forty interviews with Jobs conducted over two years.',
        'cover_url': 'https://covers.openlibrary.org/b/isbn/9781451648539-L.jpg',
        'isbn': '9781451648539'
    },
    {
        'title': 'Thinking, Fast and Slow',
        'author_name': 'Daniel Kahneman',
        'category_name': 'Academic and Educational',
        'category_slug': 'academic-and-educational',
        'price': Decimal('1200.00'),
        'discount_price': Decimal('990.00'),
        'is_bestseller': False,
        'is_new_arrival': True,
        'description': 'A monumental tour de force explaining the two systems that drive the way we think and make choices.',
        'cover_url': 'https://covers.openlibrary.org/b/isbn/9780374275631-L.jpg',
        'isbn': '9780374275631'
    }
]

for item in new_books_data:
    cat, _ = Category.objects.get_or_create(
        name=item['category_name'],
        defaults={'slug': item['category_slug'], 'description': 'Curated collection'}
    )
    author, _ = Author.objects.get_or_create(name=item['author_name'])
    
    book, created = Book.objects.get_or_create(
        title=item['title'],
        defaults={
            'author': author,
            'category': cat,
            'price': item['price'],
            'discount_price': item['discount_price'],
            'is_bestseller': item['is_bestseller'],
            'is_new_arrival': item['is_new_arrival'],
            'description': item['description'],
            'isbn': item['isbn'],
            'pages': 360
        }
    )
    
    try:
        req = urllib.request.Request(item['cover_url'], headers={'User-Agent': 'BookNestBot/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            if len(data) > 1000:
                book.cover_image.save(f'{book.slug}_real.jpg', ContentFile(data), save=True)
                print(f'Retrieved cover for: {book.title}')
    except Exception as e:
        print(f'Note for {book.title}: {e}')

print('Database count:', Book.objects.count())
