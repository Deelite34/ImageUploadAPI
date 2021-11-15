def user_directory_path(instance, filename):
    """
    Used for specifying unique for each user file path of
    stored files, using his ID number.
    Usable in a imagefield model field, in upload_to parameter.
    """
    return 'user_{0}/{1}'.format(instance.owner.user.id, filename)
