from API.models import StoredImage, APIUserProfile, GeneratedImage
from API.serializers import StoredImageSerializer, TimeLimitedImageSerializer
from API.utils import set_generated_image_model_slug_and_expire_date
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
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

    @extend_schema(  # drf-spectacular documentation extension
        responses={200: OpenApiTypes.OBJECT,
                   401: OpenApiTypes.OBJECT},
        examples=[OpenApiExample(
            "200 OK",
            description="Response when user sends get request.",
            value={"id": 0,
                   "file": "string",
                   "thumbnails": [
                       {
                           "id": 0,
                           "type": 350,
                           "image_url": "localhost:8000/i/qwertUbe9COTEy/",
                           "expire_date": "2021-12-01T16:44:19.723Z",
                           "created": "2021-12-01T16:44:19.723Z"
                       }
                   ]
                   },
            response_only=True,
            status_codes=["200"],
        ), OpenApiExample(
            "401 No authorization provided",
            description="Response when user does not provide token or jwt token in request header",
            value={"detail": "Authentication credentials were not provided."},
            response_only=True,
            status_codes=["401"],
        )]
    )
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

    @extend_schema(  # drf-spectacular documentation extension
        parameters=[
            OpenApiParameter(name='id', location=OpenApiParameter.PATH,
                             description='ID number of image passed trough url',
                             required=True)
        ],
        responses={201: OpenApiTypes.OBJECT,
                   401: OpenApiTypes.OBJECT,
                   404: OpenApiTypes.OBJECT,
                   },
        examples=[OpenApiExample(
            "request body",
            description="Attached file in file parameter must be an image of png or jpg type",
            value={"file": "attached file"},
            request_only=True,
        ), OpenApiExample(
            "201 thumbnail retrieved successfully",
            description="Response when user is owner of image and it does exist.",
            value={"id": 1,
                   "file": "http://localhost:8000/media/user_1/image_name.png",
                   "thumbnails": [
                       {
                           "id": 1,
                           "type": "200x200",
                           "image_url": "localhost:8000/i/qwertUbe9COTEy/",
                           "expire_date": "null",
                           "created": "2021-12-01T16:16:04.917572Z"
                       },
                       {
                           "id": 2,
                           "type": "400x400",
                           "image_url": "localhost:8000/i/qwertlH32N03SMm/",
                           "expire_date": "null",
                           "created": "2021-12-01T16:16:04.917618Z"
                       },
                       {
                           "id": 3,
                           "type": "840x680",
                           "image_url": "localhost:8000/i/qwertZ2Bg9zXp3M/",
                           "expire_date": "null",
                           "created": "2021-12-01T16:16:04.917646Z"
                       },
                       {
                           "id": 4,
                           "type": "500x500",
                           "image_url": "localhost:8000/i/qwerteAry621ywC/",
                           "expire_date": "null",
                           "created": "2021-12-01T16:16:04.917672Z"
                       },
                       {
                           "id": 5,
                           "type": "1000x1000",
                           "image_url": "localhost:8000/i/f2qwertnlboYlD1/",
                           "expire_date": "null",
                           "created": "2021-12-01T16:16:04.917696Z"
                       }
                   ]},
            response_only=True,
            status_codes=["201"],
        ), OpenApiExample(
            "401 No authorization provided",
            description="Response when user does not provide token or jwt token in request header",
            value={"detail": "Authentication credentials were not provided."},
            response_only=True,
            status_codes=["401"],
        ), OpenApiExample(
            "404 thumbnail not found",
            description="Response when image with id does not exist or is not owned by user.",
            value={"detail": "Item not found"},
            response_only=True,
            status_codes=["404"],
        )]
    )
    def retrieve(self, request, pk=None):
        """
        Lists specific uploaded image and related thumbnails if it exists, and user owns it.
        """
        try:
            # Normal user should include token or jwt token in his header
            request_token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')
            if request_token[0] == "Bearer":
                data = TokenBackend(algorithm='HS256').decode(request_token[1], verify=False)
                token_user_id = data['user_id']
            elif request_token[0] == "Token":
                token_user_id = Token.objects.get(key=request_token[1]).only('user_id').user_id
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

    @extend_schema(  # drf-spectacular documentation extension
        parameters=[
            OpenApiParameter(name='file', location=OpenApiParameter.QUERY, description='attached image',
                             required=True)
        ],
        responses={201: OpenApiTypes.OBJECT,
                   400: OpenApiTypes.OBJECT,
                   401: OpenApiTypes.OBJECT
                   },
        examples=[OpenApiExample(
            "request body",
            description="File must be an image of png or jpg type.",
            value={"file": "attached file"},
            request_only=True,
        ), OpenApiExample(
            "201 Thumbnail created",
            description="Example response when image(of size 840x680 is sent and thumbnails are created successfully",
            value={"id": 1,
                   "file": "http://localhost:8000/media/user_1/image_name.png",
                   "thumbnails": {
                       "200x200": "localhost:8000/i/qwertmDw5pmYm9O/",
                       "400x400": "localhost:8000/i/qwerte7EiCdMyAX/",
                       "840x680": "localhost:8000/i/qwertD58FxlnpLg/",
                       "500x500": "localhost:8000/i/qwert6mZc15bZap/",
                       "1000x1000": "localhost:8000/i/qwertAOGmWghPlz/"
                   }},
            response_only=True,
            status_codes=["201"],
        ), OpenApiExample(
            "400 No file parameter",
            description="Response when 'file' parameter is not included.",
            value={"file": [
                "No file was submitted."
            ]},
            response_only=True,
            status_codes=["400"],
        ), OpenApiExample(
            "401 No authorization provided",
            description="Response when user does not provide token or jwt token in request header",
            value={"detail": "Authentication credentials were not provided."},
            response_only=True,
            status_codes=["401"],
        )]
    )
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

    @extend_schema(  # drf-spectacular documentation extension
        parameters=[
            OpenApiParameter(name='file', location=OpenApiParameter.QUERY, description='attached image',
                             required=True),
            OpenApiParameter(name='type', location=OpenApiParameter.QUERY, description='integer',
                             required=True),
            OpenApiParameter(name='expire_time', location=OpenApiParameter.QUERY, description='integer',
                             required=True),
        ],
        responses={201: OpenApiTypes.OBJECT,
                   400: OpenApiTypes.OBJECT,
                   401: OpenApiTypes.OBJECT,
                   403: OpenApiTypes.OBJECT,
                   },
        examples=[OpenApiExample(
            "request body",
            description="File must be an image of png or jpg type, type is integer describing lenght of side of "
                        "square shaped thumbnail to be created, and expire_time is a value from 300 to 30000 "
                        "describing expiration time in seconds. ",
            value={"file": "attached file",
                   "type": "integer",
                   "expire_time": "integer"},
            request_only=True,
        ), OpenApiExample(
            "201 Thumbnail created",
            description="Example response when thumbnail gets created successfully.",
            value={"id": 1,
                   "file": "http://localhost:8000/media/user_1/image_name.png",
                   "thumbnails": {
                       "200": "localhost:8000/i/3PwncHZUWiZuCZr/"
                   }},
            response_only=True,
            status_codes=["201"],
        ), OpenApiExample(
            "400 No file parameter",
            description="Response when 'file' parameter is not included.",
            value={"file": [
                "No file was submitted."
            ]},
            response_only=True,
            status_codes=["400"],
        ), OpenApiExample(
            "400 No type or expire_time parameter",
            description="Response either or both 'type' or 'expire_time' parameters are not included.",
            value={"type": "This field is required.",
                   "expire_time": "This field is required."
                   },
            response_only=True,
            status_codes=["400"],
        ), OpenApiExample(
            "401 No authorization provided",
            description="Response when user does not provide token or jwt token in request header",
            value={"detail": "Authentication credentials were not provided."},
            response_only=True,
            status_codes=["401"],
        ), OpenApiExample(
            "403 Permission error",
            description="Response when user profile type is not allowed to create time limited thumbnails.",
            value={"error": "Your profile type does not permit to create time limited or this type of thumbnail"
                   },
            response_only=True,
            status_codes=["403"],
        )]
    )
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
                error_msg = {"error": "Your profile type does not have permission to create time limited or this type "
                                      "of thumbnail"
                             }
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
