import os
import io
from pathlib import Path
from tempfile import NamedTemporaryFile
import time
from typing import Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment

# 加載環境變量
load_dotenv()

# 獲取 OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 標準音頻模型和聲音選項
STANDARD_AUDIO_MODELS = [
    "tts-1",
    "tts-1-hd",
]
STANDARD_VOICES = [
    "alloy",
    "echo",
    "fable",
    "onyx",
    "nova",
    "shimmer",
]

# 創建 FastAPI 應用
app = FastAPI(
    title="TTS API",
    description="API for generating audio from text using OpenAI TTS",
    version="1.0.0"
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源，可以根據需要限制
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有方法
    allow_headers=["*"],  # 允許所有頭部
)

# 優化腳本處理 - 合併相同說話者連續文本
def optimize_script(script):
    lines = [line.strip() for line in script.splitlines() if line.strip()]
    optimized = []
    current_speaker = None
    current_text = ""
    
    for line in lines:
        if line.lower().startswith("speaker-1:"):
            speaker = "speaker-1"
            text = line.split(":", 1)[1].strip()
        elif line.lower().startswith("speaker-2:"):
            speaker = "speaker-2"
            text = line.split(":", 1)[1].strip()
        else:
            speaker = "speaker-1"  # 默認使用說話者1
            text = line
        
        # 如果說話者變了，保存之前的文本並開始新的
        if speaker != current_speaker and current_text:
            optimized.append((current_speaker, current_text))
            current_text = text
            current_speaker = speaker
        else:
            # 相同說話者，合併文本（加空格）
            if current_text:
                current_text += " " + text
            else:
                current_text = text
                current_speaker = speaker
                
    # 添加最後一個說話者的文本
    if current_text:
        optimized.append((current_speaker, current_text))
        
    return optimized

def get_mp3(text: str, voice: str, audio_model: str, api_key: str) -> bytes:
    """使用 OpenAI TTS API 生成音頻"""
    client = OpenAI(api_key=api_key)
    try:
        with client.audio.speech.with_streaming_response.create(
            model=audio_model,
            voice=voice,
            input=text,
        ) as response:
            with io.BytesIO() as file:
                for chunk in response.iter_bytes():
                    file.write(chunk)
                return file.getvalue()
    except Exception as e:
        print(f"Error generating audio: {e}")
        raise

def generate_audio_from_script(
    script: str,
    audio_api_key: str,
    audio_model: str = "tts-1",
    speaker1_voice: str = "onyx",
    speaker2_voice: str = "nova",
    volume_boost: float = 0,
) -> tuple[bytes, list]:
    """從腳本生成音頻，支持兩個說話者，並優化 API 調用"""
    combined_audio = b""
    status_log = []
    
    # 優化腳本處理
    optimized_script = optimize_script(script)
    
    # 處理每一段
    for speaker, text in optimized_script:
        voice_to_use = speaker1_voice if speaker == "speaker-1" else speaker2_voice
        status_log.append(f"[{speaker}] {text}")
        
        try:
            # 生成這一段的音頻
            audio_chunk = get_mp3(
                text,
                voice_to_use,
                audio_model,
                audio_api_key
            )
            combined_audio += audio_chunk
        except Exception as e:
            status_log.append(f"[錯誤] 無法生成音頻: {str(e)}")
            raise HTTPException(status_code=500, detail=f"無法生成音頻: {str(e)}")
    
    # 如果需要調整音量
    if volume_boost > 0:
        try:
            # 將二進制數據轉換為 AudioSegment
            with NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(combined_audio)
                temp_file_path = temp_file.name
            
            # 讀取音頻並調整音量
            audio = AudioSegment.from_mp3(temp_file_path)
            audio = audio + volume_boost  # 增加音量 (dB)
            
            # 將調整後的音頻轉換回二進制數據
            output = io.BytesIO()
            audio.export(output, format="mp3")
            combined_audio = output.getvalue()
            
            # 刪除臨時文件
            os.unlink(temp_file_path)
            
            status_log.append(f"[音量] 已增加 {volume_boost} dB")
        except Exception as e:
            status_log.append(f"[警告] 音量調整失敗: {str(e)}")
    
    return combined_audio, status_log

def save_audio_file(audio_data: bytes) -> str:
    """將音頻數據保存為臨時文件"""
    temp_dir = Path("./temp_audio")
    temp_dir.mkdir(exist_ok=True)
    # 清理舊文件
    for old_file in temp_dir.glob("*.mp3"):
        if old_file.stat().st_mtime < (time.time() - 24*60*60):  # 24小時前的文件
            old_file.unlink()
    # 創建新的臨時文件
    temp_file = NamedTemporaryFile(
        dir=temp_dir,
        delete=False,
        suffix=".mp3"
    )
    temp_file.write(audio_data)
    temp_file.close()
    return temp_file.name

# 定義請求模型
class TTSRequest(BaseModel):
    script: str
    api_key: Optional[str] = None
    model: Optional[str] = "tts-1"
    speaker1_voice: Optional[str] = "onyx"
    speaker2_voice: Optional[str] = "nova"
    volume_boost: Optional[float] = 6.0
    return_url: Optional[bool] = False

# API 端點
@app.post("/generate-audio")
async def generate_audio(request: TTSRequest):
    """
    生成音頻 API 端點
    
    - **script**: 腳本內容，格式為 "speaker-1: 文本" 或 "speaker-2: 文本"
    - **api_key**: OpenAI API Key (可選，如果未提供則使用環境變量)
    - **model**: 音頻模型 (可選，默認為 "tts-1")
    - **speaker1_voice**: 說話者1的聲音 (可選，默認為 "onyx")
    - **speaker2_voice**: 說話者2的聲音 (可選，默認為 "nova")
    - **volume_boost**: 音量增益 dB (可選，默認為 6.0)
    - **return_url**: 是否返回音頻文件的 URL (可選，默認為 False)
    """
    # 使用提供的 API Key 或環境變量中的 API Key
    api_key = request.api_key or OPENAI_API_KEY
    
    if not api_key:
        raise HTTPException(status_code=400, detail="未提供 OpenAI API Key")
    
    try:
        # 生成音頻
        audio_data, status_log = generate_audio_from_script(
            request.script,
            api_key,
            request.model,
            request.speaker1_voice,
            request.speaker2_voice,
            request.volume_boost
        )
        
        # 保存音頻文件
        audio_path = save_audio_file(audio_data)
        
        # 根據請求返回不同的響應
        if request.return_url:
            # 構建文件 URL (相對路徑)
            file_name = os.path.basename(audio_path)
            file_url = f"/audio/{file_name}"
            
            return {
                "status": "success",
                "message": "音頻生成成功",
                "audio_url": file_url,
                "logs": status_log
            }
        else:
            # 直接返回文件
            return FileResponse(
                audio_path,
                media_type="audio/mpeg",
                filename="generated_audio.mp3"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成音頻時發生錯誤: {str(e)}")

# 獲取音頻文件的端點
@app.get("/audio/{file_name}")
async def get_audio(file_name: str):
    """獲取生成的音頻文件"""
    file_path = Path(f"./temp_audio/{file_name}")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="音頻文件不存在")
    
    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename="generated_audio.mp3"
    )

# 獲取可用的音頻模型和聲音選項
@app.get("/options")
async def get_options():
    """獲取可用的音頻模型和聲音選項"""
    return {
        "models": STANDARD_AUDIO_MODELS,
        "voices": STANDARD_VOICES
    }

# 健康檢查端點
@app.get("/health")
async def health_check():
    """API 健康檢查"""
    return {"status": "healthy", "api_version": "1.0.0"}

# 主程序
if __name__ == "__main__":
    # 啟動 API 服務器
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)