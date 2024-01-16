from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True)

    def update_rating(self):
        #суммарный рейтинг каждой статьи автора умножается на 3
        art_rating = self.post_set.filter(art_new='A').aggregate(Sum('rating'))['rating__sum']*3
        if art_rating is None:
            art_rating = 0
        #суммарный рейтинг всех комментариев автора
        author_id = self.id
        comment_rating = Comment.objects.filter(post__author__id=author_id).aggregate(Sum('rating'))['rating__sum']
        if comment_rating is None:
            comment_rating = 0
        #суммарный рейтинг всех комментариев к статьям автора.
        total_article_comment_rating = Comment.objects.filter(post__author__id=author_id, post__art_new='A').aggregate(Sum('rating'))['rating__sum']
        if total_article_comment_rating is None:
            total_article_comment_rating = 0
        self.rating = art_rating + comment_rating + total_article_comment_rating
        self.save()
    #9.Вывести username и рейтинг лучшего пользователя (применяя сортировку и возвращая поля первого объекта).
    def who_best(self):
        best_author = Author.objects.annotate(total_rating=Sum('post__comment__rating')).order_by(
            '-total_rating').first()

        if best_author:
            print(f"Лучший автор: {best_author.user.username}")
            print(f"Рейтинг: {best_author.total_rating}")
        else:
            print("Нет авторов с комментариями.")

article = 'A'
news = 'N'

TYPE = [
    (article, 'Статья'),
    (news, 'Новость')
]
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

class Post(models.Model):
    article = 'A'
    news = 'N'
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    art_new = models.CharField(max_length=1,
                                choices=TYPE,
                                default=article)
    create_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)
    categories = models.ManyToManyField(Category, through='PostCategory', null=True)

    def like(self):
        self.rating +=1
        self.save()

    def dislike(self):
        self.rating -=1
        self.save()

    def preview(self):
        return self.text[:124] + "..."
    #10. Вывести дату добавления, username автора, рейтинг, заголовок и превью лучшей статьи, основываясь на лайках/дислайках к этой статье.
    def best(self):
        best_article = Post.objects.filter(art_new='A').annotate(total_rating=Sum('comment__rating')).order_by(
            '-total_rating').first()

        if best_article:
            print(f"Дата добавления: {best_article.create_date}")
            print(f"Username автора: {best_article.author.user.username}")
            print(f"Рейтинг автора: {best_article.author.rating}")
            print(f"Заголовок статьи: {best_article.title}")
            print(f"Превью статьи: {best_article.preview()}")  # Выводим первые 100 символов превью
        else:
            print("Нет статей для вывода.")
    #11.Вывести все комментарии (дата, пользователь, рейтинг, текст) к этой статье.
    def all_comments(self):
        article_id = self.id
        comments = Comment.objects.filter(post__id=article_id)

        if comments.exists():
            i = 0
            for comment in comments:
                i+=1
                print(f"Комментарий: {i}")
                print(f"Дата: {comment.create_date}")
                print(f"Пользователь: {comment.user.username}")
                print(f"Рейтинг: {comment.rating}")
                print(f"Текст: {comment.text}")
                print("----")
        else:
            print("Нет комментариев для данной статьи.")

class PostCategory(models.Model):
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating +=1
        self.save()

    def dislike(self):
        self.rating -=1
        self.save()

