import io
import json
import os

import pytest
from API.models import CustomThumbnailSize, AccountTypePermissions, APIUserProfile, StoredImage, GeneratedImage
from ImageUploadAPI.settings import TEST_MEDIA_ROOT
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from PIL import Image


TEST_USER_LOGIN = 'test_user'
TEST_USER_PASS = 'qwerty12345'
TEST_PROFILE_TYPE_NAME = "test_profile_type"
TEST_IMAGE_WIDTH = 840
TEST_IMAGE_HEIGHT = 680
pytestmark = pytest.mark.django_db


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


def test_all_endpoint_list():
    """
    Create test data, then list all items then test response status and content
    """
    initial_data = db_data_preparation()
    endpoint_all = '/api/all/'
    client = APIClient()
    client.login(username=TEST_USER_LOGIN, password=TEST_USER_PASS)
    token = Token.objects.create(user=initial_data['test_user'])
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    mock_image_path = "test_image.png"
    mock_alt_image_path = "test_image_b.png"
    # To post 2 images, they need to be separate,
    # otherwise second post request will return 400 with info about empty file
    mock_image = SimpleUploadedFile(name=mock_image_path, content=open(mock_image_path, 'rb').read(),
                                    content_type='image/png')
    mock_image_b = SimpleUploadedFile(name=mock_alt_image_path, content=open(mock_image_path, 'rb').read(),
                                      content_type='image/png')

    client.post(endpoint_all, {'file': mock_image}, format='multipart')
    client.post(endpoint_all, {'file': mock_image_b}, format='multipart')
    response = client.get(endpoint_all)
    json_dict = json.loads(response.content)

    assert response.status_code == 200
    assert len(json_dict) == 2
    assert len(json_dict[0].keys()) == 3
    assert len(json_dict[1].keys()) == 3
    assert len(json_dict[0]['thumbnails'][0].keys()) == 5
    assert len(json_dict[1]['thumbnails'][0].keys()) == 5


def test_all_endpoint_create():
    """
    Post image to /api/all/ and test response status, response structure and content
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

    response = client.post(endpoint_all, {'file': mock_image}, format='multipart')
    json_dict = json.loads(response.content.decode('utf8'))

    assert response.status_code == 201
    assert len(json.loads(response.content)) == 3
    assert len(json_dict['thumbnails'].keys()) == 5

    # possible TODO file cleanup(create cleanup script?): rename test_image to some unique, long string
    # and create functiong removing all images starting with that phrase within /media/ directory

def test_timed_endpoint_create():
    """
    Post image to /api/timed/ and test response status, response structure and content
    """
    initial_data = db_data_preparation()
    endpoint_timed = '/api/timed/'
    client = APIClient()
    client.login(username=TEST_USER_LOGIN, password=TEST_USER_PASS)
    token = Token.objects.create(user=initial_data['test_user'])
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    mock_image_path = "test_image.png"
    mock_image = SimpleUploadedFile(name=mock_image_path, content=open(mock_image_path, 'rb').read(),
                                    content_type='image/png')
    request_body = {'file': mock_image, 'expire_time': 300, 'type': '200'}

    response = client.post(endpoint_timed, request_body, format='multipart')
    #response = clieng.get(reverse('edit_project', kwargs={'project_id':4}))
    json_dict = json.loads(response.content)
    timed_image = GeneratedImage.objects.get(expire_date__isnull=False)

    assert response.status_code == 201
    assert timed_image.expire_time == request_body['expire_time']
    assert timed_image.type == request_body['type']
    assert len(json_dict.keys()) == 3
    assert len(json_dict['thumbnails'].keys()) == 1

# TODO test attempts to request data when unauthorized, requesting data that is not own, trying to delete or modify
# disallowed items

# TODO sending malformed requests
