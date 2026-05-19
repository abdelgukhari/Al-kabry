"""
Management command to seed the database with sample data for testing recommendation algorithms.
Creates categories, products, users, reviews, and interactions.
"""
import os
import random
import pandas as pd
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from products.models import Category, Tag, Product, Review
from recommendations.models import UserInteraction

User = get_user_model()

# Sample data
CATEGORIES = [
    {'name': 'Fashion', 'children': ['Shirts', 'Pants', 'Dresses', 'Jackets', 'Shoes']},
    {'name': 'Accessories', 'children': ['Bags', 'Hats', 'Sunglasses', 'Jewelry', 'Scarves']},
    {'name': 'Activewear', 'children': ['Leggings', 'Sports Tops', 'Track Pants', 'Windbreakers', 'Sneakers']},
    {'name': 'Trends', 'children': ['Bestsellers', 'New Arrivals', 'Sale Items', 'Limited Edition', 'Seasonal']},
]

BRANDS = {
    'Fashion': ['H&M'],
    'Accessories': ['H&M'],
    'Activewear': ['H&M'],
    'Trends': ['H&M'],
}

PRODUCT_NAMES = {
    'Shirts': ['H&M Cotton Shirt', 'H&M Striped Shirt', 'H&M Linen Button-Up', 'H&M Chambray Shirt', 'H&M Flannel Shirt'],
    'Pants': ['H&M Tailored Chinos', 'H&M Slim Fit Trousers', 'H&M Cargo Pants', 'H&M Corduroy Pants', 'H&M Wide-Leg Pants'],
    'Dresses': ['H&M Summer Midi Dress', 'H&M Cocktail Dress', 'H&M Maxi Dress', 'H&M A-Line Dress', 'H&M Wrap Dress'],
    'Jackets': ['H&M Leather Jacket', 'H&M Denim Jacket', 'H&M Windbreaker', 'H&M Puffer Jacket', 'H&M Bomber Jacket'],
    'Shoes': ['H&M Running Sneakers', 'H&M Casual Loafers', 'H&M Chelsea Boots', 'H&M Espadrille Flats', 'H&M Trainers'],
    'Bags': ['H&M Leather Tote Bag', 'H&M Canvas Backpack', 'H&M Crossbody Bag', 'H&M Clutch Purse', 'H&M Weekend Duffel'],
    'Hats': ['H&M Baseball Cap', 'H&M Wide Brim Hat', 'H&M Beanie', 'H&M Fedora', 'H&M Bucket Hat'],
    'Sunglasses': ['H&M Aviator Shades', 'H&M Round Sunglasses', 'H&M Cat Eye Sunglasses', 'H&M Sport Sunglasses', 'H&M Oversized Sunglasses'],
    'Jewelry': ['H&M Gold Pendant Necklace', 'H&M Silver Hoop Earrings', 'H&M Charm Bracelet', 'H&M Layered Necklace', 'H&M Stackable Rings'],
    'Scarves': ['H&M Silk Scarf', 'H&M Wool Wrap', 'H&M Cashmere Scarf', 'H&M Infinity Scarf', 'H&M Plaid Scarf'],
    'Leggings': ['H&M High-Waist Leggings', 'H&M Performance Leggings', 'H&M Printed Leggings', 'H&M Seamless Leggings', 'H&M Yoga Leggings'],
    'Sports Tops': ['H&M Mesh Training Tank', 'H&M Running Crop Top', 'H&M Long Sleeve Workout Top', 'H&M Performance Tee', 'H&M Training Hoodie'],
    'Track Pants': ['H&M Slim Track Pants', 'H&M Relaxed Sweatpants', 'H&M Zip Pocket Track Pants', 'H&M Cuffed Joggers', 'H&M Performance Track Pants'],
    'Windbreakers': ['H&M Lightweight Windbreaker', 'H&M Packable Windbreaker', 'H&M Hooded Windbreaker', 'H&M Colorblock Windbreaker', 'H&M Reflective Windbreaker'],
    'Sneakers': ['H&M Retro Sneakers', 'H&M Chunky Sneakers', 'H&M Slip-On Sneakers', 'H&M Court Sneakers', 'H&M Platform Sneakers'],
    'Bestsellers': ['H&M Iconic Crewneck Sweatshirt', 'H&M Denim Jacket', 'H&M Leather Jacket', 'H&M Boho Dress', 'H&M Hoodie'],
    'New Arrivals': ['H&M New Season Trench', 'H&M Denim Jacket', 'H&M Fresh Hoodie', 'H&M New Blazer', 'H&M Wrap Dress'],
    'Sale Items': ['H&M Knit Sweater', 'H&M Denim Shorts', 'H&M Slip Dress', 'H&M Bomber Jacket', 'H&M Anorak'],
    'Limited Edition': ['H&M Limited Edition Jacket', 'H&M Collector Hoodie', 'H&M Signature Jeans', 'H&M Release Sneaker', 'H&M Quilted Coat'],
    'Seasonal': ['H&M Linen Shirt', 'H&M Wool Coat', 'H&M Knit Pullover', 'H&M Floral Dress', 'H&M Velvet Blazer'],
}

TAGS = ['bestseller', 'new-arrival', 'sale', 'premium', 'eco-friendly', 'limited-edition', 'trending', 'popular', 'recommended', 'top-rated']
COLORS = ['Black', 'White', 'Red', 'Blue', 'Green', 'Gray', 'Brown', 'Pink', 'Yellow', 'Purple']
SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'One Size']
MATERIALS = ['Cotton', 'Polyester', 'Leather', 'Metal', 'Plastic', 'Wood', 'Glass', 'Ceramic']

DESCRIPTIONS = [
    "High-quality product designed for optimal performance and durability.",
    "Premium materials and excellent craftsmanship make this a great choice.",
    "Perfect for everyday use with excellent value for money.",
    "Top-rated product with outstanding features and customer satisfaction.",
    "Innovative design with advanced technology for modern lifestyle.",
    "Comfortable, stylish, and built to last. Highly recommended.",
    "Professional grade product suitable for demanding applications.",
    "Eco-friendly product made with sustainable materials.",
]


class Command(BaseCommand):
    help = 'Seed the database with sample data for recommendation algorithm testing'
    
    def _generate_unique_slug(self, base, existing_slugs):
        slug = slugify(base)
        original = slug
        counter = 1
        while slug in existing_slugs:
            slug = f"{original}-{counter}"
            counter += 1
        existing_slugs.add(slug)
        return slug

    def _safe_text(self, value):
        if pd.isna(value):
            return ''
        return str(value).strip()

    def _first_available(self, row, keys):
        for key in keys:
            if key in row and not pd.isna(row[key]):
                text = str(row[key]).strip()
                if text:
                    return text
        return ''

    def _load_kaggle_dataframe(self, kaggle_file):
        if not os.path.isfile(kaggle_file):
            raise FileNotFoundError(f'Kaggle file not found: {kaggle_file}')
        df = pd.read_csv(kaggle_file, low_memory=False).fillna('')
        if df.empty:
            raise ValueError('Kaggle file is empty')
        return df

    def _get_kaggle_price(self, row):
        price_columns = ['price', 'sales_price', 'rrp', 'cost_price', 'price_sales']
        for key in price_columns:
            if key in row and row[key] != '':
                try:
                    return round(float(row[key]), 2)
                except (ValueError, TypeError):
                    continue
        return round(random.uniform(10, 100), 2)

    def _get_kaggle_category(self, row):
        category_columns = [
            'department_name',
            'product_group_name',
            'section_name',
            'product_type_name',
            'article_type_name'
        ]
        return self._first_available(row, category_columns) or 'H&M Fashion'

    def _get_kaggle_product_name(self, row):
        name_columns = [
            'product_name',
            'article_name',
            'detail_desc',
            'graphical_appearance_name',
            'index_name'
        ]
        return self._first_available(row, name_columns) or 'H&M Fashion Product'

    def _get_kaggle_brand(self, row):
        brand_columns = ['brand_name', 'brand', 'index_group_name']
        return self._first_available(row, brand_columns) or 'H&M'

    def _get_kaggle_color(self, row):
        color_columns = [
            'colour_group_name',
            'perceived_colour_value_name',
            'perceived_colour_master_name',
            'colour_code',
            'color'
        ]
        return self._first_available(row, color_columns)

    def create_products_from_kaggle(self, kaggle_file, num_products):
        df = self._load_kaggle_dataframe(kaggle_file)
        products = []
        categories = {}
        all_tag_names = set()
        existing_slugs = set(Product.objects.values_list('slug', flat=True))

        for _, row in df.head(num_products).iterrows():
            name = self._get_kaggle_product_name(row)
            category_name = self._get_kaggle_category(row)
            brand = self._get_kaggle_brand(row)
            color = self._get_kaggle_color(row)
            price = self._get_kaggle_price(row)
            description = self._first_available(row, ['detail_desc', 'product_name', 'article_name'])
            if not description:
                description = f'{name} from H&M dataset.'

            category = categories.get(category_name)
            if not category:
                category, _ = Category.objects.get_or_create(
                    name=category_name,
                    defaults={
                        'description': f'{category_name} imported from Kaggle dataset',
                        'is_active': True
                    }
                )
                categories[category_name] = category

            slug = self._generate_unique_slug(name, existing_slugs)
            product = Product.objects.create(
                name=name,
                slug=slug,
                description=description,
                price=price,
                compare_price=round(price * random.uniform(1.05, 1.3), 2) if random.random() > 0.5 else None,
                stock=random.randint(10, 200),
                category=category,
                brand=brand,
                color=color,
                is_active=True,
            )

            tag_names = set()
            if category_name:
                tag_names.add(category_name.lower().replace(' ', '-'))
            if color:
                tag_names.add(color.lower().replace(' ', '-'))
            if brand:
                tag_names.add(brand.lower().replace(' ', '-'))

            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                product.tags.add(tag)
                all_tag_names.add(tag_name)

            products.append(product)

        return products, categories, list(Tag.objects.filter(name__in=all_tag_names))

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=30, help='Number of users to create')
        parser.add_argument('--products', type=int, default=80, help='Number of products to create')
        parser.add_argument('--reviews', type=int, default=200, help='Number of reviews to create')
        parser.add_argument('--interactions', type=int, default=500, help='Number of interactions to create')
        parser.add_argument('--kaggle-file', type=str, help='Optional CSV file path for Kaggle dataset import')
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        
        num_users = options['users']
        num_products = options['products']
        num_reviews = options['reviews']
        num_interactions = options['interactions']
        
        kaggle_file = options.get('kaggle_file')
        if kaggle_file:
            self.stdout.write(self.style.SUCCESS(f'Loading Kaggle dataset from {kaggle_file}...'))
            products, categories, tags = self.create_products_from_kaggle(kaggle_file, num_products)
            self.stdout.write(self.style.SUCCESS(f'  ✓ Imported {len(products)} products from Kaggle dataset'))
        else:
            # Create categories
            self.stdout.write('Creating categories...')
            categories = {}
            for cat_data in CATEGORIES:
                parent, _ = Category.objects.get_or_create(
                    name=cat_data['name'],
                    defaults={'description': f'Products in {cat_data["name"]} category'}
                )
                categories[cat_data['name']] = parent
                
                for child_name in cat_data['children']:
                    child, _ = Category.objects.get_or_create(
                        name=child_name,
                        parent=parent,
                        defaults={'description': f'Products in {child_name} subcategory'}
                    )
                    categories[child_name] = child
            
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(categories)} categories'))
            
            # Create tags
            self.stdout.write('Creating tags...')
            tags = []
            for tag_name in TAGS:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
            
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(tags)} tags'))
            
            # Create products
            self.stdout.write('Creating products...')
            products = []
            product_id = 1
            existing_slugs = set(Product.objects.values_list('slug', flat=True))
            
            for category_name, category in categories.items():
                if category_name in PRODUCT_NAMES:
                    for name in PRODUCT_NAMES[category_name]:
                        if len(products) >= num_products:
                            break
                            
                        parent_category = category.parent if category.parent else category
                        brand_list = BRANDS.get(parent_category.name, ['Generic'])
                        slug = self._generate_unique_slug(name, existing_slugs)
                        
                        product = Product.objects.create(
                            name=name,
                            slug=slug,
                            description=random.choice(DESCRIPTIONS),
                            price=round(random.uniform(10, 1000), 2),
                            compare_price=round(random.uniform(50, 1200), 2) if random.random() > 0.5 else None,
                            stock=random.randint(5, 100),
                            category=category,
                            brand=random.choice(brand_list),
                            color=random.choice(COLORS) if random.random() > 0.3 else '',
                            size=random.choice(SIZES) if random.random() > 0.5 else '',
                            material=random.choice(MATERIALS) if random.random() > 0.5 else '',
                            is_featured=random.random() > 0.8,
                            views_count=random.randint(0, 500),
                            purchases_count=random.randint(0, 50),
                        )
                        
                        # Add random tags
                        num_tags = random.randint(1, 3)
                        product.tags.set(random.sample(tags, num_tags))
                        
                        products.append(product)
                        product_id += 1
                
                if len(products) >= num_products:
                    break
            
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(products)} products'))
        
        # Create users
        self.stdout.write('Creating users...')
        users = []
        for i in range(num_users):
            user, created = User.objects.get_or_create(
                email=f'user{i}@example.com',
                defaults={
                    'username': f'user{i}',
                    'first_name': f'User{i}',
                    'last_name': f'Tester{i}',
                    'address': f'{random.randint(1, 999)} Main Street',
                    'city': random.choice(['Riyadh', 'Jeddah', 'Dammam', 'Makkah', 'Madinah']),
                    'country': 'Saudi Arabia',
                }
            )
            user.set_password('password123')
            user.save()
            users.append(user)
        
        # Create admin user
        admin, created = User.objects.get_or_create(
            email='admin@alkabry.com',
            defaults={
                'username': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'User',
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(users)} users + 1 admin'))
        
        # Create reviews
        self.stdout.write('Creating reviews...')
        reviews_created = 0
        
        for _ in range(num_reviews):
            if not products or not users:
                break
            
            product = random.choice(products)
            user = random.choice(users)
            
            # Skip if user already reviewed this product
            if Review.objects.filter(product=product, user=user).exists():
                continue
            
            rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]
            
            Review.objects.create(
                product=product,
                user=user,
                rating=rating,
                title=f'{"Great" if rating >= 4 else "Average" if rating == 3 else "Poor"} product',
                comment=f'This is a {rating}-star review. {"Highly recommended!" if rating >= 4 else "Could be better." if rating >= 3 else "Not satisfied."}',
                is_approved=True
            )
            reviews_created += 1
        
        # Update product ratings
        for product in products:
            product.update_rating()
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {reviews_created} reviews'))
        
        # Create user interactions
        self.stdout.write('Creating user interactions...')
        interactions_created = 0
        
        for _ in range(num_interactions):
            if not products or not users:
                break
            
            product = random.choice(products)
            user = random.choice(users)
            
            interaction_type = random.choices(
                ['view', 'click', 'add_to_cart', 'purchase', 'review'],
                weights=[40, 30, 15, 10, 5]
            )[0]
            
            UserInteraction.objects.create(
                user=user,
                product=product,
                interaction_type=interaction_type
            )
            interactions_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {interactions_created} interactions'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))
        self.stdout.write(self.style.SUCCESS(f'  Categories: {Category.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Products: {Product.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Users: {User.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Reviews: {Review.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Interactions: {UserInteraction.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.WARNING('\nAdmin credentials: admin@alkabry.com / admin123'))
        self.stdout.write(self.style.WARNING('User credentials: user0@example.com / password123'))
