# Generated by Django 3.2.9 on 2021-11-14 14:18

from django.db import migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0009_alter_generatedimage_modified_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generatedimage',
            name='modified_image',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, upload_to='thumbnail/'),
        ),
    ]
