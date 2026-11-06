from rest_framework import serializers


class LoginInputSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()


class CurrentUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    email = serializers.EmailField()
    is_approver = serializers.SerializerMethodField()
    on_probation = serializers.SerializerMethodField()
    approver = serializers.SerializerMethodField()

    def get_name(self, user) -> str:
        return user.get_full_name()

    def get_is_approver(self, user) -> bool:
        return user.profile.is_approver

    def get_on_probation(self, user) -> bool:
        return user.profile.on_probation

    def get_approver(self, user) -> dict | None:
        approver = user.profile.approver
        return {"name": approver.get_full_name()} if approver else None
