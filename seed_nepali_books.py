import os
import django
import urllib.request
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore_project.settings')
django.setup()

from core.models import Category, Author, Book
from django.core.files.base import ContentFile

nepali_cat, _ = Category.objects.get_or_create(
    name='Nepali Literature',
    defaults={'slug': 'nepali-literature', 'description': 'Rich treasures of Nepali novels, poetry, memoirs, and Himalayan philosophy.'}
)

nepali_books_data = [
    {
        'title': 'Seto Bagh (The White Tiger)',
        'author_name': 'Diamond Shumsher Rana',
        'price': Decimal('480.00'),
        'discount_price': Decimal('420.00'),
        'description': 'A monumental historical novel depicting the twilight years of Jung Bahadur Rana and the fierce power struggles within the Rana dynasty.',
        'cover_url': 'https://covers.openlibrary.org/b/isbn/9789937829779-L.jpg',
        'isbn': '9789937829779'
    },
    {
        'title': 'Palpasa Cafe',
        'author_name': 'Narayan Wagle',
        'price': Decimal('550.00'),
        'discount_price': Decimal('480.00'),
        'description': 'The critically acclaimed Madan Puraskar-winning novel about Drishya, an artist in Kathmandu amidst the conflict era in Nepal.',
        'cover_url': 'https://covers.openlibrary.org/b/isbn/9789993304876-L.jpg',
        'isbn': '9789993304876'
    },
    {
        'title': 'Karnali Blues',
        'author_name': 'Buddhisagar',
        'price': Decimal('590.00'),
        'discount_price': Decimal('520.00'),
        'description': 'An emotional coming-of-age story of a son and his profound relationship with his father, set in the remote villages of Western Nepal.',
        'cover_url': 'https://covers.openlibrary.org/b/isbn/9780143455110-L.jpg',
        'isbn': '9780143455110'
    },
    {
        'title': 'Muna Madan',
        'author_name': 'Laxmi Prasad Devkota',
        'price': Decimal('320.00'),
        'discount_price': Decimal('270.00'),
        'description': 'The legendary epic by Mahakavi Laxmi Prasad Devkota. "A person is great by heart and deeds, not by birth or caste."',
        'cover_url': 'https://covers.openlibrary.org/b/isbn/9789993322122-L.jpg',
        'isbn': '9789993322122'
    },
    {
        'title': 'Shirishko Phool (The Blue Mimosa)',
        'author_name': 'Parijat',
        'price': Decimal('450.00'),
        'discount_price': Decimal('390.00'),
        'description': 'Parijat’s masterwork exploring existentialism, post-war trauma, and complex love in 1960s Kathmandu.',
        'cover_url': 'https://covers.openlibrary.org/b/isbn/9789937829786-L.jpg',
        'isbn': '9789937829786'
    },
    {
        'title': 'Radha',
        'author_name': 'Krishna Dharabasi',
        'price': Decimal('540.00'),
        'discount_price': Decimal('460.00'),
        'description': 'Madan Puraskar winning literary fiction re-interpreting the Mahabharata from the poignant perspective of Radha.',
        'cover_url': 'https://covers.openlibrary.org/b/isbn/9789993356066-L.jpg',
        'isbn': '9789993356066'
    },
    {
        'title': 'China Harayeko Manchhe',
        'author_name': 'Hari Bansa Acharya',
        'price': Decimal('600.00'),
        'discount_price': Decimal('520.00'),
        'description': 'The deeply touching and witty autobiography of Nepal’s beloved comedy icon and cultural giant, Hari Bansa Acharya.',
        'cover_url': 'https://covers.openlibrary.org/b/isbn/9789937862707-L.jpg',
        'isbn': '9789937862707'
    },
    {
        'title': 'Ghumne Mechmathi Andho Manchhe',
        'author_name': 'Bhupi Sherchan',
        'price': Decimal('380.00'),
        'discount_price': Decimal('320.00'),
        'description': 'A landmark collection of modern Nepali poems capturing social realism, irony, and human spirit in Kathmandu.',
        'cover_url': 'https://covers.openlibrary.org/b/isbn/9789993306122-L.jpg',
        'isbn': '9789993306122'
    }
]

for item in nepali_books_data:
    author, _ = Author.objects.get_or_create(name=item['author_name'])
    book, created = Book.objects.get_or_create(
        title=item['title'],
        defaults={
            'author': author,
            'category': nepali_cat,
            'price': item['price'],
            'discount_price': item['discount_price'],
            'is_bestseller': True,
            'is_new_arrival': False,
            'description': item['description'],
            'isbn': item['isbn'],
            'pages': 280
        }
    )
    
    try:
        req = urllib.request.Request(item['cover_url'], headers={'User-Agent': 'BookNestBot/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            if len(data) > 1000:
                book.cover_image.save(f'{book.slug}_nepali.jpg', ContentFile(data), save=True)
                print(f'Retrieved cover for: {book.title}')
    except Exception as e:
        print(f'Note: {e}')

print('Seeded Nepali Literature. Total books now:', Book.objects.count())
