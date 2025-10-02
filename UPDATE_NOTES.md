# 更新說明 - 新增 OpenAI TTS API 語氣控制功能

## 更新日期
2025年10月2日

## 主要更新內容

### 1. 新增模型支援
- ✅ **gpt-4o-mini-tts**：OpenAI 最新的平價 TTS 模型（推薦使用）
- ✅ **gpt-4o-audio-preview**：音頻預覽版本
- 保留原有的 `tts-1` 和 `tts-1-hd` 模型支援

### 2. 新增聲音選項
- ✅ **coral**：活潑的女聲
- ✅ **sage**：成熟的男聲
- 原有聲音（alloy、echo、fable、onyx、nova、shimmer）繼續可用

### 3. 語氣控制功能（Instructions）
新增 `instructions` 參數，允許用戶自訂說話者的語氣和風格：

#### 在 Gradio 界面中使用：
- 新增「說話者1語氣」輸入框
- 新增「說話者2語氣」輸入框
- 預設值：「保持活潑愉快的語氣」

#### 在 API 中使用：
```json
{
  "speaker1_instructions": "保持活潑愉快的語氣",
  "speaker2_instructions": "用專業嚴肅的口吻說話"
}
```

#### 語氣範例：
- "保持活潑愉快的語氣" - 輕鬆對話
- "用專業嚴肅的口吻說話" - 正式場合
- "以熱情洋溢的方式表達" - 激勵演講
- "用溫柔平和的語調" - 冥想引導
- "保持中性客觀的態度" - 教育內容

### 4. 預設值更新
- 預設模型：`tts-1` → `gpt-4o-mini-tts`（更經濟實惠）
- 說話者1（男角）：預設使用 `onyx` 聲音
- 說話者2（女角）：預設使用 `nova` 聲音
- 預設語氣：「保持活潑愉快的語氣」

## 技術實現細節

### app.py 更新
1. 更新 `STANDARD_AUDIO_MODELS` 和 `STANDARD_VOICES` 列表
2. 修改 `get_mp3()` 函數，新增 `instructions` 參數
3. 更新 `generate_audio_from_script()` 函數，支援語氣參數
4. 修改 `process_and_save_audio()` 函數簽名
5. 更新 Gradio 界面，新增語氣輸入欄位

### api.py 更新
1. 更新 `STANDARD_AUDIO_MODELS` 和 `STANDARD_VOICES` 列表
2. 修改 `get_mp3()` 函數，新增 `instructions` 參數
3. 更新 `generate_audio_from_script()` 函數，支援語氣參數
4. 更新 `TTSRequest` 模型，新增語氣欄位
5. 修改 API 端點以傳遞語氣參數

### API 調用方式更新
```python
# 短文本（單次調用）
api_params = {
    "model": audio_model,
    "voice": voice,
    "input": text,
}
if instructions:
    api_params["instructions"] = instructions

with client.audio.speech.with_streaming_response.create(**api_params) as response:
    # 處理回應...
```

## 向後兼容性
✅ 完全向後兼容
- 語氣參數為可選，不提供時使用預設值
- 原有的模型和聲音選項仍然可用
- API 端點保持不變

## 使用範例

### Python 直接調用
```python
from openai import OpenAI

client = OpenAI()
with client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",
    voice="nova",
    input="歡迎收聽我們的播客！",
    instructions="保持活潑愉快的語氣",
) as response:
    response.stream_to_file("output.mp3")
```

### 通過 Gradio 界面
1. 選擇模型：`gpt-4o-mini-tts`
2. 設定說話者1聲音：`onyx`（男聲）
3. 設定說話者2聲音：`nova`（女聲）
4. 設定說話者1語氣：「保持活潑愉快的語氣」
5. 設定說話者2語氣：「保持活潑愉快的語氣」
6. 輸入腳本並生成

### 通過 API
```bash
curl -X POST "http://localhost:8000/generate-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "script": "speaker-1: 你好！\nspeaker-2: 你好啊！",
    "model": "gpt-4o-mini-tts",
    "speaker1_voice": "onyx",
    "speaker2_voice": "nova",
    "speaker1_instructions": "保持活潑愉快的語氣",
    "speaker2_instructions": "保持活潑愉快的語氣"
  }'
```

## 效益
1. 💰 **成本降低**：使用 `gpt-4o-mini-tts` 模型可降低 TTS 成本
2. 🎭 **表現力增強**：語氣控制讓生成的語音更自然、更符合場景
3. 🎤 **更多選擇**：新增的聲音選項提供更多樣化的選擇
4. 🔧 **靈活性提升**：每個說話者可設定不同的語氣

## 測試檔案
- `example_usage.py`：包含各種使用範例，包括基本用法、語氣控制、對話生成等

## 相關文件
- OpenAI TTS API 文檔：https://platform.openai.com/docs/guides/text-to-speech
- Gradio 文檔：https://www.gradio.app/docs
