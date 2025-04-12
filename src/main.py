from enum import Enum

from fastapi import FastAPI, HTTPException, UploadFile, APIRouter
from fastapi.responses import FileResponse
from pathlib import Path
import os

app = FastAPI()

router = APIRouter(prefix="/cdn", tags=["CDN"])

# Configuration
STATIC_DIR = Path("static")
STATIC_DIR.mkdir(parents=True, exist_ok=True)


class FilePathType(Enum):
    SUPERMARKET = "supermarket"
    PRODUCT = "product"
    USER = "user"


def validate_file_path(file_type: FilePathType, path: str) -> Path:
    target_path = (STATIC_DIR / file_type.name / path).resolve()

    # Prevent directory traversal attacks
    if not target_path.is_relative_to(STATIC_DIR.resolve()):
        raise HTTPException(status_code=400, detail="Invalid file path")

    return target_path


@router.post("/{file_type}/{path}")
async def upload_file(file_type: FilePathType, path: str, file: UploadFile) -> dict:
    try:
        target_path = validate_file_path(file_type, path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with target_path.open("wb") as buffer:
            content = await file.read()
            buffer.write(content)

        return {
            "message": "File uploaded successfully",
            "path": f"cdn/{file_type}/{path}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_type}/{path}")
async def get_file(file_type: FilePathType, path: str) -> FileResponse:
    try:
        target_path = validate_file_path(file_type, path)

        if not target_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(target_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{file_type}/{path}")
async def delete_file(file_type: FilePathType, path: str) -> dict:
    try:
        target_path = validate_file_path(file_type, path)

        if not target_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        target_path.unlink()

        # Clean up empty directories
        current_dir = target_path.parent
        while current_dir != STATIC_DIR and not os.listdir(current_dir):
            current_dir.rmdir()
            current_dir = current_dir.parent

        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(router)
