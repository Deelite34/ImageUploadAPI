import os

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import pytest
# Create your tests here.
from API.models import CustomThumbnailSize, AccountTypePermissions, APIUserProfile,\
                       StoredImage, GeneratedImage

from ImageUploadAPI.settings import BASE_DIR, MEDIA_ROOT, TEST_MEDIA_ROOT


@pytest.fixture(scope="session", autouse=True)
def directory_setup():
    """Move to /API/test directory  before tests start, to ensure access to test image file"""
    os.chdir(TEST_MEDIA_ROOT)


@pytest.mark.django_db
class TestCustomThumbnailSizeModel:
    def test_to_string(self):
        size = 1000

        CustomThumbnailSize.objects.create(size=size)
        queryset = CustomThumbnailSize.objects.get(size=size)

        assert queryset.__str__() == f'{queryset.size}x{queryset.size}'


@pytest.mark.django_db
class TestAccountTypePermissionsModel:
    def test_to_string(self):
        name = "test name"

        queryset = AccountTypePermissions.objects.create(name=name)

        assert queryset.__str__() == f'{name}'


@pytest.mark.django_db
class TestAPIUserProfileModel:
    def test_to_string(self):
        test_user = User.objects.create(username='test_user', password='QFSV#^@#HE')

        APIUserProfile.objects.create(user=test_user)
        queryset = APIUserProfile.objects.select_related('user').get(user=test_user)

        assert queryset.__str__() == f'{queryset.user.username}'


@pytest.mark.django_db
class TestStoredImageModel:
    def test_to_string(self):
        # Arrange required data
        # Create and get User
        test_user = User.objects.create(username='test_user', password='QFSV#^@#HE')
        # Create and get APIUserPrpipofile
        api_user_profile_object = APIUserProfile.objects.create(user=test_user)
        # Create and get mock image to be used as file field for StoredImage
        mock_image_path = "test_image.png"
        mock_image = SimpleUploadedFile(name='test_image.png', content=open(mock_image_path, 'rb').read(),
                                        content_type='image/jpeg')

        # Act to get results to test
        StoredImage.objects.create(owner=api_user_profile_object, file=mock_image)
        image_object = StoredImage.objects.get(owner=api_user_profile_object)

        # file cleanup before assert ends function
        os.remove(image_object.file.path)

        # Assert expected results
        assert image_object.__str__() == f"{os.path.basename('test_image.png')}"




@pytest.mark.django_db
class TestGeneratedImageModel:
    def test_to_string(self):
        # Arrange required data
        test_user = User.objects.create(username='test_user', password='QFSV#^@#HE')
        APIUserProfile.objects.create(user=test_user)
        api_user = APIUserProfile.objects.select_related('user').get(user=test_user)
        mock_image_path = "test_image.png"
        mock_image = SimpleUploadedFile(name=mock_image_path, content=open(mock_image_path, 'rb').read(),
                                        content_type='image/jpeg')
        source_image = StoredImage.objects.create(owner=api_user, file=mock_image)

        # Act to get results to test
        generated_image = GeneratedImage.objects.create(source_image=source_image, type=200)

        # Assert expected results
        assert generated_image.__str__() == f"{generated_image.id}"

        # file cleanup
        image_object = StoredImage.objects.get(owner=api_user)
        os.remove(image_object.file.path)

