from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Avg
from django.contrib import messages
from .models import Product, Category, Tag, Review
from .forms import ReviewForm
from recommendations.services import RecommendationService
from cart.cart import CartHandler
import django_filters


class ProductFilter(django_filters.FilterSet):
    """Filter products by various criteria."""
    
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    brand = django_filters.CharFilter(lookup_expr='icontains')
    color = django_filters.CharFilter(lookup_expr='iexact')
    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='exact')
    tag = django_filters.ModelMultipleChoiceFilter(field_name='tags', queryset=Tag.objects.all())
    
    class Meta:
        model = Product
        fields = ['price_min', 'price_max', 'brand', 'color', 'category', 'tag']


def home_view(request):
    """Home page with featured products and recommendations."""
    featured_products = Product.objects.filter(
        is_featured=True, is_available=True, is_active=True
    )[:8]

    # Get recommendations for user
    recommendation_service = RecommendationService()
    recommended_products = []

    if request.user.is_authenticated:
        recommended_products = recommendation_service.get_recommendations_for_user(
            request.user, algorithm='hybrid', limit=8
        )
    else:
        # For anonymous users, show popular products
        recommended_products = Product.objects.filter(
            is_available=True, is_active=True
        ).order_by('-views_count', '-purchases_count')[:8]

    # Latest products
    latest_products = Product.objects.filter(
        is_available=True, is_active=True
    ).order_by('-created_at')[:8]

    context = {
        'featured_products': featured_products,
        'recommended_products': recommended_products,
        'latest_products': latest_products,
        'categories': Category.objects.filter(is_active=True)[:10],
    }
    return render(request, 'products/home.html', context)


def product_list_view(request):
    """List all products with filtering."""
    products = Product.objects.filter(is_available=True, is_active=True)
    categories = Category.objects.filter(is_active=True)
    tags = Tag.objects.all()
    
    product_filter = ProductFilter(request.GET, queryset=products)
    filtered_products = product_filter.qs
    
    # Pagination
    page_number = request.GET.get('page', 1)
    per_page = 12
    
    # HTMX support for dynamic filtering
    if request.htmx:
        return render(request, 'products/partials/product_grid.html', {
            'products': filtered_products,
            'page_obj': _paginate(filtered_products, page_number, per_page),
        })
    
    context = {
        'filter': product_filter,
        'products': filtered_products,
        'page_obj': _paginate(filtered_products, page_number, per_page),
        'categories': categories,
        'tags': tags,
    }
    return render(request, 'products/list.html', context)


def product_detail_view(request, slug):
    """Product detail page with recommendations."""
    product = get_object_or_404(
        Product, slug=slug, is_active=True
    )
    
    # Increment view count
    product.views_count += 1
    product.save(update_fields=['views_count'])
    
    # Track view
    from recommendations.models import UserInteraction
    UserInteraction.track_interaction(
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key,
        product=product,
        interaction_type='view'
    )
    
    # Get related products
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    # Get recommendations
    recommendation_service = RecommendationService()
    recommended_products = []
    
    if request.user.is_authenticated:
        recommended_products = recommendation_service.get_recommendations_for_user(
            request.user, algorithm='hybrid', limit=6, exclude_ids=[product.id]
        )
    
    # Reviews
    reviews = product.reviews.filter(is_approved=True).order_by('-created_at')[:5]
    review_form = ReviewForm() if request.user.is_authenticated else None
    
    context = {
        'product': product,
        'related_products': related_products,
        'recommended_products': recommended_products,
        'reviews': reviews,
        'review_form': review_form,
    }
    return render(request, 'products/detail.html', context)


def add_review_view(request, slug):
    """Add a review for a product."""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            
            # Update product rating
            product.update_rating()
            
            # Track interaction
            from recommendations.models import UserInteraction
            UserInteraction.track_interaction(
                user=request.user,
                product=product,
                interaction_type='review'
            )
            
            messages.success(request, 'Review submitted successfully!')
            return redirect('products:detail', slug=slug)
    
    return redirect('products:detail', slug=slug)


def category_view(request, slug):
    """View products in a category."""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(
        category=category, is_available=True, is_active=True
    )
    
    page_number = request.GET.get('page', 1)
    per_page = 12
    
    context = {
        'category': category,
        'products': products,
        'page_obj': _paginate(products, page_number, per_page),
    }
    return render(request, 'products/category.html', context)


def search_view(request):
    """Search products."""
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(brand__icontains=query) |
        Q(tags__name__icontains=query),
        is_available=True,
        is_active=True
    ).distinct() if query else Product.objects.none()
    
    page_number = request.GET.get('page', 1)
    
    context = {
        'query': query,
        'products': products,
        'page_obj': _paginate(products, page_number, 12),
    }
    return render(request, 'products/search.html', context)


def ajax_search_view(request):
    """AJAX search for products (HTMX)."""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return render(request, 'products/partials/search_results.html', {
            'products': [],
            'query': query,
        })
    
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(brand__icontains=query),
        is_available=True,
        is_active=True
    ).distinct()[:10]
    
    return render(request, 'products/partials/search_results.html', {
        'products': products,
        'query': query,
    })


def _paginate(queryset, page_number, per_page):
    """Helper to paginate a queryset."""
    from django.core.paginator import Paginator
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(page_number)
