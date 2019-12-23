from rest_framework.views import APIView
from .serializer import UserSerializer, PersonSerializer, CommandSerializer, CommandGetSerializer, GroupSerializer, \
    PersonSerializer
from .models import User, Command, Group, Person
from rest_framework.response import Response
from .decorators import login_required, api_permission_required, get_permission_required
from django.contrib import auth
import uuid


class BaseAPIView(APIView):
    @staticmethod
    def error(msg):
        res = {'errMsg': 'error', 'data': msg}
        return Response(res)

    @staticmethod
    def success(msg):
        res = {'errMsg': 'success', 'data': msg}
        return Response(res)


class UserRegAPI(BaseAPIView):
    def post(self, request):
        data = request.data
        open_secret = uuid.uuid1()
        username = data["username"]
        password = data["password"]
        super_user_id = data["super_user_id"]
        if User.objects.filter(username=username).exists():
            return self.error("username is existed")
        user = User.objects.create(username=username, open_secret=open_secret, super_user_id=super_user_id)
        user.set_password(password)
        user.save()
        return self.success("Register Success")


class UserLoginAPI(BaseAPIView):
    def post(self, request):
        data = request.data
        user = auth.authenticate(username=data["username"], password=data["password"])
        if user:
            if User.check_password(user, data["password"]):
                auth.login(request, user)
                return self.success("Successful")
            else:
                return self.error("Username or Password is incorrect")
        else:
            return self.error("User is not existed")


class UserLoginOutAPI(BaseAPIView):
    def post(self, request):
        auth.logout(request)
        return self.success('Logout Successful')


class EditCountAPI(BaseAPIView):
    @login_required
    def put(self, request):
        data = request.data
        user = request.user
        pattern_string = data['command']
        group_id = data['group']
        user_id = data['id']
        count = data['count']
        command = user.commands.get(pattern_string=pattern_string)
        group = command.group.get(group_id=group_id)
        person = group.person.get(number=user_id)
        user_info = get_person_information(group_id, user_id, user.cq_url)
        person.count = count
        person.nickname = user_info['data']['nickname']
        person.save()
        return self.success('Successful')

    @login_required
    def post(self, request):
        data = request.data
        user = request.user
        pattern_string = data['command']
        group_id = data['group']
        user_id = data['id']
        count = data['count']
        command = user.commands.get(pattern_string=pattern_string)
        group = command.group.get(group_id=group_id)
        user_info = get_person_information(group_id, user_id, user.cq_url)
        person = Person.objects.create(number=user_id, nickname=user_info['data']['nickname'], count=count, Group=group)
        person.save()
        return self.success('Successful')


class CheckUsernameExistAPI(BaseAPIView):
    def post(self, request):
        username = request.data['username']
        if User.objects.filter(username=username).exists():
            return self.error({'user': True})
        else:
            return self.success({'user': False})


class ProfileAPI(BaseAPIView):
    @login_required
    def get(self, request):
        user = request.user
        return self.success(UserSerializer(user).data)

    @login_required
    def put(self, request):
        data = request.data
        user = request.user
        user.super_number = data["super_number"]
        user.cq_url = data["cq_url"]
        user.save()
        return self.success("Edit Successful")


class CommandAPI(BaseAPIView):
    @login_required
    def get(self, request):
        user = request.user
        commands = user.commands.all()
        page = int(request.GET.get("page"))
        st = (page - 1) * 10
        ed = page * 10
        ed = min(len(commands), ed)
        if st > len(commands):
            return self.error("None Data")
        if request.GET.get('flag') == 'false':
            return self.success(CommandSerializer(commands[st: ed], many=True).data)
        else:
            return self.success(CommandGetSerializer(commands, many=True).data)


class CommandTotalGetAPI(BaseAPIView):
    @login_required
    def get(self, request):
        user = request.user
        command_num = user.commands.count()
        if command_num % 10 == 0:
            command_num = command_num // 10
        else:
            command_num = command_num // 10 + 1
        return self.success({'total_num': command_num})


class GroupAPI(BaseAPIView):
    @login_required
    def get(self, request):
        user = request.user
        pattern_string = request.GET.get('command')
        command = user.commands.get(pattern_string=pattern_string)
        groups = command.group.all()
        return self.success(GroupSerializer(groups, many=True).data)


class UserGetAPI(BaseAPIView):
    @login_required
    def get(self, request):
        group_id = request.GET.get('group')
        pattern_string = request.GET.get('command')
        user = request.user
        command = user.commands.get(pattern_string=pattern_string)
        group = command.group.get(group_id=group_id)
        persons = group.person.all()
        return self.success(PersonSerializer(persons, many=True).data)
