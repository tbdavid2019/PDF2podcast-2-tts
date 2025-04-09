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

## 安裝說明

### 前置需求

- Python 3.7+
- OpenAI API金鑰（需要啟用TTS功能）

### 安裝步驟

1. 克隆此專案或下載源碼
2. 安裝依賴項：

```bash
pip install -r requirements.txt
```

## 使用方法

1. 運行應用程式：

```bash
python app.py
```

2. 在瀏覽器中打開顯示的URL（通常是 http://127.0.0.1:7860）
3. 在文本框中輸入您的腳本
4. 輸入您的OpenAI API金鑰
5. 選擇所需的音頻模型和說話者聲音
6. 點擊「生成音頻」按鈕
7. 等待處理完成後，您可以播放或下載生成的音頻

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
- 使用Gradio建立網頁界面
- 自動管理臨時音頻文件（24小時後自動清理）
- 支援流式處理大型音頻文件

## 依賴項

- gradio: 網頁界面
- openai: OpenAI API客戶端
- pathlib: 文件路徑處理
- io: 二進制數據處理

## 注意事項

- 使用此應用程式需要有效的OpenAI API金鑰
- API使用會產生費用，請參考OpenAI的[價格頁面](https://openai.com/pricing)
- 生成的臨時音頻文件會在24小時後自動刪除

## 授權信息

[MIT授權](https://opensource.org/licenses/MIT)
