from django.shortcuts import render
from django.views import View

from API.models import GeneratedImage


class DisplayImageView(View):
    def get(self, request, slug):
        img = GeneratedImage.objects.get(slug=slug)
        image = img.modified_image
        context = {'img': image}
        return render(request, 'img/image.html', context=context)
