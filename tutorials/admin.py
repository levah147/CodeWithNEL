from django.contrib import admin
from .models import (
    Platform, Category, Language, Framework, Author, 
    DifficultyLevel, LearningPath, Tutorial, UserProgress,
    Subscriber
)

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_class')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'tutorial_count')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_class')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Framework)
class FrameworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'language')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('language',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__username')

@admin.register(DifficultyLevel)
class DifficultyLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_class', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)

@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_featured')
    prepopulated_fields = {'slug': ('title',)}
    # Removed filter_horizontal as it's causing issues

@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'framework', 'difficulty', 'author', 'read_time', 'view_count', 'published_date', 'is_featured')
    list_filter = ('language', 'framework', 'difficulty', 'categories', 'is_featured', 'published_date')
    search_fields = ('title', 'description', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    filter_horizontal = ('categories', 'learning_paths')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'content', 'image')
        }),
        ('Categorization', {
            'fields': ('platform', 'categories', 'language', 'framework', 'difficulty', 'learning_paths')
        }),
        ('Publication', {
            'fields': ('author', 'published_date', 'read_time', 'is_featured')
        }),
    )

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'learning_path', 'progress_percentage', 'last_updated')
    list_filter = ('learning_path', 'progress_percentage')
    search_fields = ('user__username', 'learning_path__title')
    filter_horizontal = ('completed_tutorials',)
    readonly_fields = ('progress_percentage', 'last_updated')

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'subscribed_date', 'is_active')
    list_filter = ('is_active', 'subscribed_date')
    search_fields = ('email', 'name')

