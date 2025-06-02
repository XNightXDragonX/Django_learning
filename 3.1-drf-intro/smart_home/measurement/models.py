from django.db import models

class Sensor(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    description = models.CharField(max_length=200, blank=True, verbose_name='Описание')
    
    def __str__(self):
        return self.name
    
    
class Measurement(models.Model):
    temperature = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Температура')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время измерения')
    image = models.ImageField(null=True, blank=True, verbose_name='Изображение')
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='measurements', verbose_name='Датчик')
    
    def __str__(self):
        return f'{self.sensor.name}: {self.temperature}°C'