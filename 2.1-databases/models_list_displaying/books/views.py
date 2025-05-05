from django.shortcuts import render
from django.http import Http404
from .models import Book
from datetime import datetime, timedelta

def get_books_context(pub_date=None):
    if pub_date:
        try:
            pub_date_obj = datetime.strptime(pub_date, '%Y-%m-%d').date()
            books = Book.objects.filter(pub_date=pub_date_obj).order_by('pub_date')
            prev_date = pub_date_obj - timedelta(days=1)
            next_date = pub_date_obj + timedelta(days=1)
        except ValueError:
            raise Http404('Неверный формат даты. Используйте ГГГГ-ММ-ДД')
    else:
        books = Book.objects.all().order_by('pub_date')
        prev_date = None
        next_date = None
    return {
        'books': books,
        'pub_date': pub_date,
        'prev_date': prev_date,
        'next_date': next_date,
    }


def books_view(request):
    context = get_books_context()
    return render(request, 'books/books_list.html', context)

def books_by_date(request, pub_date):
    context = get_books_context(pub_date)
    return render(request, 'books/books_list.html', context)