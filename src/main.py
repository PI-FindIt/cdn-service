from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pathlib import Path
import os

app = FastAPI()

# Configuration
STATIC_DIR = Path("static")
STATIC_DIR.mkdir(parents=True, exist_ok=True)

def validate_file_path(file_path: str) -> Path:
    target_path = (STATIC_DIR / file_path).resolve()

    # Prevent directory traversal attacks
    if not target_path.is_relative_to(STATIC_DIR.resolve()):
        raise HTTPException(status_code=400, detail="Invalid file path")

    return target_path

@app.put("/files/{file_path:path}")
async def upload_file(file_path: str, file: UploadFile):
    try:
        target_path = validate_file_path(file_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Save file
        with target_path.open("wb") as buffer:
            content = await file.read()
            buffer.write(content)

        return {"message": "File uploaded successfully", "path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{file_path:path}")
async def get_file(file_path: str):
    try:
        target_path = validate_file_path(file_path)

        if not target_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(target_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/{file_path:path}")
async def delete_file(file_path: str):
    try:
        target_path = validate_file_path(file_path)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)