import csv
import os
import random
import time
import uuid
import pandas as pd
from pathlib import Path
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import connection, OperationalError
from django.utils.text import slugify
from products.models import Category, Tag, Product, Review
from recommendations.models import UserInteraction

User = get_user_model()


class Command(BaseCommand):
    help = 'Import Kaggle fashion dataset and generate high-value user interactions.'

    def add_arguments(self, parser):
        parser.add_argument('--csv-file', type=str, required=True,
            help='Path to the Kaggle styles.csv file from fashion-product-images-small')
        parser.add_argument('--num-products', type=int, default=5000,
            help='Number of products to import from the Kaggle dataset')
        parser.add_argument('--images-dir', type=str, default=None,
            help='Optional directory containing downloaded product images')
        parser.add_argument('--interactions', type=int, default=10000,
            help='Number of user interactions to generate for imported products')
        parser.add_argument('--users', type=int, default=200,
            help='Minimum number of users to create for interaction generation')
        parser.add_argument('--force', action='store_true',
            help='Update existing products with matching SKU instead of skipping them')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        images_dir = options.get('images_dir')
        num_products = options['num_products']
        interaction_target = options['interactions']
        force = options['force']

        self.stdout.write('Importing Kaggle fashion dataset...')
        df = self._load_dataframe(csv_file)
        self.stdout.write(self.style.SUCCESS(f'Loaded {len(df)} rows from {csv_file}'))

        imported_products = self._import_products(
            df=df,
            num_products=num_products,
            images_dir=images_dir,
            force=force
        )

        if not imported_products:
            raise CommandError('No products were imported. Check the CSV file or import options.')

        self.stdout.write(self.style.SUCCESS(f'Imported {len(imported_products)} products.'))

        users = self._get_or_create_users(min_users=options['users'])
        users = users[:options['users']]
        self.stdout.write(self.style.SUCCESS(f'Using {len(users)} users for interaction generation.'))

        interactions_count, purchases_count, reviews_count = self._generate_interactions(
            users=users,
            products=imported_products,
            target_interactions=interaction_target
        )

        self.stdout.write(self.style.SUCCESS(
            f'Generated {interactions_count} interactions, {purchases_count} purchases, {reviews_count} reviews.'
        ))

    def _load_dataframe(self, csv_file):
        if not os.path.isfile(csv_file):
            raise CommandError(f'CSV file not found: {csv_file}')

        try:
            df = pd.read_csv(csv_file, low_memory=False)
        except Exception as exc:
            self.stdout.write(self.style.WARNING(
                f'Primary CSV load failed ({exc}). Retrying with robust parser...'
            ))
            try:
                df = pd.read_csv(
                    csv_file,
                    engine='python',
                    quoting=csv.QUOTE_MINIMAL,
                    on_bad_lines='skip',
                    encoding='ISO-8859-1'
                )
            except Exception as inner_exc:
                raise CommandError(
                    f'Failed to parse CSV file {csv_file}: {inner_exc}'
                )

        if df.empty:
            raise CommandError('The CSV file is empty or could not be loaded.')

        return df.fillna('')

    def _get_or_create_users(self, min_users=100):
        users = list(User.objects.filter(is_superuser=False).order_by('id'))
        if len(users) >= min_users:
            if len(users) > min_users:
                self.stdout.write(self.style.WARNING(
                    f'Found {len(users)} users, but only {min_users} are requested. Using the first {min_users} users.'
                ))
            return users[:min_users]

        if users:
            self.stdout.write(self.style.WARNING(
                f'Found {len(users)} users, but {min_users} are required. Creating additional demo users.'
            ))
        else:
            self.stdout.write(
                f'No ordinary users found. Creating {min_users} demo users for import interactions.'
            )

        return self._create_import_users(min_users, existing_users=users)

    def _create_import_users(self, count, existing_users=None):
        users = list(existing_users or [])
        start_index = len(users)
        for index in range(start_index, count):
            email = f'kaggle_import_user{index}@example.com'
            user, _ = self._retry_db_operation(
                User.objects.get_or_create,
                email=email,
                defaults={'username': f'kaggle_import_user{index}', 'first_name': 'KaggleImport'}
            )
            user.set_password('password123')
            self._retry_db_operation(user.save)
            users.append(user)
        return users

    def _get_kaggle_sku(self, row):
        sku_columns = ['id', 'article_id', 'product_id', 'style_id', 'item_id']
        for key in sku_columns:
            if key in row and row[key] != '':
                return str(row[key]).strip()
        return f'KAGGLE-{uuid.uuid4().hex[:10].upper()}'

    def _first_available(self, row, keys):
        for key in keys:
            if key in row and row[key] != '':
                value = str(row[key]).strip()
                if value:
                    return value
        return ''

    def _slugify_unique(self, base, existing_slugs):
        slug = slugify(base)
        if not slug:
            slug = 'product'
        original = slug
        counter = 1
        while slug in existing_slugs:
            slug = f'{original}-{counter}'
            counter += 1
        existing_slugs.add(slug)
        return slug

    def _get_or_create_tag(self, tag_name):
        if not tag_name:
            raise ValueError('Tag name must be provided')

        tag_slug = slugify(tag_name)
        if not tag_slug:
            tag_slug = slugify('tag')

        tag, created = self._retry_db_operation(
            Tag.objects.get_or_create,
            slug=tag_slug,
            defaults={'name': tag_name}
        )
        return tag

    def _get_stock(self, row):
        try:
            return int(row.get('stock', random.randint(10, 200)))
        except Exception:
            return random.randint(10, 200)

    def _get_price(self, row):
        price_columns = ['price', 'sales_price', 'rrp', 'cost_price', 'price_sales']
        for key in price_columns:
            if key in row and row[key] != '':
                try:
                    return round(float(row[key]), 2)
                except (ValueError, TypeError):
                    continue
        return round(random.uniform(10, 150), 2)

    def _get_category_name(self, row):
        master = self._first_available(row, ['masterCategory', 'master_category', 'department_name'])
        sub = self._first_available(row, ['subCategory', 'sub_category', 'articleType', 'product_group_name', 'product_type_name', 'article_type_name'])
        if master and sub and sub.lower() not in master.lower():
            return f'{master} > {sub}'
        return master or sub or 'Kaggle Fashion'

    def _get_product_name(self, row):
        name = self._first_available(row, ['productDisplayName', 'product_display_name', 'product_name', 'article_name', 'detail_desc', 'graphical_appearance_name', 'index_name'])
        if name:
            return name
        return self._first_available(row, ['articleType', 'product_type_name', 'article_type_name']) or 'Kaggle Fashion Product'

    def _get_brand(self, row):
        brand = self._first_available(row, ['brand', 'brand_name', 'index_group_name'])
        if brand:
            return brand

        display_name = str(row.get('productDisplayName', '') or '').strip()
        if display_name:
            candidate = display_name.split()[0]
            if candidate and len(candidate) > 2 and not candidate.isdigit():
                return candidate

        return 'Kaggle Fashion'

    def _get_color(self, row):
        color = self._first_available(row, ['baseColour', 'base_colour', 'colour_group_name', 'perceived_colour_value_name', 'perceived_colour_master_name', 'colour_code', 'color'])
        return color or ''

    def _get_description(self, row, name):
        description = self._first_available(row, ['detail_desc', 'productDisplayName', 'product_name', 'article_name'])
        if description:
            return description

        parts = []
        category = self._get_category_name(row)
        color = self._get_color(row)
        gender = self._first_available(row, ['gender'])
        season = self._first_available(row, ['season'])
        usage = self._first_available(row, ['usage'])

        if category:
            parts.append(f'Category: {category}')
        if color:
            parts.append(f'Color: {color}')
        if gender:
            parts.append(f'Gender: {gender}')
        if season:
            parts.append(f'Season: {season}')
        if usage:
            parts.append(f'Usage: {usage}')

        if parts:
            return f'{name} imported from Kaggle fashion dataset. ' + ' '.join(parts)

        return f'{name} imported from Kaggle fashion dataset.'

    def _get_image_filename(self, row):
        image_keys = ['image', 'image_name', 'image_path', 'picture', 'img', 'image_url']
        image_value = self._first_available(row, image_keys)
        if not image_value:
            return None
        return os.path.basename(str(image_value))

    def _attach_image(self, product, images_dir, image_name):
        if not image_name or not images_dir:
            return

        image_path = Path(images_dir) / image_name
        if not image_path.exists():
            return

        with image_path.open('rb') as file_obj:
            product.image.save(image_path.name, File(file_obj), save=True)

    def _retry_db_operation(self, func, *args, retries=5, delay=0.5, **kwargs):
        for attempt in range(1, retries + 1):
            try:
                return func(*args, **kwargs)
            except OperationalError as exc:
                if 'database is locked' not in str(exc).lower():
                    raise
                if attempt == retries:
                    raise
                self.stdout.write(self.style.WARNING(
                    f'Database locked on attempt {attempt}/{retries}. Retrying in {delay} seconds...'
                ))
                connection.close()
                time.sleep(delay)
        return func(*args, **kwargs)

    def _import_products(self, df, num_products, images_dir, force):
        existing_slugs = set(Product.objects.values_list('slug', flat=True))
        imported_products = []
        categories = {}

        for _, row in df.head(num_products).iterrows():
            sku = self._get_kaggle_sku(row)
            name = self._get_product_name(row)
            category_name = self._get_category_name(row)
            brand = self._get_brand(row)
            color = self._get_color(row)
            price = self._get_price(row)
            description = self._get_description(row, name)
            stock = self._get_stock(row)
            image_filename = self._get_image_filename(row)

            category = categories.get(category_name)
            if not category:
                category, _ = self._retry_db_operation(
                    Category.objects.get_or_create,
                    name=category_name,
                    defaults={
                        'description': f'Imported category from Kaggle dataset.',
                        'is_active': True
                    }
                )
                categories[category_name] = category

            slug = self._slugify_unique(name, existing_slugs)
            defaults = {
                'name': name,
                'slug': slug,
                'description': description,
                'price': price,
                'compare_price': round(price * random.uniform(1.05, 1.3), 2),
                'stock': stock,
                'category': category,
                'brand': brand,
                'color': color,
                'is_active': True,
                'is_available': True,
            }

            existing_product = Product.objects.filter(sku=sku).first()
            if existing_product and not force:
                self.stdout.write(self.style.WARNING(f'Skipped existing product sku={sku}'))
                continue

            product, created = self._retry_db_operation(
                Product.objects.update_or_create,
                sku=sku,
                defaults={**defaults, 'sku': sku}
            )

            if image_filename and images_dir:
                self._attach_image(product, images_dir, image_filename)

            tag_names = set()
            if category_name:
                tag_names.add(category_name.lower().replace(' ', '-'))
            if color:
                tag_names.add(color.lower().replace(' ', '-'))
            if brand:
                tag_names.add(brand.lower().replace(' ', '-'))

            for tag_name in tag_names:
                tag = self._get_or_create_tag(tag_name)
                product.tags.add(tag)

            if created:
                imported_products.append(product)
            else:
                if force:
                    imported_products.append(product)
                else:
                    self.stdout.write(self.style.WARNING(f'Skipped existing product sku={sku}'))

        return imported_products

    def _generate_interactions(self, users, products, target_interactions):
        if not users:
            return 0, 0, 0

        interactions = []
        reviews = []
        purchases = 0
        total = 0
        product_catalog = {}

        # Build set of existing (user, product) reviews to avoid duplicates
        reviewed_pairs = set(
            Review.objects.filter(
                user__in=users,
                product__in=products
            ).values_list('user_id', 'product_id')
        )

        # Organize products by category name
        for product in products:
            category_name = product.category.name if product.category else 'Unknown'
            product_catalog.setdefault(category_name, []).append(product)

        categories = list(product_catalog.keys()) or ['Unknown']

        # Generate interactions
        for _ in range(target_interactions):
            user = random.choice(users)
            # 80% chance to pick a product from a random category, else any category
            if random.random() < 0.80 and categories:
                category_name = random.choice(categories)
            else:
                category_name = random.choice(categories)

            available_products = product_catalog.get(category_name) or products
            product = random.choice(available_products)

            interaction_type = random.choices(
                ['view', 'click', 'add_to_cart', 'purchase', 'review'],
                weights=[0.45, 0.25, 0.15, 0.10, 0.05],
                k=1
            )[0]

            # Add interaction to list
            interactions.append(UserInteraction(
                user=user,
                product=product,
                interaction_type=interaction_type,
                weight={
                    'view': 1.0,
                    'click': 2.0,
                    'add_to_cart': 4.0,
                    'purchase': 5.0,
                    'review': 5.0,
                }.get(interaction_type, 1.0)
            ))

            # Update product counters and possibly create a review
            if interaction_type == 'view':
                product.views_count += 1
            elif interaction_type == 'purchase':
                product.purchases_count += 1
                purchases += 1
                # 50% chance to add a review after purchase (if not already reviewed)
                if random.random() < 0.50 and (user.id, product.id) not in reviewed_pairs:
                    reviews.append(Review(
                        product=product,
                        user=user,
                        rating=random.choice([4, 5]),
                        title='Great product',
                        comment='This was a good purchase and matched expectations.',
                        is_approved=True
                    ))
                    reviewed_pairs.add((user.id, product.id))
            elif interaction_type == 'review':
                if (user.id, product.id) not in reviewed_pairs:
                    reviews.append(Review(
                        product=product,
                        user=user,
                        rating=random.choice([4, 5]),
                        title='Nice item',
                        comment='The product is exactly as described and worth recommending.',
                        is_approved=True
                    ))
                    reviewed_pairs.add((user.id, product.id))

            total += 1

        # Bulk create interactions in chunks
        chunk_size_interactions = 500
        for i in range(0, len(interactions), chunk_size_interactions):
            self._retry_db_operation(
                UserInteraction.objects.bulk_create,
                interactions[i:i + chunk_size_interactions],
                batch_size=chunk_size_interactions
            )

        # Bulk create reviews in chunks
        if reviews:
            chunk_size_reviews = 200
            for i in range(0, len(reviews), chunk_size_reviews):
                self._retry_db_operation(
                    Review.objects.bulk_create,
                    reviews[i:i + chunk_size_reviews],
                    batch_size=chunk_size_reviews
                )

        # Bulk update product counts
        if products:
            chunk_size_products = 500
            for i in range(0, len(products), chunk_size_products):
                self._retry_db_operation(
                    Product.objects.bulk_update,
                    products[i:i + chunk_size_products],
                    ['views_count', 'purchases_count'],
                    batch_size=chunk_size_products
                )

        return total, purchases, len(reviews)