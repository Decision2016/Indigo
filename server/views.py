from utils.baseclasses import BaseAPIView
from account.decorators import cq_permission_required
from account.models import User, Command, Group, Person
from account.serializer import PersonSerializer
from api.porn_detection import image_api
import requests
import re
import json


def get_person(command_string, user, **kwargs):
    string_array = command_string.split(' ')
    try:
        command = user.command.get(patternString=string_array[2])
    except Command.DoesNotExist:
        return "指令错误"

    try:
        group = command.group.get(groupId=kwargs['groupId'])
    except Command.DoesNotExist:
        group = Group.objects.create(groupId=kwargs['groupId'], belong=command)
        group.save()

    try:
        person = group.person.get(userId=string_array[1])
    except Person.DoesNotExist:
        person_data = get_person_information(kwargs['groupId'], string_array[1], user.cq_url)
        person = Person.objects.create(userId=string_array[1], nickname=person_data['data']['nickname'], belong=group)

    return person


def command_analysis(command_string, user, **kwargs):
    string_array = command_string.split(' ')

    if string_array[0] == '/add1':
        # user_id:对应的用户信息，而非QQ账号
        if kwargs['user_id'] != user.superUserId:
            return "你add你🐎呢"
        if len(string_array) == 6 and not Command.objects.filter(patternString=string_array[1]).exists():
            command = Command.objects.create(patternString=string_array[1], outputCommand=string_array[2],
                                             maxLength=int(string_array[3]), belong=user,
                                             nickname=string_array[4], openRe=bool(int(string_array[5])))
            command.save()
            return " 添加成功"
        else:
            return "指令格式错误或指令已存在"
    elif string_array[0] == '/set':
        if kwargs['user_id'] != user.superUserId:
            return "你set你🐎呢"
        if len(string_array) == 4:
            person = get_person(command_string, user, **kwargs)
            person.count = int(string_array[3])
            person.save()
            return "修改成功"
        else:
            return "指令格式错误"
    elif string_array[0] == '/increase':
        if kwargs['user_id'] != user.superUserId:
            return "你increase你🐎呢"
        if len(string_array) == 4:
            person = get_person(command_string, user, **kwargs)
            person.count += int(string_array[3])
            person.save()
            return "添加成功"
        else:
            return "指令格式错误"
    elif string_array[0] == '/switch':
        if kwargs['user_id'] != user.superUserId:
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
        group = command.group.get(groupId=group_id)
    except Group.DoesNotExist:
        group = Group.objects.create(belong=command, groupId=group_id)

    try:
        person = group.person.get(userId=user_id)
    except Person.DoesNotExist:
        person = Person.objects.create(userId=user_id, belong=group, nickname=nickname)

    person.nickname = nickname
    person.count = person.count + 1
    if person.count % 1000 == 0:
        return True
    group.save()
    person.save()
    return False


def rank_get(message, group_id, user):
    commands = user.command.all()
    for command in commands:
        if message == command.outputCommand:
            try:
                group = command.group.get(groupId=group_id)
            except Group.DoesNotExist:
                group = Group.objects.create(belong=command, groupId=group_id)

            persons = group.person.filter(inGroup=True)
            persons.order_by('count')
            length = min(len(persons), command.maxLength)
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
    command_res = command_analysis(message, user, user_id=user_id, groupId=group_id)
    get_person_information(group_id, message, user.cqUrl)
    if command_res:
        group_message(command_res, data['group_id'], user.cqUrl)
    else:
        rank_dic, nickname = rank_get(message, int(group_id), user)
        if rank_dic:
            group_rank_message(rank_dic, group_id, nickname, user.cqUrl)
        else:
            command_count(message, group_id, user_id, data['sender']['nickname'], user)
            ret = re.search("CQ:image", message)
            if user.pornSwitch and ret and image_api.detection(message):
                group_message("gkdgkd!!!!", group_id, user.cqUrl)


def set_person_status(person, status):
    person.in_group = status
    person.save()


def handle_group(data):
    notice_type = data['notice_type']
    user_id = data['user_id']
    group_id = data['group_id']
    groups = Group.objects.filter(groupId=group_id)
    status = notice_type == 'group_increase'
    for group in groups:
        person = group.person.get(userId=user_id)
        set_person_status(person, status)


def command_count(message, group_id, user_id, nickname, user):
    commands = user.command.all()
    for command in commands:
        if command.openRe and re.findall(command.patternString, message):
            if count_add(group_id, command, nickname, user_id):
                return True
        elif (not command.openRe) and message == command.patternString:
            if count_add(group_id, command, nickname, user_id):
                return True
    return False


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
