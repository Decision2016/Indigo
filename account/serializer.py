from rest_framework import serializers
from account.models import User, Person, Command, Group


class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    openSecret = serializers.CharField()
    superUserId = serializers.IntegerField()
    cqUrl = serializers.CharField()

    class Meta:
        model = User
        fields = '__all__'


class PersonSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    userId = serializers.CharField()
    nickname = serializers.CharField()
    inGroup = serializers.BooleanField()
    count = serializers.IntegerField()

    class Meta:
        model = Person
        fields = '__all__'


class CommandSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    patternString = serializers.CharField()
    outputCommand = serializers.CharField()
    maxLength = serializers.CharField()
    openRe = serializers.BooleanField()
    nickname = serializers.CharField()

    class Meta:
        model = Command
        fields = '__all__'


class OnlyCommandSerializer(serializers.Serializer):
    commandString = serializers.CharField()

    class Meta:
        model = Command


class GroupSerializer(serializers.Serializer):
    groupId = serializers.IntegerField()

    class Meta:
        model = Group
