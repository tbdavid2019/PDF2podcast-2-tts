---
title: PDF2podcast 2 TTS
emoji: 💻
colorFrom: indigo
colorTo: red
sdk: gradio
sdk_version: 5.23.2
app_file: app.py
pinned: false
short_description: 原tbdavid2019/PDF2podcast拆出的語音生成(2)
---

# TTS Generator (語音合成器)

這是一個基於OpenAI TTS API的語音合成應用程式，可將文字腳本轉換為自然流暢的語音。應用程式支援雙說話者對話，並提供簡潔的網頁界面，適合製作播客、有聲書或對話式內容。

## 文檔索引

| 文檔名稱 | 說明 |
|---------|------|
| [README.md](README.md) | 主要說明文件，包含安裝、使用方法和功能介紹 |
| [UPDATE_NOTES.md](UPDATE_NOTES.md) | 更新日誌，詳細記錄版本變更和新功能說明 |
| [SUMMARY.md](SUMMARY.md) | 更新總結，概述最近的修改內容和變更點 |
| [example_usage.py](example_usage.py) | Python 使用範例，展示各種 TTS API 調用方式 |

## 功能特點

- 🎙️ **雙說話者支援**：可分配不同聲音給兩位說話者，適合對話式內容
- 🔄 **智能文本優化**：自動合併相同說話者的連續文本，減少API調用次數
- 🎛️ **多種聲音選項**：支援OpenAI的全部8種TTS聲音（alloy、echo、fable、onyx、nova、shimmer、coral、sage）
- 🎚️ **模型選擇**：支援最新的gpt-4o-mini-tts（平價版）、gpt-4o-audio-preview，以及標準的tts-1和tts-1-hd音頻模型
- 🎭 **語氣控制**：新增語氣指示功能，可自訂說話者的語氣和風格（如：活潑愉快、專業嚴肅等）
- 🌐 **友好界面**：基於Gradio的簡潔網頁界面，易於使用
- 💾 **自動文件管理**：自動保存生成的音頻並清理過期文件
- 🔊 **音量調整**：內建音量增益功能，可調整輸出音頻音量
- 🌍 **API支援**：提供獨立的API服務，支援外部應用程式呼叫
- 🔑 **環境變量**：支援通過.env文件配置API金鑰

## 安裝說明

### 前置需求

- Python 3.7+
- OpenAI API金鑰（需要啟用TTS功能）
- 可選：創建`.env`文件存儲API金鑰（從`.env.example`複製並修改）

### 安裝步驟

1. 克隆此專案或下載源碼
2. 安裝依賴項：

```bash
pip install -r requirements.txt
```

## 使用方法

### 環境設置

```bash
# 複製環境變量範本
cp .env.example .env

# 編輯 .env 文件，添加您的 OpenAI API Key
nano .env  # 或使用其他編輯器

# 安裝依賴項
pip install -r requirements.txt
```

### 通過網頁界面使用 (app.py)

1. 運行Gradio應用程式：

```bash
python app.py
```

2. 在瀏覽器中打開顯示的URL（通常是 http://127.0.0.1:7860）
3. 在文本框中輸入您的腳本
4. 輸入您的OpenAI API金鑰（或預先在`.env`文件中配置）
5. 選擇所需的音頻模型和說話者聲音
6. 調整音量增益（建議值：6-10 dB）
7. 點擊「生成音頻」按鈕
8. 等待處理完成後，您可以播放或下載生成的音頻

### 通過API使用 (api.py)

如果您需要從外部應用程式呼叫TTS功能，可以使用API：

1. 運行API服務：

```bash
python api.py
```

2. API服務將在 http://localhost:8000 啟動

- 如果`return_url`為`false`，將直接返回音頻文件
- 如果`return_url`為`true`，將返回音頻文件的URL
- `speaker1_instructions` 和 `speaker2_instructions` 為可選參數，用於控制說話者的語氣

## 腳本格式

腳本應按以下格式編寫：

```text
speaker-1: 這是第一位說話者的台詞。
speaker-2: 這是第二位說話者的台詞。
這行沒有標記說話者，將默認使用說話者1的聲音。
speaker-1: 繼續對話...
```

**提示**：相同說話者的連續文本會自動合併處理，以提高API調用效率。

## 參數說明

| 參數 | 說明 |
|------|------|
| 音頻模型 | 選擇TTS模型：gpt-4o-mini-tts（平價推薦）、gpt-4o-audio-preview、tts-1（標準）或tts-1-hd（高清） |
| 說話者1聲音（男角） | 第一位說話者使用的聲音，預設為onyx（男聲） |
| 說話者2聲音（女角） | 第二位說話者使用的聲音，預設為nova（女聲） |
| 說話者1語氣 | 第一位說話者的語氣指示，例如："保持活潑愉快的語氣"、"用專業嚴肅的口吻說話"等 |
| 說話者2語氣 | 第二位說話者的語氣指示，例如："保持活潑愉快的語氣"、"用專業嚴肅的口吻說話"等 |
| 音量增益 | 增加音頻音量的分貝值（dB），建議值：6-10 dB |
| OpenAI API Key | 您的OpenAI API金鑰 |

### 支援的聲音選項

- **alloy** - 中性音色
- **echo** - 男性音色
- **fable** - 英式口音
- **onyx** - 深沉男聲（男角預設）
- **nova** - 女性音色（女角預設）
- **shimmer** - 溫暖女聲
- **coral** - 活潑女聲（新增）
- **sage** - 成熟男聲（新增）

### 語氣指示範例

語氣指示功能讓您可以控制 TTS 輸出的表達方式：

- "保持活潑愉快的語氣" - 適合輕鬆的對話或娛樂內容
- "用專業嚴肅的口吻說話" - 適合新聞報導或正式場合
- "以熱情洋溢的方式表達" - 適合激勵演講或促銷內容
- "用溫柔平和的語調" - 適合冥想引導或睡前故事
- "保持中性客觀的態度" - 適合教育內容或說明文

## API 調用方法

### 基本概念

本專案提供 RESTful API，讓您能夠從外部應用程式呼叫 TTS 功能。API 服務運行在 `http://localhost:8000`。

### 啟動 API 服務

```bash
python api.py
```

### API 端點

#### 生成音頻

```http
POST /generate-audio
```

| 參數 | 類型 | 必填 | 預設值 | 說明 |
|------|------|------|--------|------|
| `script` | string | 是 | - | 腳本內容，格式為 "speaker-1: 文本" 或 "speaker-2: 文本" |
| `api_key` | string | 否 | 環境變數 | OpenAI API 金鑰 |
| `model` | string | 否 | "gpt-4o-mini-tts" | 音頻模型 |
| `speaker1_voice` | string | 否 | "onyx" | 說話者1的聲音 |
| `speaker2_voice` | string | 否 | "nova" | 說話者2的聲音 |
| `speaker1_instructions` | string | 否 | "保持活潑愉快的語氣" | 說話者1的語氣指示 |
| `speaker2_instructions` | string | 否 | "保持活潑愉快的語氣" | 說話者2的語氣指示 |
| `volume_boost` | float | 否 | 6.0 | 音量增益 dB |
| `return_url` | boolean | 否 | false | 是否返回音頻文件的 URL |

### API 調用範例

#### Python 範例

```python
import requests

# 基本調用
response = requests.post(
    "http://localhost:8000/generate-audio",
    json={
        "script": "speaker-1: 你好，歡迎來到播客！\nspeaker-2: 謝謝邀請，很高興來到這裡。",
        "api_key": "your_openai_api_key_here"
    }
)

# 保存音頻文件
if response.status_code == 200:
    with open("generated_audio.mp3", "wb") as f:
        f.write(response.content)
```

#### cURL 範例

```bash
# 基本調用
curl -X POST "http://localhost:8000/generate-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "script": "speaker-1: 你好！\nspeaker-2: 你好啊！",
    "api_key": "your_openai_api_key_here"
  }' \
  --output generated_audio.mp3

# 完整參數調用
curl -X POST "http://localhost:8000/generate-audio" \
  -H "Content-Type: application/json" \
  -d '{
    "script": "speaker-1: 歡迎收聽今天的節目！\nspeaker-2: 很高興來到這裡。",
    "model": "gpt-4o-mini-tts",
    "speaker1_voice": "onyx",
    "speaker2_voice": "nova",
    "speaker1_instructions": "保持活潑愉快的語氣",
    "speaker2_instructions": "用專業嚴肅的口吻說話",
    "volume_boost": 8.0,
    "api_key": "your_openai_api_key_here"
  }' \
  --output podcast_audio.mp3
```

#### JavaScript (Node.js) 範例

```javascript
const axios = require('axios');
const fs = require('fs');

async function generateAudio() {
    try {
        const response = await axios.post('http://localhost:8000/generate-audio', {
            script: "speaker-1: 你好，歡迎來到播客！\nspeaker-2: 謝謝邀請，很高興來到這裡。",
            model: "gpt-4o-mini-tts",
            speaker1_voice: "onyx",
            speaker2_voice: "nova",
            speaker1_instructions: "保持活潑愉快的語氣",
            speaker2_instructions: "保持活潑愉快的語氣",
            api_key: "your_openai_api_key_here"
        }, {
            responseType: 'arraybuffer'
        });

        fs.writeFileSync('generated_audio.mp3', response.data);
        console.log('音頻生成成功！');
    } catch (error) {
        console.error('生成失敗:', error.message);
    }
}

generateAudio();
```

#### 返回 URL 模式

如果設定 `return_url: true`，API 會返回音頻文件的 URL 而不是直接返回文件：

```python
import requests

response = requests.post(
    "http://localhost:8000/generate-audio",
    json={
        "script": "speaker-1: 這是一個測試。",
        "return_url": true,
        "api_key": "your_openai_api_key_here"
    }
)

if response.status_code == 200:
    result = response.json()
    audio_url = result["audio_url"]
    print(f"音頻URL: http://localhost:8000{audio_url}")
    
    # 下載音頻
    audio_response = requests.get(f"http://localhost:8000{audio_url}")
    with open("audio.mp3", "wb") as f:
        f.write(audio_response.content)
```

### 錯誤處理

API 會返回適當的 HTTP 狀態碼和錯誤訊息：

- `400 Bad Request`: 缺少必要參數或 API 金鑰無效
- `500 Internal Server Error`: 音頻生成失敗

錯誤響應格式：

```json
{
    "detail": "錯誤訊息描述"
}
```

### API 文檔

啟動 API 服務後，可以訪問自動生成的 API 文檔：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 其他 API 端點

#### 獲取可用選項

```http
GET /options
```

返回可用的音頻模型和聲音選項。

```json
{
    "models": ["gpt-4o-mini-tts", "gpt-4o-audio-preview", "tts-1", "tts-1-hd"],
    "voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer", "coral", "sage"]
}
```

#### 健康檢查

```http
GET /health
```

檢查 API 服務狀態。

```json
{
    "status": "healthy",
    "api_version": "1.0.0"
}
```

## 聲音選項

應用程式支援以下OpenAI TTS聲音：

- **alloy**: 全能且平穩的聲音
- **echo**: 深沉且有力的聲音
- **fable**: 溫暖且適合講故事的聲音
- **onyx**: 明確且專業的聲音
- **nova**: 友好且自然的聲音
- **shimmer**: 清晰且愉悅的聲音

## 技術細節

- 使用OpenAI的TTS API進行語音合成
- 使用Gradio建立網頁界面（app.py）
- 使用FastAPI提供RESTful API（api.py）
- 自動管理臨時音頻文件（24小時後自動清理）
- 支援流式處理大型音頻文件
- 使用pydub處理音頻音量調整

## 依賴項

- gradio: 網頁界面
- openai: OpenAI API客戶端
- fastapi: API框架
- uvicorn: ASGI服務器
- pydub: 音頻處理
- python-dotenv: 環境變量管理
- pathlib: 文件路徑處理
- io: 二進制數據處理

## 注意事項

- 使用此應用程式需要有效的OpenAI API金鑰
- API使用會產生費用，請參考OpenAI的[價格頁面](https://openai.com/pricing)
- 生成的臨時音頻文件會在24小時後自動刪除
- 在Hugging Face Space上運行時，app.py會自動啟動，提供Gradio界面
- 如需API功能，需要單獨運行api.py


