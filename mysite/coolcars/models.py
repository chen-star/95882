from django.db import models
from taggit.managers import TaggableManager

# user info
from django.utils import timezone


class Info(models.Model):
    username = models.OneToOneField('auth.User', on_delete=models.CASCADE, primary_key=True)
    # username = models.ForeignKey('auth.User', on_delete=models.DO_NOTHING)
    age = models.IntegerField(null=True)
    bio = models.CharField(max_length=420, null=True)
    followers = models.ManyToManyField("Info", symmetrical=False)

    def __str__(self):
        return "{0}, {1}, {2}".format(self.username, self.age, self.bio)


# post
class Post(models.Model):
    username = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.CharField(max_length=100)
    published_date = models.DateTimeField(default=timezone.now)
    favorite = models.IntegerField(default=0)
    tags = TaggableManager()

    def __str__(self):
        return "{0}, {1}, {2}, {3}, {4}, pk: {5}".format(self.username, self.title, self.content, self.published_date,
                                                         self.favorite, self.pk)


# comments
class Comment(models.Model):
    username = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    content = models.CharField(max_length=100)
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{0}, {1}, {2}, {3}".format(self.username, self.post, self.content, self.time)


# notifications
class Notification(models.Model):
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=300)
    time = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    def __str__(self):
        return "{0}, {1}, {2}, {3}".format(self.title, self.content, self.time, self.read)


# votes
class Vote(models.Model):
    username = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    no_vote = models.IntegerField(default=0)

    def __str__(self):
        return "{0}, {1}".format(self.username, self.no_vote)


# NL search
class Search(models.Model):
    username = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    searches = TaggableManager()

    def __str__(self):
        return "{0}".format(self.username)
