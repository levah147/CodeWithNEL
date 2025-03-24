from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import BlogPost, BlogCategory, Tag, PopularPost
from tutorials.forms import SearchForm, NewsletterForm

def blog_list(request):
    # Get all categories for filtering
    categories = BlogCategory.objects.all()
    tags = Tag.objects.all()
    
    # Get selected category filter
    category_filter = request.GET.get('category')
    tag_filter = request.GET.get('tag')
    
    # Base queryset
    posts = BlogPost.objects.all().order_by('-published_date')
    
    # Apply category filter if selected
    if category_filter:
        posts = posts.filter(category__slug=category_filter)
    
    # Apply tag filter if selected
    if tag_filter:
        posts = posts.filter(tags__slug=tag_filter)
    
    # Search functionality
    search_form = SearchForm(request.GET)
    if search_form.is_valid() and search_form.cleaned_data['query']:
        query = search_form.cleaned_data['query']
        posts = posts.filter(
            Q(title__icontains=query) | 
            Q(excerpt__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    
    # Pagination
    paginator = Paginator(posts, 6)  # 6 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get popular posts
    popular_posts = PopularPost.objects.all()[:3]
    
    # Newsletter form
    form = NewsletterForm()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'tags': tags,
        'selected_category': category_filter,
        'selected_tag': tag_filter,
        'popular_posts': popular_posts,
        'form': form,
        'search_form': search_form,
    }
    
    return render(request, 'blog/blog_list.html', context)

def blog_post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    
    # Increment view count
    post.increment_view_count()
    
    # Get related posts
    related_posts = BlogPost.objects.filter(
        Q(category=post.category) | Q(tags__in=post.tags.all())
    ).exclude(id=post.id).distinct()[:3]
    
    # Get popular posts
    popular_posts = PopularPost.objects.all()[:3]
    
    # Get all categories
    categories = BlogCategory.objects.all()
    
    # Get all tags
    tags = Tag.objects.all()
    
    # Newsletter form
    form = NewsletterForm()
    
    # Search form
    search_form = SearchForm()
    
    context = {
        'post': post,
        'related_posts': related_posts,
        'popular_posts': popular_posts,
        'categories': categories,
        'tags': tags,
        'form': form,
        'search_form': search_form,
    }
    
    return render(request, 'blog/blog_post_detail.html', context)

