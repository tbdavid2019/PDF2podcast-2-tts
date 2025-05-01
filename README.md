---
title: PDF2podcast 2 Tts
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

## 功能特點

- 🎙️ **雙說話者支援**：可分配不同聲音給兩位說話者，適合對話式內容
- 🔄 **智能文本優化**：自動合併相同說話者的連續文本，減少API調用次數
- 🎛️ **多種聲音選項**：支援OpenAI的全部6種TTS聲音（alloy、echo、fable、onyx、nova、shimmer）
- 🎚️ **模型選擇**：支援標準(tts-1)和高清(tts-1-hd)音頻模型
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

#### API端點

##### 生成音頻

```
POST /generate-audio
```

請求體示例：
```json
{
  "script": "speaker-1: 你好，歡迎來到播客！\nspeaker-2: 謝謝邀請，很高興來到這裡。",
  "api_key": "your_openai_api_key",
  "model": "tts-1",
  "speaker1_voice": "onyx",
  "speaker2_voice": "nova",
  "volume_boost": 6.0,
  "return_url": false
}
```

- 如果`return_url`為`false`，將直接返回音頻文件
- 如果`return_url`為`true`，將返回音頻文件的URL

##### 獲取可用選項

```
GET /options
```

返回可用的音頻模型和聲音選項。

##### API文檔

啟動API服務後，可以訪問自動生成的API文檔：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 腳本格式

腳本應按以下格式編寫：

```
speaker-1: 這是第一位說話者的台詞。
speaker-2: 這是第二位說話者的台詞。
這行沒有標記說話者，將默認使用說話者1的聲音。
speaker-1: 繼續對話...
```

**提示**：相同說話者的連續文本會自動合併處理，以提高API調用效率。

## 參數說明

| 參數 | 說明 |
|------|------|
| 音頻模型 | 選擇TTS模型：標準(tts-1)或高清(tts-1-hd) |
| 說話者1聲音 | 第一位說話者使用的聲音 |
| 說話者2聲音 | 第二位說話者使用的聲音 |
| 音量增益 | 增加音頻音量的分貝值（dB），建議值：6-10 dB |
| OpenAI API Key | 您的OpenAI API金鑰 |

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

## 授權信息

[MIT授權](https://opensource.org/licenses/MIT)
