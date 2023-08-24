from rest_framework import serializers

class CartSerializer(serializers.Serializer):
    id = serializers.IntegerField()

class CartQuantitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    quantity = serializers.IntegerField()
