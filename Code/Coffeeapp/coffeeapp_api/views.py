from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .question_answering import QuestionAnswerer
from rest_framework.renderers import TemplateHTMLRenderer
import Code.Clients.client_factory as factory
from django.http import JsonResponse


def home(request):
    
    # Retrieve every manufacturer from ES
    all_manufacturers = factory.get_meta_client().get_manufacturers()
    
    # Retrieve every product by manufacturer from ES
    products_by_manufacturer = factory.get_meta_client().get_products_of_all_manufacturers()
    
    if request.method == "POST":
        # Retrieve answer for question
        manufacturer = request.POST['manufacturer']
        product = request.POST['product']
        question = request.POST['question']
      
        questionanswerer = QuestionAnswerer(manufacturer=manufacturer,
                                            product_name=product,
                                            language='en',
                                            question=question)
      
      
        if questionanswerer.is_valid():
            questionanswerer.ask()
            
        return render(request, 'home.html', {
            'manufacturers': all_manufacturers,
            'products_by_manufacturer': products_by_manufacturer,
            'answers': questionanswerer.answers
            })
    
    
    return render(request, 'home.html', {
        'manufacturers': all_manufacturers,
        'products_by_manufacturer': products_by_manufacturer,
        'answers': None
        })
    
def get_products(request):
     
    manufacturer = request.GET.get('manufacturer')
    products = factory.get_meta_client().get_products_of_manufacturer(manufacturer)
    
    return JsonResponse(products, safe=False)

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