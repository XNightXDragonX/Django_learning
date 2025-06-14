from django.contrib.auth.models import User
from rest_framework import serializers

from advertisements.models import Advertisement, AdvertisementStatusChoices, Favorite


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""
    creator = UserSerializer(
        read_only=True,
    )
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', 'is_favorite')

    def create(self, validated_data):
        """Метод для создания"""
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""
        user = self.context['request'].user
        current_status = data.get('status')
        
        if current_status == AdvertisementStatusChoices.OPEN or (current_status is None or self.instance is None):
            open_ads_count = Advertisement.objects.filter(
                creator=user,
                status=AdvertisementStatusChoices.OPEN
            ).exclude(id=self.instance.id if self.instance else None).count()
            if open_ads_count > 10:
                raise serializers.ValidationError(
                    'У вас не может быть больше 10 открытых объявлений'
                )
                
        if self.instance and self.instance.status == AdvertisementStatusChoices.DRAFT and current_status ==AdvertisementStatusChoices.OPEN:
            open_ads_count = Advertisement.objects.filter(
                creator=user,
                status=AdvertisementStatusChoices.OPEN
            ).count()
            if open_ads_count > 10:
                raise serializers.ValidationError(
                    'Невозможно опубликовать черновик: достигнут лимит в 10 открытых объявленений'
                )
                
        return data
    
    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, advertisement=obj).exists()
        return False
        