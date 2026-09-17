"""Tests for the shared ImageFileValidator."""

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.common.validators import ImageFileValidator


class _FakeFile:
    """Minimal stand-in exposing size and content_type."""

    def __init__(self, size, content_type):
        self.size = size
        self.content_type = content_type


class TestImageFileValidator:
    def test_accepts_valid_image(self):
        validator = ImageFileValidator()
        # 1 MB JPEG — under the 5 MB limit, allowed type.
        validator(_FakeFile(1 * 1024 * 1024, "image/jpeg"))

    def test_rejects_oversized_file(self):
        validator = ImageFileValidator()
        with pytest.raises(ValidationError, match="too large"):
            validator(_FakeFile(6 * 1024 * 1024, "image/png"))

    def test_rejects_unsupported_type(self):
        validator = ImageFileValidator()
        with pytest.raises(ValidationError, match="Unsupported file type"):
            validator(_FakeFile(1024, "application/pdf"))

    def test_custom_limits(self):
        validator = ImageFileValidator(
            max_size=1024, allowed_types=["image/webp"]
        )
        validator(_FakeFile(500, "image/webp"))
        with pytest.raises(ValidationError):
            validator(_FakeFile(2048, "image/webp"))

    def test_equality_for_migration_stability(self):
        # Deconstructible validators must compare equal to avoid spurious
        # migrations.
        assert ImageFileValidator() == ImageFileValidator()

    def test_accepts_real_uploaded_file_object(self):
        validator = ImageFileValidator()
        upload = SimpleUploadedFile(
            "a.png", b"\x89PNG\r\n", content_type="image/png"
        )
        validator(upload)
