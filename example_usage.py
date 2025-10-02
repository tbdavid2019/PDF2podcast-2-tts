"""
OpenAI TTS API 使用範例
展示如何使用新的 gpt-4o-mini-tts 模型和語氣設定功能
"""

from pathlib import Path
from openai import OpenAI
import os
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()

# 初始化 OpenAI 客戶端
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def example_basic_tts():
    """基本 TTS 範例 - 使用新的 gpt-4o-mini-tts 模型"""
    print("正在生成基本 TTS 範例...")
    
    speech_file_path = Path(__file__).parent / "output_basic.mp3"
    
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",  # 使用更平價的模型
        voice="nova",  # 女角預設聲音
        input="今天是建立人們喜愛的東西的美好一天！",
    ) as response:
        response.stream_to_file(speech_file_path)
    
    print(f"✓ 基本範例已生成: {speech_file_path}")


def example_with_instructions():
    """使用語氣指示的範例"""
    print("\n正在生成帶語氣指示的範例...")
    
    speech_file_path = Path(__file__).parent / "output_cheerful.mp3"
    
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",  # 新增的聲音選項
        input="歡迎收聽我們的播客！今天我們將討論一些非常有趣的話題。",
        instructions="保持活潑愉快的語氣",  # 語氣設定
    ) as response:
        response.stream_to_file(speech_file_path)
    
    print(f"✓ 活潑愉快範例已生成: {speech_file_path}")


def example_professional_tone():
    """專業嚴肅語氣範例"""
    print("\n正在生成專業語氣範例...")
    
    speech_file_path = Path(__file__).parent / "output_professional.mp3"
    
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="onyx",  # 男角預設聲音
        input="根據最新的研究報告，我們發現市場趨勢正在發生重大變化。",
        instructions="用專業嚴肅的口吻說話",  # 專業語氣
    ) as response:
        response.stream_to_file(speech_file_path)
    
    print(f"✓ 專業語氣範例已生成: {speech_file_path}")


def example_dialogue():
    """對話範例 - 展示如何生成雙說話者對話"""
    print("\n正在生成對話範例...")
    
    # 說話者1（男聲）
    speech_file_1 = Path(__file__).parent / "output_speaker1.mp3"
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="onyx",
        input="你好，歡迎來到今天的節目。今天我們要討論人工智能的未來。",
        instructions="保持活潑愉快的語氣",
    ) as response:
        response.stream_to_file(speech_file_1)
    
    # 說話者2（女聲）
    speech_file_2 = Path(__file__).parent / "output_speaker2.mp3"
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="nova",
        input="謝謝邀請！我對這個話題非常感興趣。人工智能正在改變我們的生活方式。",
        instructions="保持活潑愉快的語氣",
    ) as response:
        response.stream_to_file(speech_file_2)
    
    print(f"✓ 對話範例已生成:")
    print(f"  - 說話者1: {speech_file_1}")
    print(f"  - 說話者2: {speech_file_2}")


def example_model_comparison():
    """比較不同模型"""
    print("\n正在生成模型比較範例...")
    
    text = "這是一個測試，比較不同 TTS 模型的音質差異。"
    
    # gpt-4o-mini-tts (平價版本)
    speech_file_mini = Path(__file__).parent / "output_mini_tts.mp3"
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="nova",
        input=text,
    ) as response:
        response.stream_to_file(speech_file_mini)
    
    # tts-1 (標準版本，用於比較)
    speech_file_standard = Path(__file__).parent / "output_tts1.mp3"
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="nova",
        input=text,
    ) as response:
        response.stream_to_file(speech_file_standard)
    
    print(f"✓ 模型比較範例已生成:")
    print(f"  - gpt-4o-mini-tts: {speech_file_mini}")
    print(f"  - tts-1: {speech_file_standard}")


if __name__ == "__main__":
    print("=" * 60)
    print("OpenAI TTS API 使用範例")
    print("=" * 60)
    
    try:
        # 執行所有範例
        example_basic_tts()
        example_with_instructions()
        example_professional_tone()
        example_dialogue()
        example_model_comparison()
        
        print("\n" + "=" * 60)
        print("所有範例已成功生成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        print("請確保:")
        print("1. 已設置 OPENAI_API_KEY 環境變量")
        print("2. API 金鑰有效且有足夠的額度")
        print("3. 已安裝所需的套件: pip install openai python-dotenv")
