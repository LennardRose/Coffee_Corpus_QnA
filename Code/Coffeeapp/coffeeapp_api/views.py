from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .question_answering import QuestionAnswerer
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

        questionanswerer = QuestionAnswerer(request.data.get('manufacturer'),
                                            request.data.get('product_name'),
                                            request.data.get('language'),
                                            request.data.get('questions'))

        if questionanswerer.is_valid():
            questionanswerer.ask()
            return Response(questionanswerer.answers, status=status.HTTP_200_OK)

        return Response(questionanswerer.errors, status=status.HTTP_400_BAD_REQUEST)
