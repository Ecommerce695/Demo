from rest_framework import serializers

class PicupScheduleSerializer(serializers.Serializer):
    pickup_date = serializers.CharField(default='')
    