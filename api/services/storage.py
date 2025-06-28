from io import BytesIO
import os
from pathlib import Path
import tempfile
from imagekitio import ImageKit
from api.core.config import settings
from typing import List
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

imagekit = ImageKit(
    private_key=settings.IMAGEKIT_PRIVATE_KEY,
    public_key=settings.IMAGEKIT_PUBLIC_KEY,
    url_endpoint=settings.IMAGEKIT_URL_ENDPOINT,
)

PUBLIC_FOLDER = "public/uploads"


async def upload_files(files: List[UploadFile]) -> List[str]:
    urls = []
    for file in files:
        result = upload_file(file=file)
        urls.append(result)
    return urls


async def upload_file(file: UploadFile) -> str:
    # Ensure public folder exists
    os.makedirs(PUBLIC_FOLDER, exist_ok=True)

    # Create temp file in public folder
    temp_suffix = Path(file.filename).suffix  # Preserve original extension
    with tempfile.NamedTemporaryFile(
        dir=PUBLIC_FOLDER,
        suffix=temp_suffix,
        delete=False,  # We'll handle deletion manually
    ) as tmp:
        # Write content
        content = await file.read()
        tmp.write(content)
        temp_path = tmp.name

    try:
        # Upload to ImageKit
        with open(temp_path, "rb") as f:
            result = imagekit.upload_file(file=f, file_name=file.filename)

        # Option 1: Keep the file in public folder (return both URLs)
        public_url = f"/uploads/{os.path.basename(temp_path)}"

        # Option 2: Delete after upload (recommended)
        os.unlink(temp_path)

        return result.url

    except Exception as e:
        # Clean up on error
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise


async def delete_files(urls: List[str]):
    for url in urls:
        imagekit.delete_file(url)
