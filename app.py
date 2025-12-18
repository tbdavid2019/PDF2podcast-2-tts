import io
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
import time
import gradio as gr
from openai import OpenAI
from pydub import AudioSegment
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()

# 獲取 OpenAI API Key (如果在環境變量中設置了)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# 標準音頻模型和聲音選項
STANDARD_AUDIO_MODELS = [
    "gpt-4o-mini-tts",
    "gpt-4o-audio-preview",
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
    "coral",
    "sage",
]

# 優化腳本處理 - 合並相同說話者連續文本
def optimize_script(script):
    print("🔄 開始優化腳本處理...")
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
            # 相同說話者，合並文本（加空格）
            if current_text:
                current_text += " " + text
            else:
                current_text = text
                current_speaker = speaker
                
    # 添加最後一個說話者的文本
    if current_text:
        optimized.append((current_speaker, current_text))
        
    print(f"✅ 腳本優化完成，共 {len(optimized)} 段對話")
    return optimized

def get_mp3(text: str, voice: str, audio_model: str, audio_api_key: str, instructions: str = None) -> bytes:
    """使用 OpenAI TTS API 生成音頻"""
    print(f"🎤 開始生成音頻: 長度 {len(text)} 字符, 聲音: {voice}, 模型: {audio_model}")
    
    # 檢查文本長度，OpenAI TTS API 有 4096 個標記的限制
    # 大約 1000 個漢字約等於 2000-3000 個標記，為安全起見，我們將限制設為 1000 個字符
    MAX_TEXT_LENGTH = 1000
    
    client = OpenAI(api_key=audio_api_key)
    
    # 如果文本長度超過限制，分割文本
    if len(text) > MAX_TEXT_LENGTH:
        print(f"📝 文本過長 ({len(text)} 字符)，分割成多個區塊")
        # 將文本分割成更小的塊
        text_chunks = []
        for i in range(0, len(text), MAX_TEXT_LENGTH):
            text_chunks.append(text[i:i + MAX_TEXT_LENGTH])
        
        print(f"📦 共分割成 {len(text_chunks)} 個區塊")
        
        # 為每個塊生成音頻並合並
        combined_audio = b""
        for i, chunk in enumerate(text_chunks, 1):
            print(f"🔄 處理區塊 {i}/{len(text_chunks)}: {len(chunk)} 字符")
            try:
                # 構建 API 參數
                api_params = {
                    "model": audio_model,
                    "voice": voice,
                    "input": chunk,
                }
                if instructions:
                    api_params["instructions"] = instructions
                    print(f"💬 使用語氣指示: {instructions}")
                
                print(f"📡 調用 OpenAI TTS API...")
                with client.audio.speech.with_streaming_response.create(**api_params) as response:
                    with io.BytesIO() as file:
                        for audio_chunk in response.iter_bytes():
                            file.write(audio_chunk)
                        chunk_audio = file.getvalue()
                        combined_audio += chunk_audio
                        print(f"✅ 區塊 {i} 生成完成: {len(chunk_audio)} bytes")
            except Exception as e:
                print(f"❌ 區塊 {i} 生成失敗: {e}")
                raise
        
        print(f"🎵 所有區塊合並完成，總大小: {len(combined_audio)} bytes")
        return combined_audio
    else:
        # 原始邏輯，處理短文本
        try:
            # 構建 API 參數
            api_params = {
                "model": audio_model,
                "voice": voice,
                "input": text,
            }
            if instructions:
                api_params["instructions"] = instructions
                print(f"💬 使用語氣指示: {instructions}")
            
            print(f"📡 調用 OpenAI TTS API...")
            with client.audio.speech.with_streaming_response.create(**api_params) as response:
                with io.BytesIO() as file:
                    for audio_chunk in response.iter_bytes():
                        file.write(audio_chunk)
                    audio_data = file.getvalue()
                    print(f"✅ 音頻生成完成: {len(audio_data)} bytes")
                    return audio_data
        except Exception as e:
            print(f"❌ 音頻生成失敗: {e}")
            raise

def generate_audio_from_script(
    script: str,
    audio_api_key: str,
    audio_model: str = "gpt-4o-mini-tts",
    speaker1_voice: str = "onyx",
    speaker2_voice: str = "nova",
    volume_boost: float = 0,
    speaker1_instructions: str = "保持活潑愉快的語氣",
    speaker2_instructions: str = "保持活潑愉快的語氣",
) -> tuple[bytes, str]:
    """從腳本生成音頻，支持兩個說話者，並優化 API 調用"""
    print("🎬 開始從腳本生成音頻")
    print(f"📜 腳本總長度: {len(script)} 字符")
    print(f"🎤 說話者聲音: 說話者1={speaker1_voice}, 說話者2={speaker2_voice}")
    print(f"🔊 音量增強: {volume_boost} dB")
    
    status_log = []
    
    # 優化腳本處理
    print("🔍 優化腳本內容...")
    optimized_script = optimize_script(script)
    print(f"✅ 腳本優化完成，共 {len(optimized_script)} 個片段")
    
    # 使用 pydub 處理音頻合並
    combined_segment = None
    
    # 處理每一段
    total_segments = len(optimized_script)
    print(f"🎵 開始處理 {total_segments} 個音頻片段")
    
    for i, (speaker, text) in enumerate(optimized_script, 1):
        voice_to_use = speaker1_voice if speaker == "speaker-1" else speaker2_voice
        instructions_to_use = speaker1_instructions if speaker == "speaker-1" else speaker2_instructions
        
        print(f"🎭 處理片段 {i}/{total_segments}: {speaker} ({len(text)} 字符)")
        status_log.append(f"[{speaker}] {text}")
        
        try:
            # 生成這一段的音頻
            print(f"📡 生成 {speaker} 的音頻...")
            audio_chunk = get_mp3(
                text,
                voice_to_use,
                audio_model,
                audio_api_key,
                instructions_to_use
            )
            
            print(f"✅ {speaker} 音頻生成完成: {len(audio_chunk)} bytes")
            
            # 將二進制數據轉換為 AudioSegment
            with NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(audio_chunk)
                temp_file_path = temp_file.name
            
            # 讀取音頻
            chunk_segment = AudioSegment.from_mp3(temp_file_path)
            
            # 刪除臨時文件
            os.unlink(temp_file_path)
            
            # 合並音頻段
            if combined_segment is None:
                combined_segment = chunk_segment
                print("🔗 創建第一個音頻片段")
            else:
                combined_segment += chunk_segment
                print(f"🔗 已合並片段 {i}/{total_segments}")
                
        except Exception as e:
            error_msg = f"❌ 片段 {i} ({speaker}) 生成失敗: {str(e)}"
            print(error_msg)
            status_log.append(f"[錯誤] 無法生成音頻: {str(e)}")
            raise
    
    # 如果沒有生成任何音頻段
    if combined_segment is None:
        error_msg = "❌ 沒有生成任何音頻"
        print(error_msg)
        status_log.append("[錯誤] 沒有生成任何音頻")
        return b"", "\n".join(status_log)
    
    # 如果需要調整音量
    if volume_boost > 0:
        try:
            print(f"🔊 調整音量 +{volume_boost} dB...")
            # 調整音量
            combined_segment = combined_segment + volume_boost  # 增加音量 (dB)
            status_log.append(f"[音量] 已增加 {volume_boost} dB")
            print("✅ 音量調整完成")
        except Exception as e:
            warning_msg = f"⚠️ 音量調整失敗: {str(e)}"
            print(warning_msg)
            status_log.append(f"[警告] 音量調整失敗: {str(e)}")
    
    # 將 AudioSegment 轉換為二進制數據
    print("💾 導出最終音頻文件...")
    output = io.BytesIO()
    combined_segment.export(output, format="mp3")
    combined_audio = output.getvalue()
    
    print(f"🎉 腳本音頻生成完成！最終大小: {len(combined_audio)} bytes")
    return combined_audio, "\n".join(status_log)

def save_audio_file(audio_data: bytes) -> str:
    """將音頻數據保存為臨時文件"""
    print("💾 開始保存音頻文件...")
    
    temp_dir = Path("./temp_audio")
    temp_dir.mkdir(exist_ok=True)
    
    # 清理舊文件
    old_files_count = 0
    for old_file in temp_dir.glob("*.mp3"):
        if old_file.stat().st_mtime < (time.time() - 24*60*60):  # 24小時前的文件
            old_file.unlink()
            old_files_count += 1
    
    if old_files_count > 0:
        print(f"🧹 清理了 {old_files_count} 個舊的臨時文件")
    
    # 創建新的臨時文件
    temp_file = NamedTemporaryFile(
        dir=temp_dir,
        delete=False,
        suffix=".mp3"
    )
    temp_file.write(audio_data)
    temp_file.close()
    
    print(f"✅ 音頻文件已保存: {temp_file.name} ({len(audio_data)} bytes)")
    return temp_file.name

def process_and_save_audio(script, api_key, model, voice1, voice2, volume_boost, instr1, instr2):
    """處理音頻生成並保存文件"""
    try:
        audio_data, status_log = generate_audio_from_script(
            script,
            api_key,
            model,
            voice1,
            voice2,
            volume_boost,
            instr1,
            instr2
        )
        audio_path = save_audio_file(audio_data)
        return audio_path, status_log
    except Exception as e:
        error_message = f"生成音頻時發生錯誤: {str(e)}"
        print(error_message)
        return None, error_message

# Gradio 界面
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
                    placeholder="""請粘貼腳本內容，格式如下：
speaker-1: 歡迎來到 David888 Podcast，我是 David...
speaker-2: 大家好，我是 Cordelia...
沒有標記說話者的行會默認使用說話者1的聲音。

提示：為提高效率，相同說話者的多行文字將自動合並處理。""",
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
                        value="gpt-4o-mini-tts"
                    )
                    speaker1_voice = gr.Dropdown(
                        label="說話者1聲音 (男角) | Speaker 1 Voice (Male)",
                        choices=STANDARD_VOICES,
                        value="onyx"
                    )
                    speaker2_voice = gr.Dropdown(
                        label="說話者2聲音 (女角) | Speaker 2 Voice (Female)",
                        choices=STANDARD_VOICES,
                        value="nova"
                    )
                
                with gr.Row():
                    speaker1_instructions = gr.Textbox(
                        label="說話者1語氣 | Speaker 1 Instructions",
                        value="保持活潑愉快的語氣",
                        placeholder="例如:保持活潑愉快的語氣、用專業嚴肅的口吻說話等"
                    )
                    speaker2_instructions = gr.Textbox(
                        label="說話者2語氣 | Speaker 2 Instructions",
                        value="保持活潑愉快的語氣",
                        placeholder="例如:保持活潑愉快的語氣、用專業嚴肅的口吻說話等"
                    )
                
                volume_boost = gr.Slider(
                    label="音量增益 (dB) | Volume Boost (dB)",
                    minimum=0,
                    maximum=20,
                    value=6,
                    step=1,
                    info="增加音頻音量，單位為分貝(dB)。建議值：6-10 dB"
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
            fn=process_and_save_audio,
            inputs=[
                script_input,
                api_key,
                audio_model,
                speaker1_voice,
                speaker2_voice,
                volume_boost,
                speaker1_instructions,
                speaker2_instructions
            ],
            outputs=[audio_output, status_output]
        )
    return demo


demo = create_gradio_interface()
# Hugging Face Spaces expects a global `app` Gradio interface
app = demo.queue()

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)