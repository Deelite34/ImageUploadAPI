from datetime import datetime
import pytz
from django.shortcuts import render
from django.views import View
from API.models import GeneratedImage


class DisplayImageView(View):
    def get(self, request, slug):
        """
        Displays uploaded image
        :param request:
        :param slug: string consisting or multiple random characters, identifying specific image to display
        """
        img = GeneratedImage.objects.get(slug=slug)
        image_path = img.modified_image

        # Check if image is expired
        utc = pytz.UTC
        expired = False
        if img.expire_date is not None:
            if img.expire_date.replace(tzinfo=utc) < datetime.now().replace(tzinfo=utc):
                expired = True

        context = {'image_path': image_path,
                   'expired': expired}
        return render(request, 'img/image.html', context=context)
