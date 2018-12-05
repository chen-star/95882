import datetime
from haystack import indexes
from coolcars.models import *


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    username = indexes.CharField(model_attr='username')
    published_date = indexes.DateTimeField(model_attr='published_date')
    favorite = indexes.IntegerField(model_attr='favorite')

    def get_model(self):
        return Post

    # def index_queryset(self, using=None):
    #     return self.get_model().objects.all().order_by('-favorite').highlight()
