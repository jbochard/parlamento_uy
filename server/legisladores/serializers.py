from legisladores.models import Legisladores, IndiceLegisladores
from rest_framework import serializers

class LegisladoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Legisladores
        fields = ('cuerpo','email','id_legislador','lema','nombre')

class IndiceLegisladoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndiceLegisladores
        fields = ('nombre','cuerpo','lema','id_legislador','asistencias','citaciones','proyectos_total','informes_total')
