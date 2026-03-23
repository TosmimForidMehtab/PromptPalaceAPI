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
    private_key=settings.IMAGEKIT_PRIVATE_KEY
)

PUBLIC_FOLDER = "public/uploads"


async def upload_files(files: List[UploadFile]) -> List[str]:
    urls = []
    for file in files:
        result = upload_file(file=file)
        urls.append(result)
    return urls


async def upload_file(file: UploadFile) -> str:
    try:
        # 1. Read the file directly into memory
        content = await file.read()

        # 2. Upload directly to ImageKit using the new SDK syntax
        result = imagekit.files.upload(
            file=content, 
            file_name=file.filename
        )
        
        # result.url contains the public URL provided by ImageKit
        return result.url

    except Exception as e:
        logger.error(f"ImageKit upload failed: {e}")
        raise


async def delete_files(urls: List[str]):
    for url in urls:
        imagekit.delete_file(url)
