import os
import shutil
import pytest
from ImageUploadAPI.settings import TEST_API_DIR, TEST_MEDIA_DIR


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    """Move to /API/test directory  before tests start, to ensure access to test image file"""
    # Will be executed before the first test
    os.chdir(TEST_API_DIR)
    yield
    # Will be executed after the last test
    print('Cleaning up created test thumbnails..')
    folders = os.listdir(TEST_MEDIA_DIR)
    for folder in folders:
        directory = TEST_MEDIA_DIR + '/' + folder
        print("Removing: " + directory)
        shutil.rmtree(directory)
