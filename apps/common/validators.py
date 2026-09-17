"""Shared validators used across domain apps.

Image validation is centralized here so avatars (accounts) and product images
(catalog) enforce identical size and type rules without duplicating logic.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.utils.deconstruct import deconstructible


@deconstructible
class ImageFileValidator:
    """Validate an uploaded image's size and content type.

    Enforces the Tech Stack limits: max 5 MB and JPEG/PNG/WEBP only. Declared
    as ``@deconstructible`` so it can be attached to a model field and appear
    in migrations without breaking serialization.
    """

    def __init__(
        self,
        max_size: int | None = None,
        allowed_types: list[str] | None = None,
    ) -> None:
        self.max_size = max_size or settings.MAX_UPLOAD_SIZE
        self.allowed_types = allowed_types or settings.ALLOWED_IMAGE_TYPES

    def __call__(self, file: UploadedFile) -> None:
        # Size check.
        if file.size is not None and file.size > self.max_size:
            mb = self.max_size / (1024 * 1024)
            raise ValidationError(
                f"File too large. Maximum size is {mb:.0f} MB."
            )

        # Content-type check. ``content_type`` is advisory (client-supplied);
        # Pillow-based verification of actual image data happens in the form.
        content_type = getattr(file, "content_type", None)
        if content_type and content_type not in self.allowed_types:
            allowed = ", ".join(
                t.split("/")[-1].upper() for t in self.allowed_types
            )
            raise ValidationError(
                f"Unsupported file type. Allowed types: {allowed}."
            )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ImageFileValidator)
            and self.max_size == other.max_size
            and self.allowed_types == other.allowed_types
        )
