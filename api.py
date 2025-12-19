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
import requests
import boto3
from google import genai

# 加載環境變量
load_dotenv()

# 獲取 API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")

# 標準音頻模型和聲音選項
STANDARD_AUDIO_MODELS = [
    "gpt-4o-mini-tts",
    "gpt-4o-audio-preview",
    "tts-1",
    "tts-1-hd",
]
STANDARD_VOICES = [
    "alloy", "echo", "fable", "onyx", 
    "nova", "shimmer", "coral", "sage",
]
GEMINI_VOICES = [
    "Puck", "Charon", "Kore", 
    "Fenrir", "Aoede", "Alnilam", "Algieba"
]
POLLY_VOICES = ["Zhiyu"]
TAI_TTS_MODELS = ["model6"]
TAI_TTS_URL = "https://learn-language.tokyo/taiwanesettsapi/"

# 創建 FastAPI 應用
app = FastAPI(
    title="多語言 TTS API",
    description="支援 OpenAI、Gemini、AWS Polly、台語 TTS 的語音合成 API",
    version="2.0.0"
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

def get_mp3(text: str, voice: str, audio_model: str, api_key: str, instructions: str = None) -> bytes:
    """使用 OpenAI TTS API 生成音頻"""
    MAX_TEXT_LENGTH = 1000
    
    client = OpenAI(api_key=api_key)
    
    # 如果文本長度超過限制，分割文本
    if len(text) > MAX_TEXT_LENGTH:
        print(f"Text too long ({len(text)} chars), splitting into chunks")
        text_chunks = []
        for i in range(0, len(text), MAX_TEXT_LENGTH):
            text_chunks.append(text[i:i + MAX_TEXT_LENGTH])
        
        combined_audio = b""
        for chunk in text_chunks:
            try:
                api_params = {
                    "model": audio_model,
                    "voice": voice,
                    "input": chunk,
                }
                if instructions:
                    api_params["instructions"] = instructions
                
                with client.audio.speech.with_streaming_response.create(**api_params) as response:
                    with io.BytesIO() as file:
                        for audio_chunk in response.iter_bytes():
                            file.write(audio_chunk)
                        combined_audio += file.getvalue()
            except Exception as e:
                print(f"Error generating audio for chunk: {e}")
                raise
        
        return combined_audio
    else:
        try:
            api_params = {
                "model": audio_model,
                "voice": voice,
                "input": text,
            }
            if instructions:
                api_params["instructions"] = instructions
            
            with client.audio.speech.with_streaming_response.create(**api_params) as response:
                with io.BytesIO() as file:
                    for chunk in response.iter_bytes():
                        file.write(chunk)
                    return file.getvalue()
        except Exception as e:
            print(f"Error generating audio: {e}")
            raise

def get_gemini_pcm(text: str, voice: str, api_key: str) -> bytes:
    """使用 Gemini TTS API 生成音頻"""
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=text,
            config={
                'speech_config': {
                    'voice_config': {
                        'prebuilt_voice_config': {
                            'voice_name': voice
                        }
                    }
                }
            }
        )
        
        # 提取音頻數據
        pcm_data = b''
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                pcm_data += part.inline_data.data
        
        if not pcm_data:
            raise ValueError("未從 Gemini API 收到音頻數據")
        
        return pcm_data
    except Exception as e:
        print(f"Gemini TTS 錯誤: {e}")
        raise

def get_polly_mp3(text: str, voice: str, api_key: str, secret_key: str, region: str) -> bytes:
    """使用 AWS Polly 生成音頻"""
    try:
        polly = boto3.client(
            'polly',
            aws_access_key_id=api_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId=voice,
            Engine='neural'
        )
        
        audio_data = response['AudioStream'].read()
        return audio_data
    except Exception as e:
        print(f"AWS Polly 錯誤: {e}")
        raise

def get_tai_tts_mp3(text: str, model: str) -> bytes:
    """使用台語 TTS API 生成音頻"""
    try:
        # Step 1: 發送 POST 請求獲取 JSON 響應
        response = requests.post(
            TAI_TTS_URL,
            json={"text": text, "model": model},
            timeout=60
        )
        response.raise_for_status()
        
        # Step 2: 從 JSON 響應中獲取 audio_url
        json_data = response.json()
        audio_url = json_data.get("audio_url")
        
        if not audio_url:
            raise ValueError("台語 TTS API 未返回 audio_url")
        
        # Step 3: 下載 WAV 文件
        audio_response = requests.get(audio_url, timeout=60)
        audio_response.raise_for_status()
        
        return audio_response.content
    except Exception as e:
        print(f"台語 TTS 錯誤: {e}")
        raise

def generate_audio_from_script(
    script: str,
    provider: str = "openai",
    # OpenAI 參數
    audio_api_key: str = None,
    audio_model: str = "gpt-4o-mini-tts",
    speaker1_voice: str = "onyx",
    speaker2_voice: str = "nova",
    speaker1_instructions: str = "保持活潑愉快的語氣",
    speaker2_instructions: str = "保持活潑愉快的語氣",
    # Gemini 參數
    gemini_api_key: str = None,
    gemini_male_voice: str = "Puck",
    gemini_female_voice: str = "Aoede",
    # AWS Polly 參數
    aws_access_key: str = None,
    aws_secret_key: str = None,
    aws_region: str = "ap-northeast-1",
    polly_voice: str = "Zhiyu",
    # 台語 TTS 參數
    tai_model: str = "model6",
    # 通用參數
    volume_boost: float = 0,
) -> tuple[bytes, list]:
    """從腳本生成音頻，支持多個 TTS provider"""
    status_log = []
    
    # 優化腳本處理
    optimized_script = optimize_script(script)
    
    # 使用 pydub 處理音頻合併
    combined_segment = None
    
    # 處理每一段
    for speaker, text in optimized_script:
        status_log.append(f"[{speaker}] {text}")
        
        try:
            audio_chunk = None
            
            # 根據 provider 生成音頻
            if provider == "openai":
                if not audio_api_key:
                    raise ValueError("缺少 OpenAI API Key")
                voice = speaker1_voice if speaker == "speaker-1" else speaker2_voice
                instructions = speaker1_instructions if speaker == "speaker-1" else speaker2_instructions
                audio_chunk = get_mp3(text, voice, audio_model, audio_api_key, instructions)
                audio_format = "mp3"
                
            elif provider == "gemini":
                if not gemini_api_key:
                    raise ValueError("缺少 Gemini API Key")
                voice = gemini_male_voice if speaker == "speaker-1" else gemini_female_voice
                audio_chunk = get_gemini_pcm(text, voice, gemini_api_key)
                audio_format = "raw"
                
            elif provider == "polly":
                if not aws_access_key or not aws_secret_key:
                    raise ValueError("缺少 AWS 憑證")
                audio_chunk = get_polly_mp3(text, polly_voice, aws_access_key, aws_secret_key, aws_region)
                audio_format = "mp3"
                
            elif provider == "taiwanese":
                audio_chunk = get_tai_tts_mp3(text, tai_model)
                audio_format = "wav"
                
            else:
                raise ValueError(f"不支援的 provider: {provider}")
            
            # 將音頻轉換為 AudioSegment
            with NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as temp_file:
                temp_file.write(audio_chunk)
                temp_file_path = temp_file.name
            
            # 根據格式讀取音頻
            if audio_format == "mp3":
                chunk_segment = AudioSegment.from_mp3(temp_file_path)
            elif audio_format == "wav":
                chunk_segment = AudioSegment.from_wav(temp_file_path)
            elif audio_format == "raw":
                # Gemini 返回 24kHz 單聲道 PCM
                chunk_segment = AudioSegment(
                    data=audio_chunk,
                    sample_width=2,
                    frame_rate=24000,
                    channels=1
                )
                os.unlink(temp_file_path)
                temp_file_path = None
            
            # 刪除臨時文件
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            
            # 合併音頻段
            if combined_segment is None:
                combined_segment = chunk_segment
            else:
                combined_segment += chunk_segment
                
        except Exception as e:
            status_log.append(f"[錯誤] 無法生成音頻: {str(e)}")
            raise HTTPException(status_code=500, detail=f"無法生成音頻: {str(e)}")
    
    # 如果沒有生成任何音頻段
    if combined_segment is None:
        status_log.append("[錯誤] 沒有生成任何音頻")
        return b"", status_log
    
    # 如果需要調整音量
    if volume_boost > 0:
        try:
            combined_segment = combined_segment + volume_boost
            status_log.append(f"[音量] 已增加 {volume_boost} dB")
        except Exception as e:
            status_log.append(f"[警告] 音量調整失敗: {str(e)}")
    
    # 將 AudioSegment 轉換為二進制數據
    output = io.BytesIO()
    combined_segment.export(output, format="mp3")
    combined_audio = output.getvalue()
    
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
    provider: Optional[str] = "openai"  # openai, gemini, polly, taiwanese
    
    # OpenAI 參數
    api_key: Optional[str] = None
    model: Optional[str] = "gpt-4o-mini-tts"
    speaker1_voice: Optional[str] = "onyx"
    speaker2_voice: Optional[str] = "nova"
    speaker1_instructions: Optional[str] = "保持活潑愉快的語氣"
    speaker2_instructions: Optional[str] = "保持活潑愉快的語氣"
    
    # Gemini 參數
    gemini_api_key: Optional[str] = None
    gemini_male_voice: Optional[str] = "Puck"
    gemini_female_voice: Optional[str] = "Aoede"
    
    # AWS Polly 參數
    aws_access_key: Optional[str] = None
    aws_secret_key: Optional[str] = None
    aws_region: Optional[str] = "ap-northeast-1"
    polly_voice: Optional[str] = "Zhiyu"
    
    # 台語 TTS 參數
    tai_model: Optional[str] = "model6"
    
    # 通用參數
    volume_boost: Optional[float] = 6.0
    return_url: Optional[bool] = False

# API 端點
@app.post("/generate-audio")
async def generate_audio(request: TTSRequest):
    """
    生成音頻 API 端點
    
    支援 4 種 TTS Provider:
    - **openai**: OpenAI TTS (需 api_key)
    - **gemini**: Google Gemini TTS (需 gemini_api_key)
    - **polly**: AWS Polly (需 aws_access_key, aws_secret_key)
    - **taiwanese**: 台語 TTS (免費，無需金鑰)
    
    通用參數:
    - **script**: 腳本內容，格式為 "speaker-1: 文本" 或 "speaker-2: 文本"
    - **provider**: TTS 服務商 (預設: openai)
    - **volume_boost**: 音量增益 dB (預設: 6.0)
    - **return_url**: 是否返回音頻 URL (預設: False)
    """
    # 根據 provider 獲取相應的 API Key
    if request.provider == "openai":
        api_key = request.api_key or OPENAI_API_KEY
        if not api_key:
            raise HTTPException(status_code=400, detail="未提供 OpenAI API Key")
    elif request.provider == "gemini":
        gemini_key = request.gemini_api_key or GEMINI_API_KEY
        if not gemini_key:
            raise HTTPException(status_code=400, detail="未提供 Gemini API Key")
    elif request.provider == "polly":
        aws_key = request.aws_access_key or AWS_ACCESS_KEY_ID
        aws_secret = request.aws_secret_key or AWS_SECRET_ACCESS_KEY
        if not aws_key or not aws_secret:
            raise HTTPException(status_code=400, detail="未提供 AWS 憑證")
    # taiwanese 不需要 API Key
    
    try:
        # 生成音頻
        audio_data, status_log = generate_audio_from_script(
            script=request.script,
            provider=request.provider,
            # OpenAI
            audio_api_key=request.api_key or OPENAI_API_KEY,
            audio_model=request.model,
            speaker1_voice=request.speaker1_voice,
            speaker2_voice=request.speaker2_voice,
            speaker1_instructions=request.speaker1_instructions,
            speaker2_instructions=request.speaker2_instructions,
            # Gemini
            gemini_api_key=request.gemini_api_key or GEMINI_API_KEY,
            gemini_male_voice=request.gemini_male_voice,
            gemini_female_voice=request.gemini_female_voice,
            # AWS Polly
            aws_access_key=request.aws_access_key or AWS_ACCESS_KEY_ID,
            aws_secret_key=request.aws_secret_key or AWS_SECRET_ACCESS_KEY,
            aws_region=request.aws_region,
            polly_voice=request.polly_voice,
            # 台語
            tai_model=request.tai_model,
            # 通用
            volume_boost=request.volume_boost,
        )
        
        # 保存音頻文件
        audio_path = save_audio_file(audio_data)
        
        # 根據請求返回不同的響應
        if request.return_url:
            file_name = os.path.basename(audio_path)
            file_url = f"/audio/{file_name}"
            
            return {
                "status": "success",
                "message": "音頻生成成功",
                "provider": request.provider,
                "audio_url": file_url,
                "logs": status_log
            }
        else:
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
    """獲取所有 TTS provider 的可用選項"""
    return {
        "providers": ["openai", "gemini", "polly", "taiwanese"],
        "openai": {
            "models": STANDARD_AUDIO_MODELS,
            "voices": STANDARD_VOICES
        },
        "gemini": {
            "voices": GEMINI_VOICES
        },
        "polly": {
            "voices": POLLY_VOICES
        },
        "taiwanese": {
            "models": TAI_TTS_MODELS
        }
    }

# 健康檢查端點
@app.get("/health")
async def health_check():
    """API 健康檢查"""
    return {
        "status": "healthy", 
        "api_version": "2.0.0",
        "supported_providers": ["openai", "gemini", "polly", "taiwanese"]
    }

# 主程序
if __name__ == "__main__":
    # 啟動 API 服務器
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)