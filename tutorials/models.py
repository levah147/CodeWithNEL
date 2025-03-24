from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User

class Platform(models.Model):
    name = models.CharField(max_length=50)
    icon_class = models.CharField(max_length=50, help_text="Remix icon class name")
    color_class = models.CharField(max_length=50, help_text="Tailwind color class")
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    tutorial_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def update_tutorial_count(self):
        self.tutorial_count = self.tutorial_set.count()
        self.save()

class Language(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    color_class = models.CharField(max_length=50, help_text="Tailwind color class for badge", default="blue")
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Framework(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="frameworks")
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='authors/', blank=True, null=True)
    
    def __str__(self):
        return self.name

class DifficultyLevel(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(unique=True)
    color_class = models.CharField(max_length=50, help_text="Tailwind color class for badge")
    order = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class LearningPath(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='learning_paths/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('learning_path_detail', kwargs={'slug': self.slug})

class Tutorial(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    content = models.TextField()
    image = models.ImageField(upload_to='tutorials/')
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)
    framework = models.ForeignKey(Framework, on_delete=models.SET_NULL, null=True, blank=True)
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, blank=True)
    learning_paths = models.ManyToManyField(LearningPath, blank=True, related_name="tutorials")
    read_time = models.PositiveIntegerField(help_text="Estimated read time in minutes")
    view_count = models.PositiveIntegerField(default=0)
    published_date = models.DateField()
    is_featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
        # Update category tutorial count
        for category in self.categories.all():
            category.update_tutorial_count()
    
    def get_absolute_url(self):
        return reverse('tutorial_detail', kwargs={'slug': self.slug})
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    completed_tutorials = models.ManyToManyField(Tutorial, blank=True)
    progress_percentage = models.PositiveSmallIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'learning_path')
    
    def __str__(self):
        return f"{self.user.username}'s progress on {self.learning_path.title}"
    
    def update_progress(self):
        total_tutorials = self.learning_path.tutorials.count()
        if total_tutorials > 0:
            completed = self.completed_tutorials.count()
            self.progress_percentage = int((completed / total_tutorials) * 100)
        else:
            self.progress_percentage = 0
        self.save(update_fields=['progress_percentage'])

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    subscribed_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    gdpr_consent = models.BooleanField(default=True)
    
    def __str__(self):
        return self.email

# class Subscriber(models.Model):
#     email = models.EmailField(unique=True)
#     name = models.CharField(max_length=100, blank=True)
#     subscribed_date = models.DateTimeField(auto_now_add=True)
#     is_active = models.BooleanField(default=True)
    
#     def __str__(self):
#         return self.email
    