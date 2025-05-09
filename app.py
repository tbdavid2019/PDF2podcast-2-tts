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

# 标准音频模型和声音选项
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

# 优化脚本处理 - 合并相同说话者连续文本
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
            speaker = "speaker-1"  # 默认使用说话者1
            text = line
        
        # 如果说话者变了，保存之前的文本并开始新的
        if speaker != current_speaker and current_text:
            optimized.append((current_speaker, current_text))
            current_text = text
            current_speaker = speaker
        else:
            # 相同说话者，合并文本（加空格）
            if current_text:
                current_text += " " + text
            else:
                current_text = text
                current_speaker = speaker
                
    # 添加最后一个说话者的文本
    if current_text:
        optimized.append((current_speaker, current_text))
        
    return optimized

def get_mp3(text: str, voice: str, audio_model: str, audio_api_key: str) -> bytes:
    """使用 OpenAI TTS API 生成音频"""
    # 检查文本长度，OpenAI TTS API 有 4096 个标记的限制
    # 大约 1000 个汉字约等于 2000-3000 个标记，为安全起见，我们将限制设为 1000 个字符
    MAX_TEXT_LENGTH = 1000
    
    client = OpenAI(api_key=audio_api_key)
    
    # 如果文本长度超过限制，分割文本
    if len(text) > MAX_TEXT_LENGTH:
        print(f"Text too long ({len(text)} chars), splitting into chunks")
        # 将文本分割成更小的块
        text_chunks = []
        for i in range(0, len(text), MAX_TEXT_LENGTH):
            text_chunks.append(text[i:i + MAX_TEXT_LENGTH])
        
        # 为每个块生成音频并合并
        combined_audio = b""
        for chunk in text_chunks:
            try:
                with client.audio.speech.with_streaming_response.create(
                    model=audio_model,
                    voice=voice,
                    input=chunk,
                ) as response:
                    with io.BytesIO() as file:
                        for audio_chunk in response.iter_bytes():
                            file.write(audio_chunk)
                        combined_audio += file.getvalue()
            except Exception as e:
                print(f"Error generating audio for chunk: {e}")
                raise
        
        return combined_audio
    else:
        # 原始逻辑，处理短文本
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
) -> tuple[bytes, str]:
    """从脚本生成音频，支持两个说话者，并优化 API 调用"""
    status_log = []
    
    # 优化脚本处理
    optimized_script = optimize_script(script)
    
    # 使用 pydub 处理音频合并
    combined_segment = None
    
    # 处理每一段
    for speaker, text in optimized_script:
        voice_to_use = speaker1_voice if speaker == "speaker-1" else speaker2_voice
        status_log.append(f"[{speaker}] {text}")
        
        try:
            # 生成这一段的音频
            audio_chunk = get_mp3(
                text,
                voice_to_use,
                audio_model,
                audio_api_key
            )
            
            # 将二进制数据转换为 AudioSegment
            with NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(audio_chunk)
                temp_file_path = temp_file.name
            
            # 读取音频
            chunk_segment = AudioSegment.from_mp3(temp_file_path)
            
            # 删除临时文件
            os.unlink(temp_file_path)
            
            # 合并音频段
            if combined_segment is None:
                combined_segment = chunk_segment
            else:
                combined_segment += chunk_segment
        except Exception as e:
            status_log.append(f"[错误] 无法生成音频: {str(e)}")
    
    # 如果沒有生成任何音頻段
    if combined_segment is None:
        status_log.append("[錯誤] 沒有生成任何音頻")
        return b"", "\n".join(status_log)
    
    # 如果需要調整音量
    if volume_boost > 0:
        try:
            # 調整音量
            combined_segment = combined_segment + volume_boost  # 增加音量 (dB)
            status_log.append(f"[音量] 已增加 {volume_boost} dB")
        except Exception as e:
            status_log.append(f"[警告] 音量調整失敗: {str(e)}")
    
    # 將 AudioSegment 轉換為二進制數據
    output = io.BytesIO()
    combined_segment.export(output, format="mp3")
    combined_audio = output.getvalue()
    
    return combined_audio, "\n".join(status_log)

def save_audio_file(audio_data: bytes) -> str:
    """将音频数据保存为临时文件"""
    temp_dir = Path("./temp_audio")
    temp_dir.mkdir(exist_ok=True)
    # 清理旧文件
    for old_file in temp_dir.glob("*.mp3"):
        if old_file.stat().st_mtime < (time.time() - 24*60*60):  # 24小时前的文件
            old_file.unlink()
    # 创建新的临时文件
    temp_file = NamedTemporaryFile(
        dir=temp_dir,
        delete=False,
        suffix=".mp3"
    )
    temp_file.write(audio_data)
    temp_file.close()
    return temp_file.name

def process_and_save_audio(script, api_key, model, voice1, voice2, volume_boost):
    """处理音频生成并保存文件"""
    try:
        audio_data, status_log = generate_audio_from_script(
            script,
            api_key,
            model,
            voice1,
            voice2,
            volume_boost
        )
        audio_path = save_audio_file(audio_data)
        return audio_path, status_log
    except Exception as e:
        error_message = f"生成音频时发生错误: {str(e)}"
        print(error_message)
        return None, error_message

# Gradio 界面
def create_gradio_interface():
    with gr.Blocks(title="TTS Generator", css="""
        #header { text-align: center; margin-bottom: 20px; }
    """) as demo:
        gr.Markdown("# 语音合成器 | TTS Generator", elem_id="header")
        with gr.Row():
            with gr.Column(scale=1):
                # 输入区
                script_input = gr.Textbox(
                    label="输入脚本 | Input Script",
                    placeholder="""请粘贴脚本内容，格式如下：
speaker-1: 欢迎来到 David888 Podcast，我是 David...
speaker-2: 大家好，我是 Cordelia...
没有标记说话者的行会默认使用说话者1的声音。

提示：为提高效率，相同说话者的多行文字将自动合并处理。""",
                    lines=20
                )
                api_key = gr.Textbox(
                    label="OpenAI API Key",
                    type="password"
                )
                with gr.Row():
                    audio_model = gr.Dropdown(
                        label="音频模型 | Audio Model",
                        choices=STANDARD_AUDIO_MODELS,
                        value="tts-1"
                    )
                    speaker1_voice = gr.Dropdown(
                        label="说话者1声音 | Speaker 1 Voice",
                        choices=STANDARD_VOICES,
                        value="onyx"
                    )
                    speaker2_voice = gr.Dropdown(
                        label="说话者2声音 | Speaker 2 Voice",
                        choices=STANDARD_VOICES,
                        value="nova"
                    )
                
                volume_boost = gr.Slider(
                    label="音量增益 (dB) | Volume Boost (dB)",
                    minimum=0,
                    maximum=20,
                    value=6,
                    step=1,
                    info="增加音頻音量，單位為分貝(dB)。建議值：6-10 dB"
                )
                generate_button = gr.Button("生成音频 | Generate Audio")
            with gr.Column(scale=1):
                # 输出区
                audio_output = gr.Audio(
                    label="生成的音频 | Generated Audio",
                    type="filepath"
                )
                status_output = gr.Textbox(
                    label="生成状态 | Generation Status",
                    lines=20,
                    show_copy_button=True
                )
        
        # 事件处理
        generate_button.click(
            fn=process_and_save_audio,
            inputs=[
                script_input,
                api_key,
                audio_model,
                speaker1_voice,
                speaker2_voice,
                volume_boost
            ],
            outputs=[audio_output, status_output]
        )
    return demo

if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch()