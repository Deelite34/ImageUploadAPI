from API.models import StoredImage, APIUserProfile, GeneratedImage
from API.serializers import StoredImageSerializer, TimeLimitedImageSerializer
from API.utils import set_generated_image_model_slug_and_expire_date
from easy_thumbnails.files import get_thumbnailer
from rest_framework import viewsets, status
from rest_framework.authtoken.admin import User
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.backends import TokenBackend


class ImageUploadView(viewsets.ViewSet):
    """
    User can send POST request with auth token in header to the endpoint /api/thumbnail/
    POST request should include .jpg or .png image file.
    User will receive response containing info on source image, and thumbnails generated using source image.

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
            # Normal user should include token or jwt token in his header
            request_token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')
            if request_token[0] == "Bearer":
                data = TokenBackend(algorithm='HS256').decode(request_token[1], verify=False)
                token_user_id = data['user_id']
                token_user = User.objects.get(id=token_user_id).user_id
            elif request_token[0] == "Token":
                token_user_id = Token.objects.get(key=request_token[1]).only('user_id').user_id
                token_user = User.objects.get(id=token_user_id).user_id
        except AttributeError:
            # Admin who does not include token, but is logged in can still use API
            token_user = request.user.id

        queryset = StoredImage.objects.filter(owner=token_user)
        serializer = StoredImageSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Lists specific uploaded image and related thumbnails
        """
        try:
            # Normal user should include token or jwt token in his header
            request_token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')
            if request_token[0] == "Bearer":
                data = TokenBackend(algorithm='HS256').decode(request_token[1], verify=False)
                token_user_id = data['user_id']
                # token_user = User.objects.get(id=token_user_id).id
            elif request_token[0] == "Token":
                token_user_id = Token.objects.get(key=request_token[1]).only('user_id').user_id
                # token_user = User.objects.get(id=token_user_id).id
                # token_user = User.objects.select_related('apiuserprofile').get(id=token_user_id)
            token_user = User.objects.select_related('apiuserprofile').get(id=token_user_id)
        except AttributeError:
            # Admin who does not include token, but is logged in can still use API
            token_user = request.user

        try:
            queryset = StoredImage.objects.get(owner=token_user.apiuserprofile.id, id=pk)
        except StoredImage.DoesNotExist:
            data = {"detail": "Item not found"}
            return Response(data, status=status.HTTP_404_NOT_FOUND)

        serializer = StoredImageSerializer(queryset, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """
        Checks authorization of user, then creates thumbnails for all available for user profile permissions, except
        timed thumbnails
        """
        try:
            # Normal user should include token or jwt token in his header
            request_token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')
            if request_token[0] == "Bearer":
                data = TokenBackend(algorithm='HS256').decode(request_token[1], verify=False)
                token_user_id = data['user_id']
                token_user = User.objects.get(id=token_user_id)
            elif request_token[0] == "Token":
                token_user = Token.objects.get(key=request_token[1]).only('user_id')
                # token_user = User.objects.get(id=token_user_id).id
        except AttributeError:
            # Admin who does not include token, but is logged in can still use API
            token_user = request.user

        serializer = StoredImageSerializer(data=request.data, context={"request": request})  # image sent by user

        # Check permissions, and create all permitted thumbnails
        if serializer.is_valid():
            serializer.save(owner=token_user.apiuserprofile)

            # Get user permissions, custom thumbnail sizes and original image object
            queryset_permissions = APIUserProfile.objects.select_related('account_type') \
                .prefetch_related('account_type__custom_size').get(user=token_user.id)
            source_image = StoredImage.objects.filter(owner=token_user.apiuserprofile).latest('id')

            # Create all thumbnail images, assign them to specific URLs
            # TODO move size strings to constant variables to allow easier modification+possibly
            # TODO thumbnails_aliases from settings.py
            sizes = ['200x200',
                     '400x400',
                     f'{source_image.img_width}x{source_image.img_height}']

            default_permissions = [queryset_permissions.account_type.create_200px_thumbnail_perm,
                                   queryset_permissions.account_type.create_400px_thumbnail_perm,
                                   queryset_permissions.account_type.create_original_img_link_perm]

            # Create standard allowed thumbnails
            thumbnails_to_be_bulk_created = []
            for index, permission in enumerate(default_permissions):
                if permission is True:
                    # TODO possibly move thumbnail creation to separate place/async function/celery
                    x_side = sizes[index].split('x')[0]
                    y_side = sizes[index].split('x')[1]
                    options = {'size': (x_side, y_side), 'upscale': True, 'crop': True}
                    img = get_thumbnailer(source_image.file).get_thumbnail(options)

                    thumbnail = GeneratedImage(source_image=source_image,
                                               modified_image=img.url,
                                               type=sizes[index])
                    thumbnails_to_be_bulk_created.append(thumbnail)

            # Iterate over custom sizes assigned to account type, and create custom sized thumbnails
            related_custom_sizes = queryset_permissions.account_type.custom_size
            if default_permissions[2] is True and related_custom_sizes.count() > 0:
                for index, item in enumerate(related_custom_sizes.all()):
                    side = f"{str(item.size)}"
                    options = {'size': (side, side), 'upscale': True, 'crop': True}
                    img = get_thumbnailer(source_image.file).get_thumbnail(options)

                    side = str(related_custom_sizes.all()[index].size)
                    side_full = f'{side}x{side}'

                    thumbnail = GeneratedImage(source_image=source_image,
                                               modified_image=img.url,
                                               type=side_full)
                    thumbnails_to_be_bulk_created.append(thumbnail)

            response_thumbnails_data = {'thumbnails': {}}
            for index, item in enumerate(thumbnails_to_be_bulk_created):
                set_generated_image_model_slug_and_expire_date(item)
                response_thumbnails_data['thumbnails'][item.type] = request.get_host() + '/i/' + item.slug + '/'

            GeneratedImage.objects.bulk_create(thumbnails_to_be_bulk_created)
            # Dictionary containing created thumbnails

            updated_serializer_data = serializer.data
            updated_serializer_data.update(response_thumbnails_data)
            return Response(updated_serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TimeLimitedThumbnailView(viewsets.ViewSet):
    serializer_class = TimeLimitedImageSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        """
        Checks authorization of user, then creates a time limited thumbnail if user permission allows it
        """
        try:
            # Normal user should include token or jwt token in his header
            request_token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')
            if request_token[0] == "Bearer":
                data = TokenBackend(algorithm='HS256').decode(request_token[1], verify=False)
                token_user_id = data['user_id']
                token_user = User.objects.get(id=token_user_id)
            elif request_token[0] == "Token":
                token_user_id = Token.objects.get(key=request_token[1]).only('user_id').user_id
                token_user = User.objects.get(id=token_user_id)
        except AttributeError:
            # Admin who does not include token, but is logged in can still use API
            token_user = request.user

        request_data_cleared = request.data
        # If file key is not present, serializer.is_valid() will detect it and return proper response
        if 'file' in request_data_cleared.keys():
            if 'type' in request_data_cleared.keys() and \
                    'expire_time' in request_data_cleared.keys():
                # Both fields won't be used directly by serializer. Instead they are used to mannualy
                # create required data
                del request_data_cleared['type']
                del request_data_cleared['expire_time']
            else:
                # Prepare error response informing about lack of specific required keys in the request
                error_response = {}
                if 'type' not in request_data_cleared.keys():
                    error_response['type'] = "This field is required."
                if 'expire_time' not in request_data_cleared.keys():
                    error_response['expire_time'] = "This field is required."
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        serializer = TimeLimitedImageSerializer(data=request_data_cleared, context={"request": request})

        if serializer.is_valid():
            queryset_permissions = APIUserProfile.objects.select_related('account_type') \
                .prefetch_related('account_type__custom_size').get(user=token_user)

            img_expire_time = request.POST.get('expire_time', '')
            img_type = request.POST.get('type', '')

            # Check permissions for creating time limited thumbnail and specific type of thumbnail
            custom_time_permission = queryset_permissions.account_type.create_time_limited_link_perm
            if img_type == '200':
                custom_size_permission = queryset_permissions.account_type.create_200px_thumbnail_perm
            elif img_type == '400':
                custom_size_permission = queryset_permissions.account_type.create_400px_thumbnail_perm
            else:
                related_custom_sizes = queryset_permissions.account_type.custom_size
                custom_size_permission = True
                if img_type not in related_custom_sizes:
                    custom_size_permission = False
            if custom_time_permission is False or custom_size_permission is False:
                error_msg = "Your profile type does not permit to create time limited or this type of thumbnail"
                return Response(error_msg, status=status.HTTP_403_FORBIDDEN)

            serializer.save(owner=token_user.apiuserprofile)

            source_image = StoredImage.objects.filter(owner=token_user.apiuserprofile).latest('id')

            options = {'size': (img_type, img_type), 'upscale': True, 'crop': True}
            img = get_thumbnailer(source_image.file).get_thumbnail(options)

            thumbnail = GeneratedImage.objects.create(source_image=source_image,
                                                      modified_image=img.url,
                                                      type=str(img_type),
                                                      expire_time=img_expire_time)

            response_thumbnails_data = {'thumbnails': {}}
            response_thumbnails_data['thumbnails'][str(img_type)] = request.get_host() + '/i/' + thumbnail.slug + '/'

            # Dictionary containing created thumbnails
            updated_serializer_data = serializer.data
            updated_serializer_data.update(response_thumbnails_data)

            return Response(updated_serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
