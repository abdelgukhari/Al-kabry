from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import AlgorithmMetrics, ComparisonReport
from recommendations.services import RecommendationService
from recommendations.models import RecommendationEvent
from products.models import Product
from orders.models import Order


@staff_member_required
def algorithm_performance_api(request):
    """API endpoint for algorithm performance data."""
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)

    data = {}
    for algo in RecommendationService.ALGORITHMS:
        metrics = AlgorithmMetrics.objects.filter(
            algorithm=algo,
            date__gte=start_date
        ).aggregate(
            avg_precision=Avg('precision'),
            avg_recall=Avg('recall'),
            avg_f1=Avg('f1_score'),
            avg_ndcg=Avg('ndcg'),
            avg_diversity=Avg('diversity'),
            avg_coverage=Avg('coverage'),
        )

        data[algo] = metrics

    return JsonResponse(data)


@staff_member_required
def compare_view(request):
    """Compare all algorithms side by side."""
    service = RecommendationService()

    # Get evaluation metrics for each algorithm
    evaluations = {}
    for algo in RecommendationService.ALGORITHMS:
        metrics = service.evaluate_algorithm(algo)
        if metrics:
            evaluations[algo] = metrics

    # Get historical performance
    historical_data = {}
    for algo in RecommendationService.ALGORITHMS:
        metrics = AlgorithmMetrics.objects.filter(
            algorithm=algo
        ).order_by('-date')[:30]

        historical_data[algo] = {
            'ctr': [(m.date.strftime('%Y-%m-%d'), m.ctr * 100) for m in metrics],
            'conversion_rate': [(m.date.strftime('%Y-%m-%d'), m.conversion_rate * 100) for m in metrics],
            'revenue': [(m.date.strftime('%Y-%m-%d'), float(m.total_revenue)) for m in metrics],
        }

    # Determine winner
    if evaluations:
        # Score algorithms based on weighted metrics
        scores = {}
        for algo, metrics in evaluations.items():
            scores[algo] = (
                metrics.get('precision', 0) * 0.25 +
                metrics.get('recall', 0) * 0.25 +
                metrics.get('ndcg', 0) * 0.30 +
                metrics.get('diversity', 0) * 0.10 +
                metrics.get('coverage', 0) * 0.10
            )

        winner = max(scores.items(), key=lambda x: x[1])[0] if scores else None
    else:
        winner = None
        scores = {}

    context = {
        'evaluations': evaluations,
        'historical_data': historical_data,
        'scores': scores,
        'winner': winner,
    }
    return render(request, 'analytics/compare.html', context)


@staff_member_required
def generate_report_view(request):
    """Generate a comparison report."""
    service = RecommendationService()

    # Evaluate all algorithms
    evaluations = {}
    for algo in RecommendationService.ALGORITHMS:
        metrics = service.evaluate_algorithm(algo)
        if metrics:
            evaluations[algo] = metrics

    # Score and rank
    scores = {}
    for algo, metrics in evaluations.items():
        scores[algo] = (
            metrics.get('precision', 0) * 0.25 +
            metrics.get('recall', 0) * 0.25 +
            metrics.get('ndcg', 0) * 0.30 +
            metrics.get('diversity', 0) * 0.10 +
            metrics.get('coverage', 0) * 0.10
        )

    ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    winner = ranking[0][0] if ranking else None

    # Create report
    report = ComparisonReport.objects.create(
        title=f'Algorithm Comparison Report - {timezone.now().strftime("%Y-%m-%d")}',
        description='Comprehensive comparison of all recommendation algorithms',
        metrics_data=evaluations,
        ranking=[{'algorithm': algo, 'score': score} for algo, score in ranking],
        winner=winner,
        start_date=timezone.now() - timedelta(days=30),
        end_date=timezone.now(),
        is_final=True,
    )

    return render(request, 'analytics/report.html', {
        'report': report,
        'evaluations': evaluations,
        'ranking': ranking,
        'winner': winner,
    })
