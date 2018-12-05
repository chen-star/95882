from django.shortcuts import render
from haystack.views import SearchView
from coolcars.models import Post
from .forms import *


# class MySearchView(SearchView):
#     def extra_context(self):
#         context = super(MySearchView, self).extra_context()
#         side_list = Post.objects.all().order_by('-favorite')[:8]
#         context['side_list'] = side_list
#         context['form'] = MySearchForm()
#         return context

def post_search(request):
    form = MySearchForm()
    cd = None
    results = None
    total_results = None
    if 'q' in request.GET:
        form = MySearchForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            print(SearchQuerySet().models(Post).filter(content=cd['q']).order_by('-favorite').load_all())
            results = SearchQuerySet().models(Post).filter(content=cd['q']).order_by('-favorite').load_all()
            total_results = results.count()
    return render(request, 'search/search.html', {'form': form,
                                                  'cd': cd,
                                                  'results': results,
                                                  'total_results': total_results})

