from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Category, Author, Book, Review
from decimal import Decimal
import datetime

class Command(BaseCommand):
    help = 'Populates Book Nest with rich curated literary books and categories'

    def handle(self, *args, **kwargs):
        # Create Superuser if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@aditibohara.com.np', 'admin12345')
            self.stdout.write(self.style.SUCCESS("Superuser 'admin' created with password 'admin12345'"))

        # Create Categories
        categories_data = [
            ("Fiction", "fiction", "bi-book", "Compelling novels, classics, and captivating literary fiction."),
            ("Romance", "romance", "bi-heart", "Heartfelt narratives, emotional journeys, and passionate bonds."),
            ("Mystery and Thriller", "mystery-and-thriller", "bi-incognito", "Spine-chilling suspense, unraveled enigmas, and dark detectives."),
            ("Self Help", "self-help", "bi-compass", "Personal transformation, mindfulness, and habits."),
            ("Science and Technology", "science-and-technology", "bi-cpu", "Artificial intelligence, cosmos, and future technologies."),
            ("Academic and Educational", "academic-and-educational", "bi-mortarboard", "Scholarly research, economics, philosophy, and reference guides."),
            ("Children's Book", "childrens-book", "bi-balloon", "Enchanting fairy tales, illustrated wonders, and bedtime fables."),
            ("History", "history", "bi-hourglass-split", "Ancient empires, monumental revolutions, and world chronicles."),
            ("Fantasy", "fantasy", "bi-magic", "Epic worlds, mystical lore, and wondrous mythologies."),
            ("Personal Development", "personal-development", "bi-lightning-charge", "Productivity blueprints, leadership mastery, and mindset cultivation.")
        ]

        cat_objs = {}
        for name, slug, icon, desc in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'icon': icon, 'description': desc}
            )
            cat_objs[slug] = cat
        self.stdout.write(self.style.SUCCESS("Categories populated."))

        # Create Authors
        authors_data = [
            ("Haruki Murakami", "haruki-murakami", "Renowned contemporary Japanese author blending surrealism with poetic loneliness."),
            ("Gabriel García Márquez", "gabriel-garcia-marquez", "Nobel laureate and pioneer of magical realism."),
            ("Aditi Bohara", "aditi-bohara", "Visionary writer, technologist, and literary architect behind Book Nest."),
            ("James Clear", "james-clear", "Author focused on habit formation, decision making, and continuous improvement."),
            ("Yuval Noah Harari", "yuval-noah-harari", "Historian and philosopher analyzing human cognition and future eras."),
            ("Donna Tartt", "donna-tartt", "Pulitzer Prize-winning American author of dark academia and literary mysteries."),
            ("J.R.R. Tolkien", "jrr-tolkien", "Legendary father of modern high fantasy and world-building."),
            ("Agatha Christie", "agatha-christie", "The timeless Queen of Crime and detective mysteries."),
            ("Tara Westover", "tara-westover", "Acclaimed American memoirist exploring education and resilience.")
        ]

        auth_objs = {}
        for name, slug, bio in authors_data:
            auth, _ = Author.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'bio': bio}
            )
            auth_objs[slug] = auth
        self.stdout.write(self.style.SUCCESS("Authors populated."))

        # Create Rich Books
        books_data = [
            {
                "title": "Kafka on the Shore",
                "slug": "kafka-on-the-shore",
                "author": auth_objs["haruki-murakami"],
                "category": cat_objs["fiction"],
                "price": Decimal("24.99"),
                "discount_price": Decimal("19.99"),
                "description": "A magnificent blend of magical realism, Japanese folklore, and psychological discovery following a runaway boy and an elderly man who speaks with cats.",
                "pages": 505,
                "is_bestseller": True,
                "is_featured": True,
                "is_book_of_the_week": True,
            },
            {
                "title": "One Hundred Years of Solitude",
                "slug": "one-hundred-years-of-solitude",
                "author": auth_objs["gabriel-garcia-marquez"],
                "category": cat_objs["fiction"],
                "price": Decimal("28.00"),
                "discount_price": Decimal("22.50"),
                "description": "The landmark multi-generational story of the Buendía family whose patriarch founds the mythical Colombian town of Macondo.",
                "pages": 417,
                "is_bestseller": True,
                "is_featured": True,
            },
            {
                "title": "Atomic Habits",
                "slug": "atomic-habits",
                "author": auth_objs["james-clear"],
                "category": cat_objs["self-help"],
                "price": Decimal("22.00"),
                "discount_price": Decimal("16.99"),
                "description": "An extraordinarily practical framework for breaking bad routines, building 1% daily increments of improvement, and mastering behaviors.",
                "pages": 320,
                "is_bestseller": True,
                "is_featured": True,
            },
            {
                "title": "Sapiens: A Brief History of Humankind",
                "slug": "sapiens",
                "author": auth_objs["yuval-noah-harari"],
                "category": cat_objs["history"],
                "price": Decimal("30.00"),
                "discount_price": Decimal("24.00"),
                "description": "Explore 70,000 years of human evolution from hunter-gatherer bands to the threshold of artificial superintelligence and bio-engineering.",
                "pages": 443,
                "is_bestseller": True,
                "is_featured": True,
            },
            {
                "title": "The Secret History",
                "slug": "the-secret-history",
                "author": auth_objs["donna-tartt"],
                "category": cat_objs["mystery-and-thriller"],
                "price": Decimal("25.00"),
                "discount_price": Decimal("19.50"),
                "description": "Under the influence of a charismatic classics professor, a group of eccentric New England college students discover a way of thinking that leads to dark murder.",
                "pages": 559,
                "is_bestseller": True,
                "is_new_arrival": False,
            },
            {
                "title": "The Fellowship of the Ring",
                "slug": "fellowship-of-the-ring",
                "author": auth_objs["jrr-tolkien"],
                "category": cat_objs["fantasy"],
                "price": Decimal("26.50"),
                "discount_price": Decimal("21.00"),
                "description": "The epic foundation of Middle-earth where Frodo Baggins begins his treacherous journey to destroy the One Ring.",
                "pages": 423,
                "is_bestseller": True,
                "is_featured": True,
            },
            {
                "title": "And Then There Were None",
                "slug": "and-then-there-were-none",
                "author": auth_objs["agatha-christie"],
                "category": cat_objs["mystery-and-thriller"],
                "price": Decimal("18.00"),
                "discount_price": Decimal("14.50"),
                "description": "Ten strangers are lured to an isolated island mansion off the Devon coast by a mysterious host, only to be executed one by one.",
                "pages": 272,
                "is_new_arrival": True,
            },
            {
                "title": "Educated: A Memoir",
                "slug": "educated-memoir",
                "author": auth_objs["tara-westover"],
                "category": cat_objs["personal-development"],
                "price": Decimal("24.00"),
                "discount_price": Decimal("18.00"),
                "description": "Born to survivalists in the mountains of Idaho, Tara Westover stepped into a classroom for the first time at seventeen and earned a doctorate from Cambridge.",
                "pages": 352,
                "is_new_arrival": True,
            },
            {
                "title": "Architecting Next-Gen Intelligence",
                "slug": "next-gen-intelligence",
                "author": auth_objs["aditi-bohara"],
                "category": cat_objs["science-and-technology"],
                "price": Decimal("35.00"),
                "discount_price": Decimal("29.00"),
                "description": "A pioneering guide on deep computational systems, neural alignment, and creating graceful digital user experiences.",
                "pages": 380,
                "is_new_arrival": True,
                "is_featured": True,
            },
            {
                "title": "Norwegian Wood",
                "slug": "norwegian-wood",
                "author": auth_objs["haruki-murakami"],
                "category": cat_objs["romance"],
                "price": Decimal("21.00"),
                "discount_price": Decimal("16.50"),
                "description": "A poignant journey through nostalgic love, youth, loss, and mental resilience in 1960s Tokyo.",
                "pages": 296,
                "is_new_arrival": True,
            },
            {
                "title": "Principles of Modern Economics",
                "slug": "modern-economics",
                "author": auth_objs["aditi-bohara"],
                "category": cat_objs["academic-and-educational"],
                "price": Decimal("45.00"),
                "discount_price": Decimal("38.00"),
                "description": "Comprehensive institutional analysis of macro-economic structures, currency dynamics, and algorithmic commerce.",
                "pages": 612,
                "is_new_arrival": True,
            },
            {
                "title": "The Little Star's Journey",
                "slug": "little-stars-journey",
                "author": auth_objs["aditi-bohara"],
                "category": cat_objs["childrens-book"],
                "price": Decimal("15.00"),
                "discount_price": Decimal("12.00"),
                "description": "An enchanting bedtime story about a curious star who journeys across galaxies to learn how to kindle its own inner light.",
                "pages": 48,
                "is_new_arrival": True,
            }
        ]

        for b_data in books_data:
            book, created = Book.objects.get_or_create(
                slug=b_data["slug"],
                defaults=b_data
            )
            if created:
                # Add sample reviews
                Review.objects.create(
                    book=book,
                    customer_name="Clara Montgomery",
                    rating=5,
                    comment="An extraordinary literary masterpiece. Book Nest delivered this in immaculate condition within 24 hours.",
                    helpful_count=14
                )
                Review.objects.create(
                    book=book,
                    customer_name="Julian Sterling",
                    rating=5,
                    comment="Mesmerizing prose and exquisite depth. Truly a book that belongs in every serious reader's personal library.",
                    helpful_count=9
                )

        self.stdout.write(self.style.SUCCESS("All Books and Reviews successfully seeded!"))
