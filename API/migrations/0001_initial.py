# Generated by Django 3.2.9 on 2021-11-09 13:41

import API.custom_validators
import API.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountTypePermissions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('create_200px_thumbnail_perm', models.BooleanField(default=False)),
                ('create_400px_thumbnail_perm', models.BooleanField(default=False)),
                ('create_original_img_link_perm', models.BooleanField(default=False)),
                ('create_time_limited_link_perm', models.BooleanField(default=False)),
                ('create_custom_sized_thumbnail_perm', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='APIUserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='API.accounttypepermissions')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CustomThumbnailSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(4096)])),
            ],
        ),
        migrations.CreateModel(
            name='StoredImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.ImageField(upload_to=API.models.user_directory_path, validators=[API.custom_validators.validate_image_type])),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.apiuserprofile')),
            ],
        ),
        migrations.CreateModel(
            name='GeneratedImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modified_image', sorl.thumbnail.fields.ImageField(upload_to=API.models.user_directory_path, validators=[API.custom_validators.validate_image_type])),
                ('slug', models.SlugField()),
                ('expire_time', models.IntegerField(blank=True, default=None, null=True, validators=[API.custom_validators.MinValueValidatorIgnoreNull(300), API.custom_validators.MaxValueValidatorIgnoreNull(30000)])),
                ('expire_date', models.DateTimeField(blank=True, null=True)),
                ('type', models.CharField(max_length=100)),
                ('created', models.DateTimeField(auto_now=True)),
                ('source_image', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='API.storedimage')),
            ],
        ),
        migrations.AddField(
            model_name='accounttypepermissions',
            name='custom_size',
            field=models.ManyToManyField(blank=True, default=None, to='API.CustomThumbnailSize'),
        ),
    ]
