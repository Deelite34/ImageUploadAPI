import pytest
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from API.models import CustomThumbnailSize, AccountTypePermissions, APIUserProfile, StoredImage, GeneratedImage
from API.test.constants_tests import TEST_USER_PASS, TEST_USER_LOGIN, TEST_MEDIA_ROOT, TEST_MEDIA_URL, \
    TEST_PROFILE_TYPE_NAME
from API.test.utils import db_data_preparation


pytestmark = pytest.mark.django_db  # all test functions can access db


@override_settings(MEDIA_URL=TEST_MEDIA_URL, MEDIA_ROOT=TEST_MEDIA_ROOT)
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
