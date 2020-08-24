from rest_framework import serializers
from .models import Handwriting

class HandwritingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Handwriting
        fields = '__all__'