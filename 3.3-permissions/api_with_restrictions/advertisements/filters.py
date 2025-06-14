from django_filters import rest_framework as filters
from django_filters.filters import DateFromToRangeFilter
from advertisements.models import Advertisement


class AdvertisementFilter(filters.FilterSet):
    created_at = DateFromToRangeFilter()
    status = filters.CharFilter()
    creator = filters.NumberFilter()
    
    class Meta:
        model = Advertisement
        fields = ['created_at', 'status', 'creator']
        
    is_favorite = filters.BooleanFilter(method='filter_is_favorite')
    
    def filter_is_favorite(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset