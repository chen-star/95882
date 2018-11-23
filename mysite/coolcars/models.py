from django.db import models


# user info
class Info(models.Model):
    username = models.OneToOneField('auth.User', on_delete=models.CASCADE, primary_key=True)
    # username = models.ForeignKey('auth.User', on_delete=models.DO_NOTHING)
    age = models.IntegerField(null=True)
    bio = models.CharField(max_length=420, null=True)
    followers = models.ManyToManyField("Info", symmetrical=False)

    def __str__(self):
        return "{0}, {1}, {2}".format(self.username, self.age, self.bio)
