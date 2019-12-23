from rest_framework.views import APIView
from rest_framework.response import Response
from account.decorators import cq_permission_required
from account.models import User, Command, Group, Person
from account.serializer import PersonSerializer
from api.porn_detection import image_api
import requests
import re
import json


def command_analysis(command_string, user, **kwargs):
    string_array = command_string.split(' ')

    if string_array[0] == '/add':
        if kwargs['user_id'] != user.super_user_id:
            return "你add你🐎呢"
        if len(string_array) == 6:
            command = Command.objects.create(pattern_string=string_array[1], output_command=string_array[2],
                                             max_length=int(string_array[3]), belong=user,
                                             nickname=string_array[4], open_re=bool(int(string_array[5])))
            command.save()
            return " 添加成功"
        else:
            return "指令格式错误"
    elif string_array[0] == '/set':
        if kwargs['user_id'] != user.super_user_id:
            return "你set你🐎呢"
        if len(string_array) == 4:
            try:
                command = user.commands.get(pattern_string=string_array[2])
            except Command.DoesNotExist:
                return "指令错误"

            try:
                group = command.group.get(group_id=kwargs['group_id'])
            except Command.DoesNotExist:
                group = Group.objects.create(group_id=kwargs['group_id'], belong=command)
                group.save()

            try:
                person = group.person.get(user_id=string_array[1])
            except Person.DoesNotExist:
                person_data = get_person_information(kwargs['group_id'], string_array[1], user.cq_url)
                person = Person.objects.create(user_id=string_array[1], nickname=person_data['data']['nickname'],
                                               group=group)
            person.count = int(string_array[3])
            person.save()
            return "修改成功"
        else:
            return "指令格式错误"
    elif string_array[0] == '/increase':
        if kwargs['user_id'] != user.super_user_id:
            return "你increase你🐎呢"
        if len(string_array) == 4:
            try:
                command = user.commands.get(pattern_string=string_array[2])
            except Command.DoesNotExist:
                return "指令错误"

            try:
                group = command.group.get(group_id=kwargs['group_id'])
            except Command.DoesNotExist:
                group = Group.objects.create(group_id=kwargs['group_id'], belong=command)
                group.save()

            try:
                person = group.person.get(user_id=string_array[1])
            except Person.DoesNotExist:
                person_data = get_person_information(kwargs['group_id'], string_array[1], user.cq_url)
                person = Person.objects.create(user_id=string_array[1], nickname=person_data['data']['nickname'], group=group)
            person.count = person.count + int(string_array[3])
            person.save()
            return "添加成功"
        else:
            return "指令格式错误"
    elif string_array[0] == '/switch':
        if kwargs['user_id'] != user.super_user_id:
            return "你close你🐎呢"
        if len(string_array) == 1:
            user.porn_switch = not user.porn_switch
            user.save()
            return "接口状态已调整:" + ('ON' if user.porn_switch else 'OFF')
        else:
            return "指令格式错误"
    return None


def get_person_information(group_id, user_id, cq_url):
    url = cq_url + '/get_group_member_info'
    data = {
        'group_id': group_id,
        'user_id': user_id,
        'no_cache': 'true'
    }
    request = requests.post(url, data)
    return json.loads(request.text)


def count_add(group_id, command, nickname, user_id):
    try:
        group = command.group.get(group_id=group_id)
    except Group.DoesNotExist:
        group = Group.objects.create(belong=command, group_id=group_id)

    try:
        person = group.person.get(user_id=user_id)
    except Person.DoesNotExist:
        person = Person.objects.create(user_id=user_id, group=group, nickname=nickname)

    person.nickname = nickname
    person.count = person.count + 1
    group.save()
    person.save()


def rank_get(message, group_id, user):
    commands = user.commands.all()
    for command in commands:
        if message == command.output_command:
            try:
                group = command.group.get(group_id=group_id)
            except Group.DoesNotExist:
                group = Group.objects.create(belong=command, group_id=group_id)

            persons = group.person.filter(in_group=True)
            persons.order_by('count')
            length = min(len(persons), command.max_length)
            res_data = PersonSerializer(persons[:length], many=True)
            return res_data.data, command.nickname
    return None, None


def group_message(message, group_id, cq_url):
    url = cq_url + "/send_group_msg"
    data_dic = {
         'group_id': group_id,
         'message': message,
    }
    request = requests.post(url=url, data=data_dic)


def group_rank_message(rank_dic, group_id, nickname, cq_url):
    length = len(rank_dic)
    msg = "你群前" + str(length) + "名" + nickname + "："
    for item in rank_dic:
        msg += "\n" + str(item['nickname']) + " " + str(item['count'])
    group_message(msg, group_id, cq_url)


def handle_message(data, user):
    message = data['message']
    user_id = data['user_id']
    group_id = data['group_id']
    command_res = command_analysis(message, user, user_id=user_id, group_id=group_id)
    get_person_information(group_id, message, user.cq_url)
    if command_res:
        group_message(command_res, data['group_id'], user.cq_url)
    else:
        rank_dic, nickname = rank_get(message, int(group_id), user)
        if rank_dic:
            group_rank_message(rank_dic, group_id, nickname, user.cq_url)
        else:
            command_count(message, group_id, user_id, data['sender']['nickname'], user)
            ret = re.search("CQ:image", message)
            if user.porn_switch and ret and image_api.detection(message):
                group_message("gkdgkd!!!!", group_id, user.cq_url)


def set_person_status(person, status):
    person.in_group = status
    person.save()


def handle_group(data):
    notice_type = data['notice_type']
    user_id = data['user_id']
    group_id = data['group_id']
    groups = Group.objects.filter(group_id=group_id)
    status = notice_type == 'group_increase'
    for group in groups:
        person = group.person.get(user_id=user_id)
        set_person_status(person, status)


def command_count(message, group_id, user_id, nickname, user):
    commands = user.commands.all()
    for command in commands:
        if command.openRe and re.match(r'message', command.pattern_string):
            count_add(group_id, command, nickname, user_id)
            return True
        elif (not command.openRe) and message == command.pattern_string:
            count_add(group_id, command, nickname, user_id)
            return True
    return False


class BaseAPIView(APIView):
    @staticmethod
    def success(msg):
        res = {'errMsg': 'success', 'Data': msg}
        return Response(res)


class ServerAPI(BaseAPIView):
    @cq_permission_required
    def post(self, request):
        data = request.data
        user = User.objects.get(username=request.query_params['username'])
        if data['post_type'] == 'message' and data['message_type'] == 'group':
            handle_message(data, user)
        elif data['post_type'] == 'notice':
            handle_group(data, user)
        return self.success("Success")
