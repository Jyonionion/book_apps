from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView,DetailView,CreateView,DeleteView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book,Review
from django.core.exceptions import PermissionDenied
from django.db.models import Avg
from .forms import SearchForm
from django.core.paginator import Paginator
from .consts import ITEM_PER_PAGE


class ListBookView(LoginRequiredMixin, ListView):
    template_name = 'book/book_list.html'
    model = Book

class DetailBookView(DetailView):
    template_name = 'book/book_detail.html'
    model = Book

class CreateBookView(LoginRequiredMixin, CreateView):
    template_name = 'book/book_create.html'
    model = Book
    fields = ('title','text','category','thumbnail')
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.user = self.request.user

        return super().form_valid(form)
    
class DeleteBookView(LoginRequiredMixin, DeleteView):
    template_name = 'book/book_confirm_delete.html'
    model = Book
    success_url = reverse_lazy('index')
    def get_object(self, queryset=None):
        obj = super().get_object()

        if obj.user != self.request.user:
            raise PermissionDenied("この本を削除する権限がありません")
        return obj

class UpdateBookView(LoginRequiredMixin, UpdateView):
    template_name = 'book/book_update.html'
    model = Book
    fields = ('title','text','category','thumbnail')
    success_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if obj.user != self.request.user:
            raise PermissionDenied("この本を更新する権限がありません")
        return obj

    def get_success_url(self):
        return reverse('detail-book', kwargs={'pk': self.object.id})

def index_view(request):
    sort_option = request.GET.get('sort', 'newest')

    search_results = Book.objects.all()

    if sort_option == 'rating':
        search_results = search_results.annotate(avg_ranking=Avg('review__rate')).order_by('-avg_ranking')
    elif sort_option == 'newest':
        search_results = search_results.order_by('-id')
    elif sort_option == 'oldest':
        search_results = search_results.order_by('id')

    searchForm = SearchForm(request.GET)
    if searchForm.is_valid():
        keyword = searchForm.cleaned_data['keyword']
        search_results = search_results.filter(title__icontains=keyword)


    ranking_list = Book.objects.annotate(avg_ranking=Avg('review__rate')).order_by('-avg_ranking')[:5]

    paginator = Paginator(ranking_list, ITEM_PER_PAGE)
    page_number = request.GET.get('page',1)
    page_obj = paginator.page(page_number)


    context = {
        'object_list': search_results,
        'ranking_list': ranking_list,
        'searchForm': searchForm,
        'sort_option': sort_option, 
        'page_obj':page_obj
    }

    return render(
        request,
        'book/index.html',
        context,
        )

class CreateReviewView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ('book', 'title', 'text', 'rate')
    template_name = 'book/review_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = Book.objects.get(pk=self.kwargs['book_id'])
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('detail-book', kwargs={'pk': self.object.book.id})