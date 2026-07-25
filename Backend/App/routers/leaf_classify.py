import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from ..limiter import limiter

try:
    from ..models.leaf_classifier import classify
except ImportError:
    from models.leaf_classifier import classify

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@router.post("/leaf-classify")
@limiter.limit("10/minute")
async def leaf_classify(request: Request, file: UploadFile = File(...)):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds 10MB limit")

    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    is_valid_type = (file.content_type and file.content_type.startswith("image/")) or (file_ext in ALLOWED_EXTENSIONS)

    if not is_valid_type:
        raise HTTPException(status_code=400, detail="File must be an image (JPEG, PNG, BMP, WEBP)")

    try:
        image_bytes = await file.read()
        if len(image_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File size exceeds 10MB limit")

        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        result = classify(image_bytes)
        logger.info(f"Leaf image classified: {result['predicted_class']} ({result['confidence']:.2%})")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Leaf classification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")
