import uuid
from io import BytesIO
# from pathlib import Path # Used in local storage mode in disk

from PIL import Image, ImageOps

import boto3
from starlette.concurrency import run_in_threadpool

from config import settings

# PROFILE_PICS_DIR = Path("media/profile_pics") # Used in local storage mode in disk


def _get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.s3_region,
        aws_access_key_id=(
            settings.s3_access_key_id.get_secret_value()
            if settings.s3_access_key_id
            else None
        ),
        aws_secret_access_key=(
            settings.s3_secret_access_key.get_secret_value()
            if settings.s3_secret_access_key
            else None
        ),
        endpoint_url=settings.s3_endpoint_url,
    )

# Used in local storage mode in disk
# def process_profile_image(content: bytes) -> str:
#     """local storage in disk version"""
#     with Image.open(BytesIO(content)) as original:
#         img = ImageOps.exif_transpose(original)  # Fixes orientation issues
#
#         # img arg: Resizes and crops it and maintain size ratio
#         img = ImageOps.fit(img, (300, 300), method=Image.Resampling.LANCZOS)
#
#         if img.mode in ("RGBA", "LA", "P"):
#             img = img.convert("RGB") # PNG supports transparency but JPEG does not
#
#         # Unique naming for security reasons and also avoids filename collisions
#         # Convert it to jpg
#         filename = f"{uuid.uuid4().hex}.jpg"
#         filepath = PROFILE_PICS_DIR / filename
#
#         PROFILE_PICS_DIR.mkdir(parents=True, exist_ok=True)
#
#         img.save(filepath, "JPEG", quality=85, optimize=True)
#
#     return filename  # this will be stored in DB


def process_profile_image(content: bytes) -> tuple[bytes, str]:
    """decoupled from the filesystem version"""
    with Image.open(BytesIO(content)) as original:
        img = ImageOps.exif_transpose(original)  # Fixes orientation issues

        # img arg: Resizes and crops it and maintain size ratio
        img = ImageOps.fit(img, (300, 300), method=Image.Resampling.LANCZOS)

        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB") # PNG supports transparency but JPEG does not

        # Unique naming for security reasons and also avoids filename collisions
        # Convert it to jpg
        filename = f"{uuid.uuid4().hex}.jpg"

        output = BytesIO()
        img.save(output, "JPEG", quality=85, optimize=True)
        output.seek(0) # rewinds back to the beginning of the byte stream so that we can read it

    return output.read(), filename  # this will be stored in DB


# Used in local storage mode in disk
# def delete_profile_image(filename: str | None) -> None:
#     """local storage in disk version"""
#     if filename is None:
#         return
#
#     filepath = PROFILE_PICS_DIR / filename
#     if filepath.exists():
#         filepath.unlink()

def _upload_to_s3(file_bytes: bytes, key: str) -> None:
    s3 = _get_s3_client()
    s3.upload_fileobj(
        BytesIO(file_bytes),
        settings.s3_bucket_name,
        key,
        ExtraArgs={"ContentType": "image/jpeg"}, # Tells the browser to not download imge instead it should display them
    )


def _delete_from_s3(key: str) -> None:
    s3 = _get_s3_client()
    s3.delete_object(Bucket=settings.s3_bucket_name, Key=key)


async def upload_profile_image(file_bytes: bytes, filename: str) -> None:
    key = f"profile_pics/{filename}"
    await run_in_threadpool(_upload_to_s3, file_bytes, key)


async def delete_profile_image(filename: str | None) -> None:
    if filename is None:
        return
    key = f"profile_pics/{filename}"
    await run_in_threadpool(_delete_from_s3, key)
