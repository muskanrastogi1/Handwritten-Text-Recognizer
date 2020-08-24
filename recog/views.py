from django.shortcuts import render
from .models import Handwriting
from .serializers import HandwritingSerializer
from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.decorators import parser_classes
import json, sys, os, environ, time
from django.conf import settings
from uuid import uuid4
import requests
from azure.storage.blob import BlobServiceClient, PublicAccess, BlobClient
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
environ.Env.read_env()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "try.settings.local")
endpoint = env("COMPUTER_VISION_ENDPOINT")
subscription_key = env("COMPUTER_VISION_SUBSCRIPTION_KEY")
connect_str = env('AZURE_STORAGE_CONNECTION_STRING')
# Create your views here.

@parser_classes((MultiPartParser,JSONParser))
class handwritingViewSet(viewsets.ModelViewSet):
    permission_class = [permissions.IsAuthenticated]
    serializer_class = HandwritingSerializer

    def perform_create(self, serializer):
        file = self.request.FILES['image']
        #owner = self.request.user
        serializer.save()
        data = serializer.data
        uuid = data['uuid']
        split = data['image'].split('/')     # uploaded image name from media

        # Create the BlockBlockService that is used to call the Blob service for the storage account
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
  
        # path to image file
        local_path = os.path.join(settings.MEDIA_ROOT, 'handwriting')
        local_file_name = split[-1]
        full_path_to_file = os.path.join(local_path, local_file_name)

        # Upload the file, use local_file_name for the blob name
        container_name ='handwritten-text'
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)

        with open(full_path_to_file,"rb") as data:
           blob_client.upload_blob(data)
        # Done

        # processing image
        text = processing(split[-1])
        instance = Handwriting.objects.filter(uuid=uuid).update(text=text)
        

    def get_queryset(self):
        uuid = self.request.query_params.get('id')
        queryset = Handwriting.objects.filter(uuid=uuid)
        return (queryset)



def processing(file):
        container = "handwritten-text"
        text_recognition_url = endpoint + "/vision/v3.0/read/analyze"

        # image_url -> Of the handwritten image (to be recognized).
        file_name = file
        image_url = "https://textimage.blob.core.windows.net/handwritten-text/" + file_name

        # blob_url
        #blob_url = "https://account.blob.core.windows.net/container/" + file_name
        #blob_client = BlobClient.from_blob_url(blob_url=image_url)


        headers = {'Ocp-Apim-Subscription-Key': subscription_key}
        data = {'url': image_url}
        response = requests.post(
            text_recognition_url, headers=headers, json=data)
        response.raise_for_status()

        # Holds the URI used to retrieve the recognized text.
        operation_url = response.headers["Operation-Location"]

        # The recognized text isn't immediately available, so poll to wait for completion.
        analysis = {}
        poll = True
        while (poll):
            response_final = requests.get(
                response.headers["Operation-Location"], headers=headers)
            analysis = response_final.json()
            #text_dict = json.loads(analysis)
            #print(json.dumps(analysis, indent=4))
            time.sleep(1)
            if ("analyzeResult" in analysis):
                poll = False
            if ("status" in analysis and analysis['status'] == 'failed'):
                poll = False
        text = (analysis['analyzeResult']['readResults'][0]['lines'])
        final = " "
        for i in range(len(text)):
                final=final+str(text[i]['text']+'\n'+" ")
        return final
        #blob_client.delete_blob(delete_snapshots=False)