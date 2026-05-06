from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Article, Category


@login_required
def article_list(request):
    articles = Article.objects.filter(is_published=True).select_related('category')
    categories = Category.objects.all()
    
    category_filter = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    if category_filter:
        articles = articles.filter(category_id=category_filter)
    
    if search:
        articles = articles.filter(
            Q(title__icontains=search) | Q(content__icontains=search)
        )
    
    return render(request, 'knowledgebase/list.html', {
        'articles': articles,
        'categories': categories,
        'category_filter': category_filter,
        'search': search,
    })


@login_required
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk, is_published=True)
    article.views_count += 1
    article.save(update_fields=['views_count'])
    
    related = Article.objects.filter(
        category=article.category, is_published=True
    ).exclude(pk=pk)[:5]
    
    return render(request, 'knowledgebase/detail.html', {
        'article': article,
        'related': related,
    })
