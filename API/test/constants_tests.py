import os
from ImageUploadAPI.settings import BASE_DIR

TEST_USER_LOGIN = 'test_user'
TEST_USER_PASS = 'qwerty12345'
TEST_PROFILE_TYPE_NAME = "test_profile_type"
TEST_IMAGE_WIDTH = 840
TEST_IMAGE_HEIGHT = 680
ENDPOINT_ALL = '/api/all/'
MOCK_IMAGE_PATH = "test_image.png"
MOCK_WRONG_FILE_TYPE_PATH = "test_text.txt"
MOCK_ALT_IMAGE_PATH = "test_image_b.png"
CONTENT_TYPE_PNG = 'image/png'
CONTENT_TYPE_DEFAULT = 'text/plain'
TESTS_MEDIA_ROOT = os.path.join(BASE_DIR, 'tests_media')
TESTS_MEDIA_URL = '/tests_media/'
