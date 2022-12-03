from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .serializers import QuestionSerializer
from rest_framework.renderers import TemplateHTMLRenderer


class CoffeeAppApiView(APIView):
 #   renderer_classes = [TemplateHTMLRenderer]
  #  template_name = 'home.html'

    # add permission to check if user is authenticated NOPE
    # permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        maybe all possible manufacturer and models
        '''
        return Response({}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        '''
        ask a question
        '''
        question = {
            'manufacturer': request.data.get('manufacturer'),
            'model': request.data.get('model'),
            'question': request.data.get('question')
        }

        serializer = QuestionSerializer(question)

        if serializer.is_valid():
            serializer.ask()
            return Response(serializer.answer, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
