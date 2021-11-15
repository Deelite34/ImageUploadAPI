import io
import json
import os

import pytest
from API.models import CustomThumbnailSize, AccountTypePermissions, APIUserProfile, StoredImage, GeneratedImage
from ImageUploadAPI.settings import TEST_MEDIA_ROOT
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from PIL import Image


TEST_USER_LOGIN = 'test_user'
TEST_USER_PASS = 'qwerty12345'
TEST_PROFILE_TYPE_NAME = "test_profile_type"
TEST_IMAGE_WIDTH = 840
TEST_IMAGE_HEIGHT = 680
pytestmark = pytest.mark.django_db  # all test functions can access db


@pytest.fixture(scope="session", autouse=True)
def directory_setup():
    """Move to /API/test directory  before tests start, to ensure access to test image file"""
    os.chdir(TEST_MEDIA_ROOT)


def db_data_preparation():
    """
    Create initial db tables; custom thumbnail sizes, profile type, user, assign profile type to user,
    :return: data - dictionary containing references to created data
    """
    test_user = User.objects.create(username=TEST_USER_LOGIN, password=TEST_USER_PASS)
    test_account_type = AccountTypePermissions.objects.create(name=TEST_PROFILE_TYPE_NAME,
                                                              create_200px_thumbnail_perm=True,
                                                              create_400px_thumbnail_perm=True,
                                                              create_original_img_link_perm=True,
                                                              create_custom_sized_thumbnail_perm=True,
                                                              create_time_limited_link_perm=True)
    test_custom_thumbnail_size_1 = CustomThumbnailSize.objects.create(size=500)
    test_custom_thumbnail_size_2 = CustomThumbnailSize.objects.create(size=1000)
    test_account_type.custom_size.add(test_custom_thumbnail_size_1,
                                      test_custom_thumbnail_size_2)
    test_api_user_profile = APIUserProfile.objects.create(user=test_user, account_type=test_account_type)

    data = {
        'test_user': test_user,
        'test_account_type': test_account_type,
        'test_custom_thumbnail_size_1': test_custom_thumbnail_size_1,
        'test_custom_thumbnail_size_2': test_custom_thumbnail_size_2,
        'test_api_user_profile': test_api_user_profile,
    }
    return data


def test_image_webpage():
    """
    Create thumbnail, test existence of corresponding image page where img should be visible
    """

    initial_data = db_data_preparation()
    endpoint_all = '/api/all/'
    client = APIClient()
    client.login(username=TEST_USER_LOGIN, password=TEST_USER_PASS)
    token = Token.objects.create(user=initial_data['test_user'])
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    mock_image_path = "test_image.png"
    mock_image = SimpleUploadedFile(name=mock_image_path, content=open(mock_image_path, 'rb').read(),
                                    content_type='image/png')
    client.post(endpoint_all, {'file': mock_image}, format='multipart')
    images = GeneratedImage.objects.select_related('source_image')\
                                   .filter(source_image__owner=initial_data['test_api_user_profile'])

    responses = []
    page_bodies = []
    for image in images:
        response = client.get(reverse('display_image', args=[image.slug]))
        responses.append(response)
        page_bodies.append(response.content.decode('utf-8'))

    for index, response in enumerate(responses):
        assert response.status_code == 200
        assert 'img' in page_bodies[index]
