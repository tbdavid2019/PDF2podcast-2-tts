---
title: PDF2podcast 2 TTS
emoji: 💻
colorFrom: indigo
colorTo: red
sdk: gradio
sdk_version: 6.1.0
app_file: app.py
pinned: false
short_description: 多語言 TTS 語音合成器 - 支援 OpenAI/Gemini/AWS Polly/台語
---

# TTS Generator (多語言語音合成器)

支援 **OpenAI TTS**、**Gemini TTS**、**AWS Polly** 與 **台語 TTS** 的多功能語音合成應用程式。可將文字腳本轉換為自然流暢的語音，支援雙說話者對話，適合製作播客、有聲書或對話式內容。

## ✨ 核心功能

- 🎯 **四大 TTS 引擎**：OpenAI、Gemini、AWS Polly、台語 TTS 自由切換
- 🎙️ **雙說話者對話**：OpenAI 與 Gemini 支援分別指定男女聲音
- 🔄 **智能腳本處理**：自動合併相同說話者連續文本，減少 API 調用
- 🎛️ **豐富聲音庫**：OpenAI 8種、Gemini 6種、Polly 中文女聲、台語女聲
- 🎭 **語氣控制**：OpenAI 支援自訂語氣指示（活潑、嚴肅、溫柔等）
- 🌐 **直覺介面**：Gradio 網頁界面，依選擇的 TTS 自動顯示對應欄位
- 🔊 **音量調整**：內建音量增益（0-20 dB）
- 💾 **自動管理**：臨時檔案 24 小時自動清理
- 🔑 **多種認證**：支援環境變數或介面輸入 API Key

## 🚀 快速開始

### 前置需求

- Python 3.10+
- 至少一組 TTS 服務的憑證（擇一即可）：
  - **OpenAI**：OPENAI_API_KEY
  - **Gemini**：GEMINI_API_KEY  
  - **AWS Polly**：AWS_ACCESS_KEY_ID、AWS_SECRET_ACCESS_KEY、AWS_REGION
  - **台語 TTS**：免金鑰

### 安裝

```bash
# 1. 克隆專案
git clone <repository_url>
cd PDF2podcast-2-tts

# 2. 安裝依賴
pip install -r requirements.txt

# 3. （選用）配置環境變數
cp .env.example .env
nano .env  # 填入您的 API 金鑰
```

### 啟動應用

```bash
python app.py
```

開啟瀏覽器訪問 `http://127.0.0.1:7860`

## 📝 使用指南

### 腳本格式

```text
speaker-1: 歡迎來到 Podcast，我是主持人。
speaker-2: 大家好，很高興來到這裡。
沒有標記的行將使用說話者1的聲音。
speaker-1: 今天我們要聊...
```

**提示**：相同說話者的連續段落會自動合併處理。

### TTS 服務選擇

| 服務 | 特色 | 雙說話者 | 中文支援 | 費用 |
|------|------|----------|----------|------|
| **OpenAI** | 8種聲音、語氣控制 | ✅ 獨立聲音 | 優秀 | 按字計費 |
| **Gemini** | 6種聲音、中文清晰 | ✅ 獨立聲音 | **最佳** | 按字計費 |
| **AWS Polly** | Zhiyu 女聲 | ⚠️ 共用女聲 | 優秀 | 按字計費 |
| **台語 TTS** | model6 女聲 | ⚠️ 共用女聲 | 台語專用 | **免費** |

## 🎤 聲音選項參考

### OpenAI TTS 聲音

| 聲音 | 特色 | 適合場景 |
|------|------|----------|
| **alloy** | 中性平衡 | 通用對話 |
| **echo** | 低沉男聲 | 旁白/正式說明 |
| **fable** | 溫暖敘事 | 故事/有聲書 |
| **onyx** | 清晰沉穩男聲 | 說明/主持 |
| **nova** | 友好女聲 | 對話互動 |
| **shimmer** | 柔和女聲 | 客服/陪伴 |
| **coral** | 活潑女聲 | 行銷/短視頻 |
| **sage** | 成熟男聲 | 新聞/解說 |

**模型選擇**：
- `gpt-4o-mini-tts`：平價推薦
- `gpt-4o-audio-preview`：最新版本
- `tts-1`：標準版
- `tts-1-hd`：高清版

### Gemini TTS 聲音

| 聲音 | 特色 | 中文支援 | 建議 |
|------|------|----------|------|
| **Puck** | 自然中音、對話感強 | ⭐⭐⭐ 咬字清楚 | **男聲首選** |
| **Aoede** | 清晰女聲 | ⭐⭐⭐ 咬字清楚 | **女聲首選** |
| **Charon** | 低沉穩重、權威感 | ⭐⭐ | 新聞/嚴肅 |
| **Fenrir** | 高亢有活力 | ⚠️ 語速不穩 | 避免用於中文 |
| Alnilam/Algieba | 舊版代號 | - | 建議用新聲音 |

**中文最佳組合**：Puck (男) + Aoede (女)

### AWS Polly 中文聲音

- **Zhiyu**：唯一中文女聲（neural 引擎），雙說話者共用

### 台語 TTS

- **model6**：唯一台語女聲，免金鑰，雙說話者共用

## 🎭 語氣控制範例（OpenAI 專用）

```text
保持活潑愉快的語氣        → 輕鬆對話/娛樂
用專業嚴肅的口吻說話      → 新聞/正式場合
以熱情洋溢的方式表達      → 激勵演講/促銷
用溫柔平和的語調          → 冥想/睡前故事
保持中性客觀的態度        → 教育/說明文
```

## 🔌 API 服務（進階）

### 啟動 API

```bash
python api.py
# 訪問 http://localhost:8000/docs 查看 Swagger 文檔
```

### 基本調用

```python
import requests

response = requests.post(
    "http://localhost:8000/generate-audio",
    json={
        "script": "speaker-1: 你好！\nspeaker-2: 你好啊！",
        "api_key": "your_openai_api_key"
    }
)

with open("output.mp3", "wb") as f:
    f.write(response.content)
```

### API 參數

| 參數 | 類型 | 必填 | 預設 | 說明 |
|------|------|------|------|------|
| `script` | string | ✅ | - | 對話腳本 |
| `api_key` | string | - | 環境變數 | OpenAI API Key |
| `model` | string | - | gpt-4o-mini-tts | 模型名稱 |
| `speaker1_voice` | string | - | onyx | 說話者1聲音 |
| `speaker2_voice` | string | - | nova | 說話者2聲音 |
| `volume_boost` | float | - | 6.0 | 音量增益 (dB) |
| `return_url` | boolean | - | false | 是否返回 URL |

**API 文檔**：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🛠️ 技術架構

```
├── app.py                 # Gradio 網頁介面主程式
├── api.py                 # FastAPI REST API 服務
├── requirements.txt       # Python 依賴套件
├── .env                   # 環境變數配置（需自行建立）
└── temp_audio/            # 臨時音頻存放（自動清理）
```

### 核心依賴

| 套件 | 用途 |
|------|------|
| `gradio` | 網頁 UI 框架 |
| `openai` | OpenAI TTS 客戶端 |
| `google-genai` | Gemini TTS 客戶端 |
| `boto3` | AWS Polly 客戶端 |
| `requests` | 台語 TTS HTTP 請求 |
| `pydub` | 音頻處理與合併 |
| `fastapi` + `uvicorn` | API 服務框架 |

## ⚠️ 注意事項

### 費用相關
- **OpenAI**：依字符計費，詳見 [價格表](https://openai.com/pricing)
- **Gemini**：依字符計費，需 Google Cloud 帳號
- **AWS Polly**：依字符計費，免費額度：每月 500 萬字符（新用戶 12 個月）
- **台語 TTS**：免費（公益服務）

### 限制說明
- **Polly / 台語**：僅單一女聲，雙說話者會共用同一聲音
- **Gemini Fenrir**：中文語速不穩定，建議避免
- **臨時檔案**：24 小時後自動清除
- **Hugging Face Spaces**：部署時自動啟動 `app.py`

### 環境變數設定

在 `.env` 檔案中配置（選填）：

```bash
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=ap-northeast-1
```

## 📄 授權

本專案從 [tbdavid2019/PDF2podcast](https://github.com/tbdavid2019/PDF2podcast) 拆分而來，保留原專案授權條款。

---

**開發者**：tbdavid2019
**專案目的**：提供多語言、多引擎的 TTS 語音合成解決方案


