from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .question_answering import QuestionAnswerer
from rest_framework.renderers import TemplateHTMLRenderer


class CoffeeAppApiView(APIView):

    # uncomment these for beautiful website
    #renderer_classes = [TemplateHTMLRenderer]
    #template_name = 'home.html'


    def get(self, request, *args, **kwargs):
        '''
        maybe all possible manufacturer and models
        '''
        return Response({}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        '''
        ask a question
        '''

        questionanswerer = QuestionAnswerer(manufacturer=request.data.get('manufacturer'),
                                            product_name=request.data.get('product_name'),
                                            language=request.data.get('language'),
                                            question=request.data.get('question'))

        if questionanswerer.is_valid():
            questionanswerer.ask()
            return Response(questionanswerer.answers, status=status.HTTP_200_OK)

        return Response(questionanswerer.errors, status=status.HTTP_400_BAD_REQUEST)
