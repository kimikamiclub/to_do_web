from django.template.loader import render_to_string

from blog.models import Category


def get_categories(request):
    categories = Category.objects.all()
    return render_to_string('blog/categories.html', {
        'categories': categories,
    })


def standart(request):
    context = dict()
    context['categories_html'] = get_categories(request)
    return context
