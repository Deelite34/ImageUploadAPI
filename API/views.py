from API.models import StoredImage, APIUserProfile, GeneratedImage, AccountTypePermissions
from API.serializers import StoredImageSerializer
from django.contrib.auth.models import User
from django.db.models import Count
from django.urls import reverse
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from easy_thumbnails.files import get_thumbnailer

class HelloWorldView(APIView):
    # Need to login in /api/auth/token/login to get token
    # token needs to be included in header to use this api
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_info = User.objects.select_related('apiuserprofile__account_type').get(username=request.user.username)
        content = {'message': 'Hello, World!',
                   'your_account_type': user_info.apiuserprofile.account_type.name,
                   'your_username': user_info.username}
        return Response(content)


class ImageUploadView(viewsets.ViewSet):
    """
    User can send POST request with auth token in header to the endpoint /api/thumbnail/
    POST request should include .jpg or .png image file.
    User will receive response containing info on source image, and thumbnails generated using source image.

    TODO: add time limited thumbnail feature
    User can also send similiar request to endpoint /Thumbnail/timed/ which needs to include expire time,
    and image file.
    User will receive response containing URL and expire date
    """
    serializer_class = StoredImageSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        """
        Lists all images and related thumbnails for specific user
        """
        try:
            # Normal user should include token in his header
            user = Token.objects.get(key=request.META.get('HTTP_AUTHORIZATION')
                                     .split()[1]).only('user_id').user_id
        except AttributeError:
            # Admin who does not include token, but is logged in can still use API
            user = request.user.id

        queryset = StoredImage.objects.filter(owner=user)
        serializer = StoredImageSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Lists all images and related thumbnails for specific user
        """
        try:
            # Normal user should include token in his header
            user = Token.objects.select_related('').get(key=request.META.get('HTTP_AUTHORIZATION')
                                     .split()[1]).only('user_id')
        except AttributeError:
            # Admin who does not include token, but is logged in can still use API
            user = request.user

        # TODO fix specific item not displaying due to incorrect owner parameter
        queryset = StoredImage.objects.get(owner=user.APIUserProfile, id=pk)
        serializer = StoredImageSerializer(queryset)
        return Response(serializer.data)

    def create(self, request):
        """
        Creates a link of the user making the request and updates users url_count value.
        Requires request to cointain 'url_input': 'value' field,
        where value is the URL to be shortened.
        """
        try:
            # Normal user should include token in his header
            user = Token.objects.get(key=request.META.get('HTTP_AUTHORIZATION')
                                     .split()[1]).only('user_id')
        except AttributeError:
            # Admin who does not include token, but is logged in can still use API
            user = request.user

        serializer = StoredImageSerializer(data=request.data, context={"request": request})  # image sent by user

        # Check permissions, and create all permitted thumbnails
        if serializer.is_valid():
            # TODO on image upload file on filesystem should be deleted(django signals?)
            serializer.save(owner=user.apiuserprofile)

            # Get user permissions, custom thumbnail sizes and original image object
            queryset_permissions = APIUserProfile.objects.select_related('account_type') \
                .prefetch_related('account_type__custom_size').get(user=user.id)
            source_image = StoredImage.objects.filter(owner=user.apiuserprofile).latest('id')

            # Create all thumbnail images, assign them to specific URLs
            created_thumbnails = []
            # TODO move size strings to constant variables to allow easier modification+possibly
            # TODO thumbnails_aliases from settings.py
            sizes = ['200x200',
                     '400x400',
                     f'{source_image.img_width}x{source_image.img_height}']

            default_permissions = [queryset_permissions.account_type.create_200px_thumbnail_perm,
                                   queryset_permissions.account_type.create_400px_thumbnail_perm,
                                   queryset_permissions.account_type.create_original_img_link_perm]

            # Create standard allowed thumbnails
            for index, permission in enumerate(default_permissions):
                if permission is True:
                    #TODO optimize object creation with bulk_create() - check docs
                    #TODO possibly move thumbnail creation to separate place/async function/celery
                    x_side = sizes[index].split('x')[0]
                    y_side = sizes[index].split('x')[1]
                    options = {'size': (x_side, y_side), 'upscale': True, 'crop': True}
                    img = get_thumbnailer(source_image.file).get_thumbnail(options)

                    thumbnail = GeneratedImage.objects.create(source_image=source_image,
                                                              modified_image=img.url,
                                                              type=sizes[index])
                    created_thumbnails.append(thumbnail)

            # Iterate over custom sizes assigned to account type, and create
            # custom size thumbnails
            related_custom_sizes = queryset_permissions.account_type.custom_size
            if default_permissions[2] is True and related_custom_sizes.count() > 0:
                for index, item in enumerate(related_custom_sizes.all()):
                    side = f"{str(item.size)}"
                    options = {'size': (side, side), 'upscale': True, 'crop': True}
                    img = get_thumbnailer(source_image.file).get_thumbnail(options)

                    side = related_custom_sizes.all()[index].size
                    img_type = f'{side}x{side}'

                    thumbnail = GeneratedImage.objects.create(source_image=source_image,
                                                              modified_image=img.url,
                                                              type=img_type)
                    created_thumbnails.append(thumbnail)

            created_thumbnails_data = {'thumbnails': {}}
            for index, item in enumerate(created_thumbnails):
                created_thumbnails_data['thumbnails'][item.type] = request.get_host() + '/i/' + item.slug + '/'

            # Dictionary containing created thumbnails
            updated_serializer_data = serializer.data
            updated_serializer_data.update(created_thumbnails_data)

            return Response(updated_serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
