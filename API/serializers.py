from django.contrib.auth.models import User
from rest_framework import serializers

from API.models import StoredImage, APIUserProfile, AccountTypePermissions, GeneratedImage


class GeneratedImageSerializer(serializers.ModelSerializer):
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
    queryset = GeneratedImage.objects.all()
    thumbnails = GeneratedImageSerializer(queryset, many=True, read_only=True)

    class Meta:
        model = StoredImage
        fields = ['id', 'file', 'thumbnails']
        read_only_fields = ['id', 'thumbnails']
