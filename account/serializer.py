from rest_framework import serializers
from account.models import User, Person, Command, Group


class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    open_secret = serializers.CharField()
    super_user_id = serializers.IntegerField()
    cq_url = serializers.CharField()

    class Meta:
        model = User
        fields = '__all__'


class PersonSerializer(serializers.Serializer):
    number = serializers.CharField()
    nickName = serializers.CharField()
    in_group = serializers.BooleanField()
    count = serializers.IntegerField()

    class Meta:
        model = Person
        fields = '__all__'


class CommandSerializer(serializers.Serializer):
    pattern_string = serializers.CharField()
    output_command = serializers.CharField()
    max_length = serializers.CharField()
    open_re = serializers.BooleanField()
    nickname = serializers.CharField()

    class Meta:
        model = Command
        fields = '__all__'


class OnlyCommandSerializer(serializers.Serializer):
    commandString = serializers.CharField()

    class Meta:
        model = Command


class GroupSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()

    class Meta:
        model = Group
