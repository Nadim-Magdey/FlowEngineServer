from posixpath import isabs
import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.authtoken.models import Token
from telebot import types
from core.api.permission import IsValidClientRequest
from core.api.utils import generate_token, verify_token
from ..models import AllowedTelgramUsers, Service, FixedFlow, OptionalFlow, FlowConstraint, UserLogs, Notifications, UserProxy, TelegramAuthSession
from ..Encryptor.Algorithms import CybersourceFlexV2Encryptor, APGMastercardEncryptor 
from rest_framework.permissions import AllowAny
import telebot
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import traceback
import datetime
from django.utils import timezone

class ServiceInputsView(APIView):
    permission_classes = [IsAuthenticated, IsValidClientRequest]
    
    def get(self, request):
        services = Service.objects.filter(users=request.user)
        
        return Response({
            "services": [
                {
                    "id": s.id,
                    "name": s.name,
                    "inputs": s.inputs
                }
                for s in services
            ]
        })
    
class ServiceFlowsView(APIView):
    permission_classes = [IsAuthenticated, IsValidClientRequest]
    
    def get(self, request):
        """
        returns all services and optional flows, and user optional flows
        and fixed_flows
        """
        
        services = (
            request.user.services
            .prefetch_related("optional_flows")
        )
        
        services_data = []
        for s in services:
            services_data.append({
                "id": s.id,
                "name": s.name,
                "inputs": s.inputs.get("inputs", []),
                "flows": s.flows,
                "optional_flows": [
                    {
                        "id": of.id,
                        "name": of.name,
                        "flows": of.flows,
                        "order": of.order,
                    }
                    for of in s.optional_flows.filter(is_active=True)
                ]
            })
            
        user_optional_flows = [
            {
                "id": of.id,
                "name": of.name,
                "flows": of.flows,
                "order": of.order,
            }
            for of in request.user.optional_flows.filter(is_active=True)
        ]

        user_fixed_flows = [
            {
                "id": of.id,
                "name": of.name,
                "flows": of.flows,
                "order": of.order,
                "notify_condition": of.notify_condition,
                "notify_variables": of.notify_variables,
                "success_value": of.success_value
            }
            for of in request.user.fixed_flows.filter(is_active=True)
        ]

        flow_constraints = [
            {
                "left_flow": c.left_flow.name,
                "right_flow": c.right_flow.name
            }
            for c in FlowConstraint.objects.all()
        ]
        
        return Response({
            "services": services_data,
            "user_optional_flows": user_optional_flows,
            "user_fixed_flows": user_fixed_flows,
            "flow_constraints": flow_constraints
        })

class CybersourceFlexV2EncryptView(APIView):
    permission_classes = [IsAuthenticated, IsValidClientRequest]
    
    def post(self, request):
        try:
            card_data = request.data.get("cardData")
            public_key_data = request.data.get("publicKey")
            extra_data = request.data.get("extra", {})
            
            encryptor = CybersourceFlexV2Encryptor(
                card_data=card_data,
                public_key_data=public_key_data,
                extra_data=extra_data
            )
            result = encryptor.encrypt()
            return Response({"status": "success", "result": result}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class APGMastercardEncryptView(APIView):
    permission_classes = [IsAuthenticated, IsValidClientRequest] 

    def post(self, request):
        try:
            print(f"reieved data {request.data}" )

            card_data = request.data.get("cardData")
            public_key_data = request.data.get("publicKey")
            extra_data = request.data.get("extra", {})
            encryptor = APGMastercardEncryptor(
                card_data=card_data,
                public_key_data=public_key_data,
                extra_data=extra_data
            )
            
            result = encryptor.encrypt()
            return Response({"status": "success", "result": result}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"error happend inside APGMastercardEncryptView view{e}")
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class CheckAuth(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        try:
            token = request.data.get("TOKEN")

            token = Token.objects.filter(key = token).first()
            isAuth = True if token else False
            
            result = {
                "isAuth": isAuth
            }
            return Response({"status": "success", "result": result}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GetServices(APIView):
    permission_classes = [IsAuthenticated, IsValidClientRequest] 
    def post(self, request):
        try:
            
            basic_services  = request.user.services.all()
            data = [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,            
                }
            for s in basic_services
            ]
            #optional flows that related to each service
            optional_flows = []
            for s in basic_services:
                optional_flows += s.optional_flows.filter(is_active=True)
            
            for of in optional_flows:
                data.append({
                "id": of.id,
                "name": of.name                })

            result = {
                "services": data
            }

            return Response({"status": "success", "result": result}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class FlowConstraintsView(APIView):
    permission_classes = [IsAuthenticated, IsValidClientRequest]

    def get(self, request):
        user = request.user

        # Get all flows related to the user
        user_services = list(Service.objects.filter(users=user))
        user_optional_flows = list(OptionalFlow.objects.filter(users=user))
        fixed_flows = list(FixedFlow.objects.filter(users=user))
        all_flows = user_services + user_optional_flows + fixed_flows
        
        # Fetch all constraints
        all_constraints = FlowConstraint.objects.all()
        
        # Filter in Python
        user_constraints = [
            c for c in all_constraints
            if c.left_flow in all_flows or c.right_flow in all_flows
        ]

        data = [
            {
                "id": c.id,
                "left_flow": getattr(c.left_flow, "name", str(c.left_flow)),
                "right_flow": getattr(c.right_flow, "name", str(c.right_flow)),
            }
            for c in user_constraints
        ]

        return Response({
            "status": "success",
            "constraints": data
        })


class UserLogsView(APIView):
    permission_classes = [IsAuthenticated, IsValidClientRequest]

    def post(self, request):
        data = request.data
        print("data",data)
        username = request.user.username
        service_name = data.get("service_name")
        logtype = data.get("logType", "INFO").upper()
        info = data.get("info", "")
        
        UserLogs.objects.create(
            user=username,
            service_name=service_name,
            logtype=logtype,
            info=info
        )
        
        return Response({"status": "ok"})


class UserNotification(APIView):
    """
    recieve notification Notification model
    class Notifications(models.Model):
    user = models.CharField()
    variables = models.JSONField(null=True, blank=True)
    sucess = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    """
    permission_classes = [IsAuthenticated, IsValidClientRequest]

    def post(self, request):
        data = request.data
        usrname = request.user.username
        variables = data.get("variables")
        sucess = data.get("sucess")
        
        Notifications.objects.create(
            user=usrname,
            variables=variables,
            sucess=sucess
        )
        
        return Response({"status": "ok"})

class UserProxyView(APIView):
    """
    reteurn list of proxies related to user
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            proxies = [{
                "ip": proxy.ip,
                "port": proxy.port,
                "username": proxy.username,
                "password": proxy.password
            } for proxy in UserProxy.objects.filter(users=user)]
            
            return Response({"proxies": proxies})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
class UserInfoView(APIView):
    """
    return user info, username, last login
    """
    permission_classes = [IsAuthenticated, IsValidClientRequest]

    def post(self, request):
        try:
                
            return Response({
                "username": request.user.username,
                "email": request.user.email,
            })
        except Exception as e:
            print(e)
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


BOT_TOKEN = "5383800787:AAEPyU2gjQQS7YTe1W3Mcld3fPvcEH6xL2o"
BOT_USERNAME = 'xServerMagicBot'

bot = telebot.TeleBot(BOT_TOKEN)
@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        text = getattr(message, 'text', '')
        parts = text.split()

        if len(parts) < 2:
            bot.reply_to(message, "Invalid login link")
            return

        token = parts[1]
        nonce = verify_token(token, max_age=60)  # 60s token lifetime

        # Check if token is already used
        existing = TelegramAuthSession.objects.filter(token=token).first()
        if existing:
            bot.reply_to(message, "❌ Token already used")
            return

        if not nonce:
            bot.reply_to(message, "❌ Token expired or invalid")
            return

        telegram_id = message.from_user.id
        user = AllowedTelgramUsers.objects.filter(telegram_id=telegram_id).first()
        if not user:
            bot.reply_to(message, "❌ Not authorized")
            return

        # Create session record in DB
        session = TelegramAuthSession.objects.create(
            token=token,
            telegram_id=telegram_id,
            user=user.user,
            is_authenticated=True
        )

        bot.reply_to(message, "✅ Login successful")
        print(f"Session created: {session}")

    except Exception as e:
        print("handle_start exception:", e)


SECRET = "your_secret"

class CreateAuthSessionView(View):
    def get(self, request):
        token = generate_token()
        auth_url = f"https://t.me/{BOT_USERNAME}?start={token}"

        return JsonResponse({
            "token": token,
            "auth_url": auth_url
        })

@method_decorator(csrf_exempt, name='dispatch')
class CheckTelegramSessionView(View):

    def post(self, request):
        try:
            body = json.loads(request.body)
            token = body.get("token")
        except Exception:
            return JsonResponse({"error": "invalid request"}, status=400)

        session = TelegramAuthSession.objects.filter(token=token).first()

        # session must exist first
        if not session:
            return JsonResponse({"authenticated": False})

        # check expiration
        if session.created_at < timezone.now() - datetime.timedelta(minutes=2):
            return JsonResponse({"authenticated": False})

        if session.is_authenticated:
            token, _ = Token.objects.get_or_create(user=session.user)

            return JsonResponse({
                "authenticated": True,
                "api_token": token.key
            })

        return JsonResponse({"authenticated": False})


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(View):
    def post(self, request):
        try:
            print("received webhook: view ",request.body)
            body_text = request.body.decode('utf-8', errors='ignore')
            update_data = json.loads(body_text)
            update = telebot.types.Update.de_json(update_data)
            bot.process_new_updates([update])
            return HttpResponse("OK")
        
        except Exception as e:
            print("Webhook error:", e)
            return HttpResponse("Error", status=500)

