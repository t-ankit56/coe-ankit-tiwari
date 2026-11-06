from rest_framework import serializers


class LoginInputSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()


class CurrentUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    email = serializers.EmailField()

    def get_name(self, user) -> str:
        return user.get_full_name()
