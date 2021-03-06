import json
import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from API.models import CustomThumbnailSize, AccountTypePermissions, APIUserProfile, StoredImage, GeneratedImage
from API.test.constants_tests import TEST_USER_LOGIN, TEST_USER_PASS, ENDPOINT_ALL, \
    CONTENT_TYPE_DEFAULT, MOCK_IMAGE_PATH, MOCK_WRONG_FILE_TYPE_PATH, TESTS_MEDIA_ROOT, TESTS_MEDIA_URL, \
    CONTENT_TYPE_PNG, MOCK_ALT_IMAGE_PATH, TEST_PROFILE_TYPE_NAME
from API.test.utils import db_data_preparation, create_test_client


pytestmark = pytest.mark.django_db  # all test functions are permitted to access test db

# todo implement uathorization with jwt token simple jwt
# todo add documentation drf-spectacular
# todo serving images(whitenoise? nginx/apache/similiar proper configuration?)


# Decorator will cause test user directories and images to be created in separate, easier to clean up directory
@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_all_endpoint_list():
    """
    Create test data, then list all items then test response status and content
    """
    initial_data = db_data_preparation()
    client = create_test_client(initial_data, authorize=True)
    
    mock_image = SimpleUploadedFile(name=MOCK_IMAGE_PATH, content=open(MOCK_IMAGE_PATH, 'rb').read(),
                                    content_type=CONTENT_TYPE_PNG)
    mock_image_b = SimpleUploadedFile(name=MOCK_ALT_IMAGE_PATH, content=open(MOCK_IMAGE_PATH, 'rb').read(),
                                      content_type=CONTENT_TYPE_PNG)

    client.post(ENDPOINT_ALL, {'file': mock_image}, format='multipart')
    client.post(ENDPOINT_ALL, {'file': mock_image_b}, format='multipart')
    response = client.get(ENDPOINT_ALL)
    json_dict = json.loads(response.content)

    assert response.status_code == 200
    assert len(json_dict) == 2
    assert len(json_dict[0].keys()) == 3
    assert len(json_dict[1].keys()) == 3
    assert len(json_dict[0]['thumbnails'][0].keys()) == 5
    assert len(json_dict[1]['thumbnails'][0].keys()) == 5


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_all_endpoint_retrieve():
    """
    Create test data, then retrieve created item then test response status and content
    """
    initial_data = db_data_preparation()
    client = create_test_client(initial_data, authorize=True)
    mock_image = SimpleUploadedFile(name=MOCK_IMAGE_PATH, content=open(MOCK_IMAGE_PATH, 'rb').read(),
                                    content_type=CONTENT_TYPE_PNG)

    post_response = client.post(ENDPOINT_ALL, {'file': mock_image}, format='multipart')
    post_json_dict = json.loads(post_response.content)
    created_item_id = post_json_dict['id']
    get_response = client.get(ENDPOINT_ALL, args=[created_item_id])
    get_json_dict = json.loads(get_response.content)

    assert get_response.status_code == 200
    assert len(get_json_dict) == 1
    assert len(get_json_dict[0].keys()) == 3
    assert len(get_json_dict[0]['thumbnails'][0].keys()) == 5


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_all_endpoint_create():
    """
    Post image to /api/all/ and test response status, response structure and content
    """
    initial_data = db_data_preparation()
    client = create_test_client(initial_data, authorize=True)
    mock_image = SimpleUploadedFile(name=MOCK_IMAGE_PATH, content=open(MOCK_IMAGE_PATH, 'rb').read(),
                                    content_type=CONTENT_TYPE_PNG)

    response = client.post(ENDPOINT_ALL, {'file': mock_image}, format='multipart')
    json_dict = json.loads(response.content.decode('utf8'))

    assert response.status_code == 201
    assert len(json.loads(response.content)) == 3
    assert len(json_dict['thumbnails'].keys()) == 5


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_timed_endpoint_create():
    """
    Post image to /api/timed/ and test response status, response structure and content
    """
    initial_data = db_data_preparation()
    endpoint_timed = '/api/timed/'
    client = create_test_client(initial_data, authorize=True)
    mock_image = SimpleUploadedFile(name=MOCK_IMAGE_PATH, content=open(MOCK_IMAGE_PATH, 'rb').read(),
                                    content_type=CONTENT_TYPE_PNG)
    request_body = {'file': mock_image, 'expire_time': 300, 'type': '200'}

    response = client.post(endpoint_timed, request_body, format='multipart')
    json_dict = json.loads(response.content)
    timed_image = GeneratedImage.objects.get(expire_date__isnull=False)

    assert response.status_code == 201
    assert timed_image.expire_time == request_body['expire_time']
    assert timed_image.type == request_body['type']
    assert len(json_dict.keys()) == 3
    assert len(json_dict['thumbnails'].keys()) == 1


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_no_token_all_list():
    """
    Try to get (list) images without providing token
    """
    initial_data = db_data_preparation()
    unauthorized_client = APIClient()
    client = create_test_client(initial_data, authorize=True)
    mock_image = SimpleUploadedFile(name=MOCK_IMAGE_PATH, content=open(MOCK_IMAGE_PATH, 'rb').read(),
                                    content_type=CONTENT_TYPE_PNG)

    client.post(ENDPOINT_ALL, {'file': mock_image}, format='multipart')
    response = unauthorized_client.get(ENDPOINT_ALL)
    json_dict = json.loads(response.content)

    assert response.status_code == 401
    assert len(json_dict.keys()) == 1


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_no_token_all_retrieve():
    """
    Try to get specific thumbnail without providing access token
    """
    initial_data = db_data_preparation()
    unauthorized_client = APIClient()
    client = create_test_client(initial_data, authorize=True)
    mock_image = SimpleUploadedFile(name=MOCK_IMAGE_PATH, content=open(MOCK_IMAGE_PATH, 'rb').read(),
                                    content_type=CONTENT_TYPE_PNG)

    post_response = client.post(ENDPOINT_ALL, {'file': mock_image}, format='multipart')
    post_dict = json.loads(post_response.content)
    created_item_id = post_dict['id']
    response = unauthorized_client.get(ENDPOINT_ALL, args=[created_item_id])
    get_json_dict = json.loads(response.content)

    assert response.status_code == 401
    assert len(get_json_dict.keys()) == 1


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_not_supported_request_type_response():
    """
    Test response when put or delete requests are made
    """
    initial_data = db_data_preparation()
    client = create_test_client(initial_data, authorize=True)

    response = client.put(ENDPOINT_ALL, {'data': 'asdf'})
    response_2 = client.delete(ENDPOINT_ALL, {'data': 'asdf'})
    json_dict = json.loads(response.content)
    json_dict_2 = json.loads(response.content)

    assert response.status_code == 405
    assert len(json_dict.keys()) == 1
    assert response_2.status_code == 405
    assert len(json_dict_2.keys()) == 1


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_not_owned_item_retrieve():
    """
    Test retrieving thumbnail that user did not create
    """
    initial_data = db_data_preparation()
    client_1 = create_test_client(initial_data, authorize=True)
    test_user_2 = User.objects.create(username=TEST_USER_LOGIN + "_2", password=TEST_USER_PASS)
    APIUserProfile.objects.create(user=test_user_2, account_type=initial_data['test_account_type'])
    client_2 = APIClient()
    token = Token.objects.create(user=test_user_2)
    client_2.force_authenticate(user=test_user_2, token=token)
    client_2.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    mock_image = SimpleUploadedFile(name=MOCK_IMAGE_PATH, content=open(MOCK_IMAGE_PATH, 'rb').read(),
                                    content_type=CONTENT_TYPE_PNG)

    post_response = client_1.post(ENDPOINT_ALL, {'file': mock_image}, format='multipart')
    post_json_dict = json.loads(post_response.content)
    created_item_id = post_json_dict['id']
    author_get_response = client_1.get(reverse('standard-detail', args=[created_item_id]))
    not_author_get_response = client_2.get(reverse('standard-detail', args=[created_item_id]))
    get_json_dict = json.loads(not_author_get_response.content)

    assert author_get_response.status_code == 200
    assert not_author_get_response.status_code == 404
    assert len(get_json_dict) == 1


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_malformed_request_response():
    """
    Send request containing rubbish data and without included file
    """
    initial_data = db_data_preparation()
    client = create_test_client(initial_data, authorize=True)

    response = client.post(ENDPOINT_ALL, {'qwert': 'yuiop'}, format='multipart')
    json_dict = json.loads(response.content.decode('utf8'))

    assert response.status_code == 400
    assert len(json_dict.keys()) == 1
    assert json_dict['file'][0].startswith('No file was submitted')


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_send_wrong_file_format():
    """
    test sending not an image to api
    """
    initial_data = db_data_preparation()
    client = create_test_client(initial_data, authorize=True)
    mock_image = SimpleUploadedFile(name=MOCK_WRONG_FILE_TYPE_PATH, content=open(MOCK_IMAGE_PATH, 'rb').read(),
                                    content_type=CONTENT_TYPE_DEFAULT)

    response = client.post(ENDPOINT_ALL, {'file': mock_image}, format='multipart')
    json_dict = json.loads(response.content.decode('utf8'))

    assert response.status_code == 400
    assert len(json_dict.keys()) == 1
    assert json_dict['file'][0].startswith('File extension ')  # file extension x is not allowed(...)
