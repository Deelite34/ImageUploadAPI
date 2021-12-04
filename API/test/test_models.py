import os
import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from API.models import CustomThumbnailSize, AccountTypePermissions, APIUserProfile,\
                       StoredImage, GeneratedImage
from API.test.constants_tests import TESTS_MEDIA_ROOT, TESTS_MEDIA_URL, TEST_USER_PASS, TEST_USER_LOGIN


pytestmark = pytest.mark.django_db


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_customthumbnailssize_to_string():
    size = 1000

    CustomThumbnailSize.objects.create(size=size)
    queryset = CustomThumbnailSize.objects.get(size=size)

    assert queryset.__str__() == f'{queryset.size}x{queryset.size}'


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_accounttypepermisions_to_string():
    name = "test name"

    queryset = AccountTypePermissions.objects.create(name=name)

    assert queryset.__str__() == f'{name}'


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_apiuserprofile_to_string():
    test_user = User.objects.create(username=TEST_USER_LOGIN, password=TEST_USER_PASS)

    APIUserProfile.objects.create(user=test_user)
    queryset = APIUserProfile.objects.select_related('user').get(user=test_user)

    assert queryset.__str__() == f'{queryset.user.username}'


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_storedimage_to_string():
    test_user = User.objects.create(username=TEST_USER_LOGIN, password=TEST_USER_PASS)
    api_user_profile_object = APIUserProfile.objects.create(user=test_user)
    mock_image_path = "test_image.png"
    mock_image = SimpleUploadedFile(name='test_image.png', content=open(mock_image_path, 'rb').read(),
                                    content_type='image/jpeg')

    StoredImage.objects.create(owner=api_user_profile_object, file=mock_image)
    image_object = StoredImage.objects.get(owner=api_user_profile_object)

    assert image_object.__str__() == f"{os.path.basename('test_image.png')}"


@override_settings(MEDIA_URL=TESTS_MEDIA_URL, MEDIA_ROOT=TESTS_MEDIA_ROOT)
def test_generatedimage_to_string():
    test_user = User.objects.create(username=TEST_USER_LOGIN, password=TEST_USER_PASS)
    APIUserProfile.objects.create(user=test_user)
    api_user = APIUserProfile.objects.select_related('user').get(user=test_user)
    mock_image_path = "test_image.png"
    mock_image = SimpleUploadedFile(name=mock_image_path, content=open(mock_image_path, 'rb').read(),
                                    content_type='image/jpeg')
    source_image = StoredImage.objects.create(owner=api_user, file=mock_image)

    generated_image = GeneratedImage.objects.create(source_image=source_image, type=200)

    assert generated_image.__str__() == f"{generated_image.id}"
