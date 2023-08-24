from rest_framework import serializers

class orderserializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()


class ordercancelserializer(serializers.Serializer):
    orderitemid = serializers.CharField()
    reason = serializers.CharField()


class ser_useraddress(serializers.Serializer):
    address_id = serializers.IntegerField()


class pr_seri(serializers.Serializer):
    product_id = serializers.IntegerField()

    