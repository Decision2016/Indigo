from utils.baseclasses import BaseAPIView
from .serializer import UserSerializer, PersonSerializer, CommandSerializer, GroupSerializer
from .models import User, Person, Command
from .decorators import login_required
from django.contrib import auth
from server.views import get_person_information
import uuid


class UserRegAPI(BaseAPIView):
    def post(self, request):
        data = request.data
        open_secret = uuid.uuid1()
        username = data["username"]
        password = data["password"]
        super_user_id = data["superUserId"]
        if User.objects.filter(username=username).exists():
            return self.error("username is existed")
        user = User.objects.create(username=username, openSecret=open_secret, superUserId=super_user_id)
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
        user.superUserId = data["superUserId"]
        user.cqUrl = data["cqUrl"]
        user.save()
        return self.success("Edit Successful")


class CommandAPI(BaseAPIView):
    @login_required
    def get(self, request):
        user = request.user
        commands = user.command.all()
        page = int(request.GET.get("page"))
        st = (page - 1) * 10
        ed = page * 10
        ed = min(len(commands), ed)
        if st > len(commands):
            return self.error("None Data")
        if request.GET.get('flag') == 'false':
            return self.success(CommandSerializer(commands[st: ed], many=True).data)
        else:
            return self.success(CommandSerializer(commands, many=True).data)

    @login_required
    def delete(self, request):
        id = request.GET.get('id')
        try:
            command = Command.objects.get(id=id)
        except Command.DoesNotExist:
             return self.error('command is not existed')
        command.delete()
        return self.success('Successful')


class CommandTotalGetAPI(BaseAPIView):
    @login_required
    def get(self, request):
        user = request.user
        command_num = user.command.count()
        if command_num % 10 == 0:
            command_num = command_num // 10
        else:
            command_num = command_num // 10 + 1
        return self.success({'totalNum': command_num})


class GroupAPI(BaseAPIView):
    @login_required
    def get(self, request):
        user = request.user
        pattern_string = request.GET.get('command')
        command = user.command.get(patternString=pattern_string)
        groups = command.group.all()
        return self.success(GroupSerializer(groups, many=True).data)


class PersonAPI(BaseAPIView):
    @login_required
    def get(self, request):
        group_id = request.GET.get('groupId')
        pattern_string = request.GET.get('command')
        user = request.user
        command = user.command.get(patternString=pattern_string)
        group = command.group.get(groupId=group_id)
        persons = group.person.all()
        return self.success(PersonSerializer(persons, many=True).data)

    @login_required
    def put(self, request):
        data = request.data
        user = request.user
        group_id = data['groupId']
        count = data['count']
        person = Person.objects.get(id=data['id'])
        user_info = get_person_information(group_id, person.userId,  user.cqUrl)
        person.count = count
        person.nickname = user_info['data']['nickname']
        person.save()
        return self.success('Successful')

    @login_required
    def post(self, request):
        data = request.data
        user = request.user
        pattern_string = data['command']
        group_id = data['groupId']
        user_id = data['userId']
        count = data['count']
        command = user.command.get(patternString=pattern_string)
        group = command.group.get(groupId=group_id)
        user_info = get_person_information(group_id, user_id, user.cqUrl)
        if group.person.filter(userId=user_id).exists():
            return self.error("member is existed")
        else:
            person = Person.objects.create(userId=user_id, nickname=user_info['data']['nickname'],
                                           count=count, belong=group)
            person.save()
        return self.success('Successful')

    @login_required
    def delete(self, request):
        id = request.GET.get('id')
        try:
            person = Person.objects.get(id=id)
        except Person.DoesNotExist:
            return self.error('Person is not existed')
        person.delete()
        return self.success('Successful')
