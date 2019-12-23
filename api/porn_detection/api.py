from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tiia.v20190529 import tiia_client, models
from api.porn_detection import api_key
import json


def porn_detection(base64code):
    try:
        cred = credential.Credential(api_key.open_id, api_key.open_secret)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tiia.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = tiia_client.TiiaClient(cred, "ap-guangzhou", clientProfile)

        req = models.ImageModerationRequest()
        params = '{"ImageBase64":"' + str(base64code) + '","Scenes":["PORN"]}'
        req.from_json_string(params)

        resp = client.ImageModeration(req).to_json_string()
        resp = json.loads(resp)

    except TencentCloudSDKException as err:
        resp = None

    return resp