import csv
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from pagination import settings


def index(request):
    return redirect(reverse('bus_stations'))


def bus_stations(request):
    with open(settings.BUS_STATION_CSV, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        stations = []
        for row in reader:
            stations.append({
                'Name': row['Name'],
                'Street': row['Street'],
                'District': row['District']
            })
    
    page_number = int(request.GET.get('page', 1))
    pagi = Paginator(stations, 10)
    page = pagi.get_page(page_number)
    context = {
        'bus_stations': page.object_list,
        'page': page,
    }
    return render(request, 'stations/index.html', context)
