from django.http import HttpResponse, JsonResponse

from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from legisladores.models import Legisladores, IndiceLegisladores
from legisladores.serializers import LegisladoresSerializer, IndiceLegisladoresSerializer

@csrf_exempt
def legisladores(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        legisladores = Legisladores.objects.all()
        serializer = LegisladoresSerializer(legisladores, many=True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def legisladores_by_id(request, id_legislador):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        legisladores = Legisladores.objects
        serializer = LegisladoresSerializer(legisladores, many=True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def legisladores_index(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        legisladores = IndiceLegisladores.objects.all()
        serializer = IndiceLegisladoresSerializer(legisladores, many=True)
        return JsonResponse(serializer.data, safe=False)
