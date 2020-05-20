from rest_framework import serializers
from .models import GTINMap

class GTINMapSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GTINMap
        fields = ['gtin', 'host', 'path', 'gs1_compliant', 'use_ssl']

