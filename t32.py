import json
import logging

import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from msrest.authentication import CognitiveServicesCredentials
import subprocess
import os


def main(event: func.EventGridEvent, context: func.Context):

    ur = os.environ.get('VIDEO_STORAGE_ACCOUNT_URL')
    cv_url = os.environ['CV_ENDPOINT']
    cv_key = os.environ['CV_SUBSCRIPTION_KEY']
    cs_url = os.environ['CS_ENDPOINT']
    cs_key = os.environ['CS_KEY']

    longname = event.subject.split('/')[-1]
    name = longname.split('.')[0]

    cvCredential = CognitiveServicesCredentials(cv_key)
    cvClient = ComputerVisionClient(cv_url, cvCredential)

    imageurl = ur + 'thumbnail-container/' + longname
    tags = cvClient.tag_image(imageurl)

    tagarr = []
    for tag in tags.tags:
        tagarr.append(tag.name)

    logging.info(tagarr)

    data = [{
        "@search.action": "upload",
        "id": name,
        "tags": tagarr
    }]

    logging.info(data)

    searchClient = SearchClient(endpoint=cs_url,
                                index_name='csindex',
                                credential=AzureKeyCredential(cs_key))

    searchClient.upload_documents(documents=data)

    logging.info('End of request')
