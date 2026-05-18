"""
Management command to seed the database with sample data for testing recommendation algorithms.
Creates categories, products, users, reviews, and interactions.
"""
import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
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
    'Fashion': ['Nike', 'Adidas', 'Zara', 'H&M', 'Levi\'s', 'Gucci'],
    'Accessories': ['Coach', 'Michael Kors', 'Ray-Ban', 'Fossil', 'Pandora'],
    'Activewear': ['Under Armour', 'Lululemon', 'Reebok', 'Puma', 'Nike'],
    'Trends': ['Supreme', 'Off-White', 'Balenciaga', 'Vetements', 'Palace'],
}

PRODUCT_NAMES = {
    'Shirts': ['Premium Cotton Shirt', 'Striped Dress Shirt', 'Linen Button-Up', 'Chambray Shirt', 'Flannel Shirt'],
    'Pants': ['Tailored Chinos', 'Slim Fit Trousers', 'Cargo Pants', 'Corduroy Pants', 'Wide-Leg Pants'],
    'Dresses': ['Summer Midi Dress', 'Cocktail Dress', 'Maxi Dress', 'A-Line Dress', 'Wrap Dress'],
    'Jackets': ['Leather Jacket', 'Denim Jacket', 'Windbreaker', 'Puffer Jacket', 'Bomber Jacket'],
    'Shoes': ['Running Sneakers', 'Casual Loafers', 'Chelsea Boots', 'Espadrille Flats', 'Sporty Trainers'],
    'Bags': ['Leather Tote Bag', 'Canvas Backpack', 'Crossbody Bag', 'Clutch Purse', 'Weekend Duffel'],
    'Hats': ['Baseball Cap', 'Wide Brim Hat', 'Beanie', 'Fedora', 'Bucket Hat'],
    'Sunglasses': ['Aviator Shades', 'Round Sunglasses', 'Cat Eye Sunglasses', 'Sport Sunglasses', 'Oversized Sunglasses'],
    'Jewelry': ['Gold Pendant Necklace', 'Silver Hoop Earrings', 'Charm Bracelet', 'Layered Necklace', 'Stackable Rings'],
    'Scarves': ['Silk Scarf', 'Wool Wrap', 'Cashmere Scarf', 'Infinity Scarf', 'Plaid Scarf'],
    'Leggings': ['High-Waist Leggings', 'Performance Leggings', 'Printed Leggings', 'Seamless Leggings', 'Yoga Leggings'],
    'Sports Tops': ['Mesh Training Tank', 'Running Crop Top', 'Long Sleeve Workout Top', 'Performance Tee', 'Training Hoodie'],
    'Track Pants': ['Slim Track Pants', 'Relaxed Sweatpants', 'Zip Pocket Track Pants', 'Cuffed Joggers', 'Performance Track Pants'],
    'Windbreakers': ['Lightweight Windbreaker', 'Packable Windbreaker', 'Hooded Windbreaker', 'Colorblock Windbreaker', 'Reflective Windbreaker'],
    'Sneakers': ['Retro Sneakers', 'Chunky Sneakers', 'Slip-On Sneakers', 'Court Sneakers', 'Platform Sneakers'],
    'Bestsellers': ['Iconic Crewneck Sweatshirt', 'Best-Selling Denim Jacket', 'Fan-Favorite Leather Jacket', 'Top-Rated Boho Dress', 'Customer Favorite Hoodie'],
    'New Arrivals': ['New Season Trench', 'Limited Edit Denim', 'Fresh Color Hoodie', 'New Cut Blazer', 'Modern Wrap Dress'],
    'Sale Items': ['Discounted Knit Sweater', 'Sale Denim Shorts', 'Clearance Slip Dress', 'Marked Down Bomber Jacket', 'Price Drop Anorak'],
    'Limited Edition': ['Limited Edition Leather Jacket', 'Collector Hoodie', 'Signature Denim Jeans', 'Special Release Sneaker', 'Exclusive Quilted Coat'],
    'Seasonal': ['Summer Linen Shirt', 'Winter Wool Coat', 'Autumn Knit Pullover', 'Spring Floral Dress', 'Holiday Velvet Blazer'],
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
    
    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=30, help='Number of users to create')
        parser.add_argument('--products', type=int, default=80, help='Number of products to create')
        parser.add_argument('--reviews', type=int, default=200, help='Number of reviews to create')
        parser.add_argument('--interactions', type=int, default=500, help='Number of interactions to create')
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        
        num_users = options['users']
        num_products = options['products']
        num_reviews = options['reviews']
        num_interactions = options['interactions']
        
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
        
        for category_name, category in categories.items():
            if category_name in PRODUCT_NAMES:
                for name in PRODUCT_NAMES[category_name]:
                    if len(products) >= num_products:
                        break
                    
                    parent_category = category.parent if category.parent else category
                    brand_list = BRANDS.get(parent_category.name, ['Generic'])
                    
                    product = Product.objects.create(
                        name=name,
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
