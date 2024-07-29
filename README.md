# Question Answering System

Comprehensive Question Answering System for Technical Documents (Coffee Machines in this implementation). 

## Poster
![](Documentation_presentation/Poster.PNG?raw=true)

## Paper

![](Documentation_presentation/Question_Answering_Paper/0001.png?raw=true)
![](Documentation_presentation/Question_Answering_Paper/0002.png?raw=true)
![](Documentation_presentation/Question_Answering_Paper/0003.png?raw=true)
![](Documentation_presentation/Question_Answering_Paper/0004.png?raw=true)
![](Documentation_presentation/Question_Answering_Paper/0005.png?raw=true)
![](Documentation_presentation/Question_Answering_Paper/0006.png?raw=true)
![](Documentation_presentation/Question_Answering_Paper/0007.png?raw=true)
![](Documentation_presentation/Question_Answering_Paper/0008.png?raw=true)
![](Documentation_presentation/Question_Answering_Paper/0009.png?raw=true)
![](Documentation_presentation/Question_Answering_Paper/0010.png?raw=true)
![](Documentation_presentation/Question_Answering_Paper/0011.png?raw=true)
![](Documentation_presentation/Question_Answering_Paper/0012.png?raw=true)


## Installation

Make sure to have ElasticSearch running with the added metadata of the corpus.

### Backend

- Step 1: Make sure you have django installed in your environment
  > `pip install django djangorestframework django-cors-headers`
- Step 2: Change directory to where Backend is located
  > `cd ./Code/CoffeeappBackend`
- Step 3: Run the server
  > `python manage.py runserver`

### Frontend

- Step 1: Make sure you have node installed in your environment
  > [https://nodejs.org/de/download/](https://nodejs.org/de/download/)
- Step 2: Change directory to where Frontend is located
  > `cd ./Code/CoffeeappFrontend`
- Step 3: Install Angular CLI
  > `npm install -g @angular/cli`
- Step 4: Install dependencies
  > `npm install`
- Step 5: Run the server
  > `ng serve --open`
