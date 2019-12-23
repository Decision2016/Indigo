from api.porn_detection import api
import re
import urllib.request
import base64
import json


def get_image_url(msg):
    ret = re.search("CQ:image", msg)
    if ret:
        res = re.findall(r"(?<=url=).*?(?=\?vuin)", msg)
        return res
    return None


def detection(msg):
    urls = get_image_url(msg)
    if not urls:
        return None
    for url in urls:
        resp = urllib.request.urlopen(url=url)
        base64code = str(base64.b64encode(resp.read()))
        porn_res = api.porn_detection(base64code[2:-1])
        if porn_res['PornResult'] and porn_res['PornResult']['Type'] in ['PORN', 'HOT']:
            return True
    return False
