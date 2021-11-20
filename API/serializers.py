from django.contrib.auth.models import User
from rest_framework import serializers

from API.models import StoredImage, APIUserProfile, AccountTypePermissions, GeneratedImage


class GeneratedImageSerializer(serializers.ModelSerializer):
    """
    Helper serializer, used in StoredImageSerializer
    """
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = GeneratedImage
        fields = ['id', 'type', 'image_url', 'expire_date', 'created']

    def get_image_url(self, GeneratedImage):
        """ Gets urls for generated images"""
        request = self.context.get('request')
        slug = GeneratedImage.slug
        image_url = request.get_host() + '/i/' + slug + '/'
        return request.build_absolute_uri(image_url)


class StoredImageSerializer(serializers.ModelSerializer):
    """
    Displays info on all images and related thumbnails for specified user
    """
    queryset = GeneratedImage.objects.all()
    thumbnails = GeneratedImageSerializer(queryset, many=True, read_only=True)

    class Meta:
        model = StoredImage
        # TODO file field should not display file path, but either display different info, or not be displayed
        #      While accepting data if post request contains 'file' key and value
        fields = ['id', 'file', 'thumbnails']
        read_only_fields = ['id', 'thumbnails']



class TimeLimitedImageSerializer(serializers.ModelSerializer):
    """
    When user sends expire_time and type fields with other data to serializer, those fields are used only in
    the view, to generate specified thumbnails.
    """
    queryset = GeneratedImage.objects.all()
    expire_time = serializers.IntegerField(min_value=300, max_value=30000, read_only=True)
    type = serializers.IntegerField(min_value=50, max_value=4000, read_only=True)

    class Meta:
        model = StoredImage
        fields = ['id', 'file', 'type', 'expire_time']
        read_only_fields = ['id']
