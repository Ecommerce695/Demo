from rest_framework import serializers

class CartSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    variant = serializers.IntegerField()

class CartQuantitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    variant=serializers.IntegerField()
    quantity = serializers.IntegerField()
