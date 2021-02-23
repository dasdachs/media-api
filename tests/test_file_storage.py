import os

import pytest

from app.file_storage import clean_up


class MockFs:
    @staticmethod
    def listdir():
        return ["1.txt", "2.txt", "3.txt"]

    @staticmethod
    def remove():
        return


@pytest.fixture
def mock_setting(monkeypatch):
    monkeypatch.setenv("FILE_STORAGE", "tmp")
    monkeypatch.setenv("UPLOADED_FILES_DIR", "uploaded")
    monkeypatch.setenv("TRANSFORMED_FILES_DIR", "transformed")
    monkeypatch.setenv("API_KEY", "super_secret_key")


@pytest.fixture
def mock_os(monkeypatch):
    def mock_list(*args, **kwargs):
        return MockFs.listdir()

    def mock_remove(*args, **kwargs):
        return MockFs.remove()

    monkeypatch.setattr(os, "listdir", mock_list)
    monkeypatch.setattr(os, "remove", mock_remove)


def test_clean_up_single_file(mock_os):
    """Create and cleanup single file"""
    assert clean_up("test.txt") == 1


def test_clean_up_multiple_files(mock_os):
    """Create and cleanup single file"""
    assert clean_up() == 3


# @pytest.mark.asyncio
# def test_save_uploaded_file():
#     """Tests that uploaded files get saved correctly"""
#     file = UploadFile("test.txt")
