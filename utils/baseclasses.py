from rest_framework.views import APIView
from rest_framework.response import Response


class BaseAPIView(APIView):
    @staticmethod
    def error(msg):
        res = {'errMsg': 'error', 'data': msg}
        return Response(res)

    @staticmethod
    def success(msg):
        res = {'errMsg': 'success', 'data': msg}
        return Response(res)