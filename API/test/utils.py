from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from API.models import CustomThumbnailSize, AccountTypePermissions, APIUserProfile, StoredImage, GeneratedImage

from API.test.constants_tests import TEST_USER_LOGIN, TEST_USER_PASS, ENDPOINT_ALL, \
    CONTENT_TYPE_DEFAULT, MOCK_IMAGE_PATH, MOCK_WRONG_FILE_TYPE_PATH, TESTS_MEDIA_ROOT, TESTS_MEDIA_URL, \
    CONTENT_TYPE_PNG, MOCK_ALT_IMAGE_PATH, TEST_PROFILE_TYPE_NAME


def db_data_preparation():
    """
    Create initial db tables; custom thumbnail sizes, profile type, user, assign profile type to user,
    :return: data - dict containing references to created data
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


def create_test_client(initial_data, authorize=True):
    """
    Creates APIClient, and authorizes it with a token
    :return: client - APIClient instance authorized with token
    """
    client = APIClient()
    user = initial_data['test_user']
    if authorize:
        token = Token.objects.create(user=user)
        client.force_authenticate(user=user, token=token)
        # api views check for authorization in the request header, therefore apiclient needs token in his header
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client
