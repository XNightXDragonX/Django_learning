from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.viewsets import ModelViewSet
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from advertisements.models import Advertisement, Favorite
from advertisements.serializers import AdvertisementSerializer
from advertisements.filters import AdvertisementFilter


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.creator == request.user
    
    
class IsAdminOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.creator == request.user
        

class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений."""
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdvertisementFilter
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["create"]:
            return [IsAuthenticated()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminOrOwner()]
        return []
    
    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        ad = self.get_object()
        if ad.creator == request.user:
            return Response({'error': 'Нельзя добавлять свои объявления в избранное'}, status=400)
        if request.method == 'POST':
            Favorite.objects.get_or_create(user=request.user, advertisement=ad)
            return Response({'status': 'added'})
        else:
            Favorite.objects.filter(user=request.user, advertisement=ad).delete()
            return Response({'status': 'removed'})
        
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.exclude(status='DRAFT')
        elif not self.request.user.is_staff:
            return queryset.exclude(
                Q(status='DRAFT') & ~Q(creator=self.request.user)
            )
        return queryset

        
            