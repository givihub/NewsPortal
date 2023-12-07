from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, F


class Author(models.Model):
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        # Суммарный рейтинг каждой статьи автора умножается на 3
        posts_rating = self.post_set.aggregate(total_posts_rating=Sum(F('rating') * 3))['total_posts_rating'] or 0

        # Суммарный рейтинг всех комментариев автора
        own_comments_rating = self.comment_set.aggregate(total_own_comments_rating=Sum('rating'))['total_own_comments_rating'] or 0

        # Суммарный рейтинг всех комментариев к статьям автора
        comments_on_posts_rating = Comment.objects.filter(post__author=self).aggregate(total_comments_on_posts_rating=Sum('rating'))['total_comments_on_posts_rating'] or 0

        # Обновление рейтинга автора
        new_rating = posts_rating + own_comments_rating + comments_on_posts_rating
        self.rating = new_rating
        self.save()


class Category(models.Model):
    name = models.CharField(unique=True, max_length=20)


class Post(models.Model):
    ARTICLE_TYPE_CHOICE = [
        ('article', 'статья'),
        ('news', 'новость')
    ]
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    article_type = models.CharField(max_length=10, choices=ARTICLE_TYPE_CHOICE)
    time_post = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    text = models.TextField(max_length=1000)
    rating = models.IntegerField(default=0)
    category = models.ManyToManyField(Category, through='PostCategory')

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        if self.rating > 0:
            self.rating -= 1
            self.save()

    def preview(self):
        if len(self.text) > 124:
            return self.text[:124] + '...'  # Возвращает начало текста и добавляет многоточие в конце
        else:
            return self.text


class PostCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    time_comment = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        if self.rating > 0:
            self.rating -= 1
            self.save()
