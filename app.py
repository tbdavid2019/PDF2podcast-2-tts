import io
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
import time
import gradio as gr
from openai import OpenAI

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

def get_mp3(text: str, voice: str, audio_model: str, audio_api_key: str) -> bytes:
    """
    使用 OpenAI TTS API 生成音頻
    """
    client = OpenAI(api_key=audio_api_key)
    
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

def optimize_script(script_lines):
    """
    優化腳本處理 - 合併相同說話者的連續文本
    """
    optimized = []
    current_speaker = None
    current_voice = None
    current_text = ""
    
    for line in script_lines:
        line = line.strip()
        if not line:
            continue
            
        # 確定當前行的說話者和文本
        if line.lower().startswith("speaker-1:"):
            speaker = "speaker-1"
            text = line.split(":", 1)[1].strip()
        elif line.lower().startswith("speaker-2:"):
            speaker = "speaker-2"
            text = line.split(":", 1)[1].strip()
        else:
            speaker = "speaker-1"  # 預設使用說話者1
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

def generate_audio_from_script(
    script: str,
    audio_api_key: str,
    audio_model: str = "tts-1",
    speaker1_voice: str = "onyx",
    speaker2_voice: str = "nova",
) -> tuple[bytes, str]:
    """
    從腳本生成音頻，支援兩個說話者，並優化 API 調用
    """
    combined_audio = b""
    status_log = []
    
    # 優化腳本處理
    optimized_script = optimize_script(script.splitlines())
    
    # 處理每一段
    for speaker, text in optimized_script:
        voice_to_use = speaker1_voice if speaker == "speaker-1" else speaker2_voice
        status_log.append(f"[{'說話者1' if speaker == 'speaker-1' else '說話者2'}] {text}")
        
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
    
    return combined_audio, "\n".join(status_log)

def save_audio_file(audio_data: bytes) -> str:
    """
    將音頻數據保存為臨時檔案
    """
    temp_dir = Path("./temp_audio")
    temp_dir.mkdir(exist_ok=True)
    
    # 清理舊檔案
    for old_file in temp_dir.glob("*.mp3"):
        if old_file.stat().st_mtime < (time.time() - 24*60*60):  # 24小時前的檔案
            old_file.unlink()
    
    # 創建新的臨時檔案
    temp_file = NamedTemporaryFile(
        dir=temp_dir,
        delete=False,
        suffix=".mp3"
    )
    
    temp_file.write(audio_data)
    temp_file.close()
    
    return temp_file.name

# Gradio 介面
def create_gradio_interface():
    with gr.Blocks(title="TTS Generator", css="""
        #header { text-align: center; margin-bottom: 20px; }
    """) as demo:
        gr.Markdown("# 語音合成器 | TTS Generator", elem_id="header")
        
        with gr.Row():
            with gr.Column(scale=1):
                # 輸入區
                script_input = gr.Textbox(
                    label="輸入腳本 | Input Script",
                    placeholder="""請貼上腳本內容，格式如下：
speaker-1: 歡迎來到 David888 Podcast，我是 David...
speaker-2: 大家好，我是 Cordelia...
沒有標記說話者的行會預設使用說話者1的聲音。

提示：相同說話者的連續文本將自動合併處理，提高生成效率。""",
                    lines=20
                )
                
                api_key = gr.Textbox(
                    label="OpenAI API Key",
                    type="password"
                )
                
                with gr.Row():
                    audio_model = gr.Dropdown(
                        label="音頻模型 | Audio Model",
                        choices=STANDARD_AUDIO_MODELS,
                        value="tts-1"
                    )
                    
                    speaker1_voice = gr.Dropdown(
                        label="說話者1聲音 | Speaker 1 Voice",
                        choices=STANDARD_VOICES,
                        value="onyx"
                    )
                    
                    speaker2_voice = gr.Dropdown(
                        label="說話者2聲音 | Speaker 2 Voice",
                        choices=STANDARD_VOICES,
                        value="nova"
                    )
                
                generate_button = gr.Button("生成音頻 | Generate Audio")
            
            with gr.Column(scale=1):
                # 輸出區
                audio_output = gr.Audio(
                    label="生成的音頻 | Generated Audio",
                    type="filepath"
                )
                
                status_output = gr.Textbox(
                    label="生成狀態 | Generation Status",
                    lines=20,
                    show_copy_button=True
                )
        
        # 事件處理
        generate_button.click(
            fn=lambda script, key, model, v1, v2: process_and_save_audio(
                script, key, model, v1, v2
            ),
            inputs=[
                script_input,
                api_key,
                audio_model,
                speaker1_voice,
                speaker2_voice
            ],
            outputs=[audio_output, status_output]
        )
    
    return demo

def process_and_save_audio(script, api_key, model, voice1, voice2):
    """
    處理音頻生成並保存檔案
    """
    try:
        audio_data, status_log = generate_audio_from_script(
            script,
            api_key,
            model,
            voice1,
            voice2
        )
        
        audio_path = save_audio_file(audio_data)
        return audio_path, status_log
    
    except Exception as e:
        error_message = f"生成音頻時發生錯誤: {str(e)}"
        print(error_message)
        return None, error_message

if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch()