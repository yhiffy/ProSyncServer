from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.

class LoginView(APIView):

    def post(self, request, *args, **kwargs):
        print('Login successfully connected')

        #拿到email和password
        # email = request.data['email']
        # password = request.data['password']
        #检测是否有这个email，有就继续

        #通过email地址查到对应的password，然后作对比（需要引入bycrpt)
        #成功了，就生成JWT返回给前端，(要配置JWT setting)

        return Response('Login successful')

