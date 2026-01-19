from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import json

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio_analyzer import AudioAnalyzer
from advanced_mixer import AdvancedMixer
from music_extender import MusicExtender
from backend.auth import get_api_key

app = FastAPI(title="DJ Web Station API", version="1.0.0")

# CORS (Frontend 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시 ["http://localhost:3000"] 등으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 저장소 설정
UPLOAD_DIR = Path("temp_uploads")
OUTPUT_DIR = Path("temp_outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# 파일 유효기간 (초)
FILE_TTL = 600  # 10분

# --- Background Task: Auto Cleanup ---
async def cleanup_old_files():
    """오래된 파일 자동 삭제"""
    while True:
        try:
            now = asyncio.get_event_loop().time()
            # UPLOAD_DIR 청소
            for f in UPLOAD_DIR.glob("*"):
                if f.is_file() and (now - f.stat().st_mtime > FILE_TTL):
                    f.unlink()
                    print(f"🗑️ Cleaned up upload: {f.name}")
            
            # OUTPUT_DIR 청소
            for f in OUTPUT_DIR.glob("*"):
                if f.is_file() and (now - f.stat().st_mtime > FILE_TTL):
                    f.unlink()
                    print(f"🗑️ Cleaned up output: {f.name}")
                    
        except Exception as e:
            print(f"Cleanup error: {e}")
            
        await asyncio.sleep(60)  # 1분마다 체크

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_old_files())


# --- API Endpoints ---

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), api_key: str = Depends(get_api_key)):
    """오디오 파일 업로드"""
    file_id = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix
    file_path = UPLOAD_DIR / f"{file_id}{file_ext}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"file_id": file_id, "filename": file.filename, "message": "File uploaded successfully"}


@app.get("/api/analyze/{file_id}")
async def analyze_audio(file_id: str, api_key: str = Depends(get_api_key)):
    """오디오 분석 (BPM, Key 등)"""
    # 파일 찾기
    found_files = list(UPLOAD_DIR.glob(f"{file_id}.*"))
    if not found_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = str(found_files[0])
    
    try:
        analyzer = AudioAnalyzer(file_path)
        # 전체 분석 대신 빠른 분석 (tempo, key만)
        # analyze_full은 시간이 걸리므로 비동기 처리가 좋지만, 여기선 간단히 직접 호출
        result = analyzer.analyze_full()
        
        # NumPy 타입 등을 JSON 호환으로 변환
        return JSONResponse(content={
            "bpm": float(result['bpm']),
            "key": result['full_key'],
            "camelot": result['camelot'],
            "duration": float(result['duration']),
            "energy": float(result['avg_energy']),
            # segments 등 복잡한 데이터는 생략 또는 단순화
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from pydantic import BaseModel

class MixRequest(BaseModel):
    track_ids: List[str]
    transition_style: str = 'classic'

class ExtendRequest(BaseModel):
    file_id: str
    duration: str = '30m'

@app.post("/api/mix")
async def mix_tracks(
    request: MixRequest,
    api_key: str = Depends(get_api_key)
):
    """여러 트랙을 플레이리스트처럼 믹싱"""
    if not request.track_ids or len(request.track_ids) < 1:
        raise HTTPException(status_code=400, detail="At least one track ID is required")

    paths = []
    for tid in request.track_ids:
        found = list(UPLOAD_DIR.glob(f"{tid}.*"))
        if not found:
            raise HTTPException(status_code=404, detail=f"Track ID {tid} not found")
        paths.append(str(found[0]))
    
    output_id = str(uuid.uuid4())
    output_filename = f"mixed_{output_id}.mp3"
    output_path = str(OUTPUT_DIR / output_filename)
    
    try:
        mixer = AdvancedMixer()
        mixer.mix_playlist(
            paths, output_path,
            sync_beats=True,
            match_tempo=True,
            harmonic_mix=True,
            transition_bars=16,
            transition_style=request.transition_style,
            auto_detect=True
        )
        return {"output_id": output_id, "download_url": f"/api/download/{output_id}"}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Mixing failed: {str(e)}")


@app.post("/api/extend")
async def extend_track(
    request: ExtendRequest,
    api_key: str = Depends(get_api_key)
):
    """트랙(오디오/비디오) 무한 반복 확장"""
    files = list(UPLOAD_DIR.glob(f"{request.file_id}.*"))
    if not files:
        raise HTTPException(status_code=404, detail="File not found")
    path = str(files[0])
    
    # 확장자 유지 (비디오인 경우 mp4로 고정하거나 원본 유지)
    is_video = path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm'))
    ext = ".mp4" if is_video else ".mp3"
    
    output_id = str(uuid.uuid4())
    output_filename = f"extended_{output_id}{ext}"
    output_path = str(OUTPUT_DIR / output_filename)
    
    try:
        extender = MusicExtender()
        extender.extend_track(path, output_path, request.duration)
        return {"output_id": output_id, "download_url": f"/api/download/{output_id}"}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Extension failed: {str(e)}")


@app.get("/api/download/{output_id}")
async def download_result(output_id: str):
    """결과 파일 다운로드 (API Key 불필요 - 웹에서 직접 다운로드)"""
    # 보안상 API Key를 요구할 수도 있지만, 다운로드는 편리하게 허용
    files = list(OUTPUT_DIR.glob(f"*{output_id}*"))
    if not files:
        raise HTTPException(status_code=404, detail="File expired or not found")
        
    path = files[0]
    ext = path.suffix
    is_video = ext.lower() in ['.mp4', '.mov', '.avi']
    media_type = "video/mp4" if is_video else "audio/mpeg"
    
    return FileResponse(
        path, 
        media_type=media_type, 
        filename=f"dj_station_result{ext}"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
