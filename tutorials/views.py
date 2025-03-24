from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from .models import (
    Tutorial, Platform, Category, Language, Framework, 
    DifficultyLevel, LearningPath, UserProgress
)
from .forms import NewsletterForm, SearchForm

def home(request):
    # Get featured tutorials
    featured_tutorials = Tutorial.objects.filter(is_featured=True).order_by('-published_date')[:3]
    
    # Get social stats
    social_stats = [
        {'platform': 'YouTube', 'count': '150K+', 'label': 'Subscribers'},
        {'platform': 'TikTok', 'count': '500K+', 'label': 'Followers'},
        {'platform': 'LinkedIn', 'count': '100K+', 'label': 'Connections'},
    ]
    
    # Newsletter form
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for subscribing! Check your email to confirm your subscription.")
            return redirect('home')
    else:
        form = NewsletterForm()
    
    # Search form
    search_form = SearchForm()
    
    context = {
        'featured_tutorials': featured_tutorials,
        'social_stats': social_stats,
        'form': form,
        'search_form': search_form,
    }
    
    return render(request, 'tutorials/home.html', context)

def tutorial_list(request):
    # Get filter options
    languages = Language.objects.all()
    frameworks = Framework.objects.all()
    difficulty_levels = DifficultyLevel.objects.all().order_by('order')
    
    # Get selected filters
    language_filter = request.GET.get('language')
    framework_filter = request.GET.get('framework')
    difficulty_filter = request.GET.get('difficulty')
    duration_filter = request.GET.get('duration')
    sort_by = request.GET.get('sort')
    
    # Base queryset
    tutorials = Tutorial.objects.all()
    
    # Apply filters
    if language_filter:
        tutorials = tutorials.filter(language__slug=language_filter)
    
    if framework_filter:
        tutorials = tutorials.filter(framework__slug=framework_filter)
    
    if difficulty_filter:
        tutorials = tutorials.filter(difficulty__slug=difficulty_filter)
    
    if duration_filter:
        if duration_filter == '0-30':
            tutorials = tutorials.filter(read_time__lte=30)
        elif duration_filter == '30-60':
            tutorials = tutorials.filter(read_time__gt=30, read_time__lte=60)
        elif duration_filter == '60+':
            tutorials = tutorials.filter(read_time__gt=60)
    
    # Apply sorting
    if sort_by == 'recent':
        tutorials = tutorials.order_by('-published_date')
    elif sort_by == 'popular':
        tutorials = tutorials.order_by('-view_count')
    else:
        # Default sorting by published date
        tutorials = tutorials.order_by('-published_date')
    
    # Search functionality
    search_form = SearchForm(request.GET)
    if search_form.is_valid() and search_form.cleaned_data['query']:
        query = search_form.cleaned_data['query']
        tutorials = tutorials.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(categories__name__icontains=query) |
            Q(language__name__icontains=query) |
            Q(framework__name__icontains=query)
        ).distinct()
    
    # Pagination
    paginator = Paginator(tutorials, 6)  # 6 tutorials per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get learning paths
    learning_paths = LearningPath.objects.filter(is_featured=True)[:3]
    
    # Get popular categories
    popular_categories = Category.objects.all().order_by('-tutorial_count')[:5]
    
    # Get skill level distribution
    skill_distribution = DifficultyLevel.objects.annotate(
        count=Count('tutorial')
    ).values('name', 'count', 'color_class')
    
    # Newsletter form
    form = NewsletterForm()
    
    context = {
        'page_obj': page_obj,
        'languages': languages,
        'frameworks': frameworks,
        'difficulty_levels': difficulty_levels,
        'learning_paths': learning_paths,
        'popular_categories': popular_categories,
        'skill_distribution': list(skill_distribution),
        'selected_language': language_filter,
        'selected_framework': framework_filter,
        'selected_difficulty': difficulty_filter,
        'selected_duration': duration_filter,
        'selected_sort': sort_by,
        'form': form,
        'search_form': search_form,
    }
    
    return render(request, 'tutorials/tutorial_list.html', context)

def tutorial_detail(request, slug):
    tutorial = get_object_or_404(Tutorial, slug=slug)
    
    # Increment view count
    tutorial.increment_view_count()
    
    # Get related tutorials
    related_tutorials = Tutorial.objects.filter(
        Q(categories__in=tutorial.categories.all()) | 
        Q(language=tutorial.language) |
        Q(framework=tutorial.framework)
    ).exclude(id=tutorial.id).distinct()[:3]
    
    # Get learning paths that include this tutorial
    learning_paths = tutorial.learning_paths.all()
    
    # Newsletter form
    form = NewsletterForm()
    
    # Search form
    search_form = SearchForm()
    
    context = {
        'tutorial': tutorial,
        'related_tutorials': related_tutorials,
        'learning_paths': learning_paths,
        'form': form,
        'search_form': search_form,
    }
    
    return render(request, 'tutorials/tutorial_detail.html', context)

def learning_path_list(request):
    learning_paths = LearningPath.objects.all()
    
    # Search form
    search_form = SearchForm()
    
    context = {
        'learning_paths': learning_paths,
        'search_form': search_form,
    }
    
    return render(request, 'tutorials/learning_path_list.html', context)

def learning_path_detail(request, slug):
    learning_path = get_object_or_404(LearningPath, slug=slug)
    tutorials = learning_path.tutorials.all().order_by('id')  # Order by the order they were added
    
    # Get user progress if logged in
    user_progress = None
    if request.user.is_authenticated:
        user_progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            learning_path=learning_path
        )
    
    # Search form
    search_form = SearchForm()
    
    context = {
        'learning_path': learning_path,
        'tutorials': tutorials,
        'user_progress': user_progress,
        'search_form': search_form,
    }
    
    return render(request, 'tutorials/learning_path_detail.html', context)

@login_required
def mark_tutorial_complete(request, path_slug, tutorial_slug):
    learning_path = get_object_or_404(LearningPath, slug=path_slug)
    tutorial = get_object_or_404(Tutorial, slug=tutorial_slug)
    
    # Get or create user progress
    user_progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        learning_path=learning_path
    )
    
    # Mark tutorial as completed
    user_progress.completed_tutorials.add(tutorial)
    
    # Update progress percentage
    user_progress.update_progress()
    
    messages.success(request, f"You've completed '{tutorial.title}'!")
    
    return redirect('learning_path_detail', slug=path_slug)

@login_required
def mark_tutorial_incomplete(request, path_slug, tutorial_slug):
    learning_path = get_object_or_404(LearningPath, slug=path_slug)
    tutorial = get_object_or_404(Tutorial, slug=tutorial_slug)
    
    # Get user progress
    user_progress = get_object_or_404(UserProgress, user=request.user, learning_path=learning_path)
    
    # Mark tutorial as incomplete
    user_progress.completed_tutorials.remove(tutorial)
    
    # Update progress percentage
    user_progress.update_progress()
    
    messages.success(request, f"'{tutorial.title}' marked as incomplete.")
    
    return redirect('learning_path_detail', slug=path_slug)

