import os

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.db import connection

from products.models import Product, Review
from recommendations.models import UserInteraction
from recommendations.services import RecommendationService


DATASET_PATH = 'data/fashion-product-images-small/styles.csv'
DEFAULT_NUM_PRODUCTS = 5000
DEFAULT_INTERACTIONS = 10000
DEFAULT_USERS = 200


class Command(BaseCommand):
    help = (
        'Replace synthetic seed data with real Kaggle fashion data, retrain recommendation models, '
        'and print final evaluation metrics.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--interactions', type=int, default=DEFAULT_INTERACTIONS,
            help='Number of synthetic interactions to generate after importing real products.'
        )
        parser.add_argument(
            '--users', type=int, default=DEFAULT_USERS,
            help='Minimum number of users to ensure for generating interactions.'
        )

    def handle(self, *args, **options):
        interactions = options['interactions']
        users = options['users']

        self.stdout.write('Deleting old synthetic data...')
        self._delete_old_data()
        self.stdout.write(self.style.SUCCESS('Deleted old products, interactions, and reviews.'))

        self.stdout.write('Resetting primary key sequences...')
        self._reset_sequences([Product, Review, UserInteraction])
        self.stdout.write(self.style.SUCCESS('Primary key sequences reset.'))

        if not os.path.isfile(DATASET_PATH):
            raise CommandError(
                f'Required dataset not found at {DATASET_PATH}. Make sure styles.csv exists in the dataset folder.'
            )

        self.stdout.write('Importing real products from Kaggle...')
        self.stdout.write(f'  CSV file: {DATASET_PATH}')
        self.stdout.write(f'  num-products: {DEFAULT_NUM_PRODUCTS}')
        self.stdout.write(f'  interactions: {interactions}')
        self.stdout.write(f'  users: {users}')

        try:
            call_command(
                'import_fashion_data',
                '--csv-file', DATASET_PATH,
                '--num-products', str(DEFAULT_NUM_PRODUCTS),
                '--interactions', str(interactions),
                '--users', str(users),
                verbosity=1,
            )
        except Exception as exc:
            raise CommandError(f'Failed to import real data: {exc}')

        product_count = Product.objects.count()
        interaction_count = UserInteraction.objects.count()
        non_superuser_count = get_user_model().objects.filter(is_superuser=False).count()

        self.stdout.write(self.style.SUCCESS('Imported real Kaggle data successfully.'))
        self.stdout.write(self.style.SUCCESS(
            f'Summary after import: {product_count} products, {interaction_count} interactions, {non_superuser_count} non-superuser users.'
        ))

        self.stdout.write('Retraining recommendation models...')
        try:
            call_command('retrain_recommendation_models', verbosity=1)
        except Exception as exc:
            raise CommandError(f'Retraining recommendation models failed: {exc}')
        self.stdout.write(self.style.SUCCESS('Recommendation models retrained successfully.'))

        self.stdout.write('Evaluating recommendation models...')
        service = RecommendationService()
        algorithm_metrics = {}

        for algorithm in service.ALGORITHMS:
            self.stdout.write(f'  Evaluating {algorithm}...')
            metrics = service.evaluate_algorithm(algorithm) or {}
            algorithm_metrics[algorithm] = metrics
            self.stdout.write(
                f'    {algorithm}: Precision@10={metrics.get("precision", 0.0):.4f}, '
                f'Hit Rate@10={metrics.get("hit_rate", 0.0):.4f}, NDCG@10={metrics.get("ndcg", 0.0):.4f}'
            )

        self.stdout.write(self.style.SUCCESS('Final evaluation metrics complete.'))
        self.stdout.write('\nFinal switch_to_real_data summary:')
        self.stdout.write(f'  Products imported: {product_count}')
        self.stdout.write(f'  Interactions generated: {interaction_count}')
        self.stdout.write(f'  Active users: {non_superuser_count}')

        for algorithm, metrics in algorithm_metrics.items():
            self.stdout.write(
                f'  {algorithm}: Precision@10={metrics.get("precision", 0.0):.4f}, '
                f'Hit Rate@10={metrics.get("hit_rate", 0.0):.4f}, NDCG@10={metrics.get("ndcg", 0.0):.4f}'
            )

    def _delete_old_data(self):
        UserInteraction.objects.all().delete()
        Review.objects.all().delete()
        Product.objects.all().delete()

    def _reset_sequences(self, models):
        try:
            sequence_sql = connection.ops.sequence_reset_sql(no_style(), models)
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
        except Exception:
            pass
