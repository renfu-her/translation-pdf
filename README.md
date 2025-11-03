# PDF 繁體中文轉換工具

這是一個可以將 PDF 文件轉換為繁體中文的工具，同時保留原始的格式、字體、佈局和圖片。

## 功能特點

- ✅ **圖形化界面 (GUI)**：使用 PySide6 提供現代化的圖形界面
- ✅ **命令行界面 (CLI)**：支援命令行操作，適合自動化腳本
- ✅ 保留原始 PDF 格式（字體、大小、顏色、佈局）
- ✅ **自動檢測原始語言**：智能識別 PDF 中的文字語系（英文、日文、法文等）
- ✅ 自動翻譯為繁體中文
- ✅ 支援 Google Translate、**Free ChatGPT API**、OpenAI API 和 LocalAI
- ✅ 翻譯緩存機制，避免重複翻譯
- ✅ 保持圖片和圖形不變
- ✅ 智能識別中文內容，跳過已翻譯的文本
- ✅ 實時進度顯示

## 安裝依賴

### 基本安裝

```bash
pip install -r requirements.txt
```

這個版本使用 `deep-translator` 庫，避免了與其他包的 `httpx` 版本衝突問題。

### 如果需要使用 OpenAI API、Free ChatGPT API 或 LocalAI

```bash
pip install openai
```

**注意**：
- **Free ChatGPT API**（默認推薦）：完全免費，無需付費 API key，只需前往 [免費領取 API Key](https://github.com/popjane/free_chatgpt_api)
- Google Translate：免費使用，但可能有速率限制
- OpenAI API：需要付費 API key，翻譯質量通常更好

## 使用方法

### 圖形化界面 (GUI) - 推薦

最簡單的方式是使用圖形界面：

```bash
# 啟動 GUI（默認）
python main.py

# 或明確指定 GUI 模式
python main.py --gui
```

GUI 界面提供：
- 📁 文件瀏覽器選擇輸入/輸出文件
- ⚙️ 翻譯服務選擇（**Free ChatGPT API** / Google Translate / OpenAI / LocalAI）
- 🔑 API 密鑰設置（Free ChatGPT API 需要免費 API Key）
- 📊 實時進度條和狀態顯示
- ✅ 自動生成輸出文件名

### 命令行界面 (CLI)

#### 基本使用（使用 Free ChatGPT API - 默認）

```bash
# 默認使用 Free ChatGPT API，需要先設置 API Key
python pdf_translator.py input.pdf --service freegpt --api-key YOUR_FREE_API_KEY
```

**免費獲取 API Key**: 前往 [https://github.com/popjane/free_chatgpt_api](https://github.com/popjane/free_chatgpt_api) 領取免費 API Key

#### 使用 Google Translate

```bash
python pdf_translator.py input.pdf --service google
```

這會自動生成 `input_zh-TW.pdf` 文件。

#### 指定輸出文件名

```bash
python pdf_translator.py input.pdf -o output.pdf
```

#### 使用 Free ChatGPT API（推薦 - 免費）

```bash
# 使用默認設置（gpt-3.5-turbo-0125）
python pdf_translator.py input.pdf --service freegpt --api-key YOUR_FREE_API_KEY

# 指定其他模型
python pdf_translator.py input.pdf --service freegpt --api-key YOUR_FREE_API_KEY --model gpt-3.5-turbo

# 自定義 Base URL（通常不需要）
python pdf_translator.py input.pdf --service freegpt --api-key YOUR_FREE_API_KEY --base-url https://free.v36.cm/v1/
```

**免費 API Key 獲取地址**: [https://github.com/popjane/free_chatgpt_api](https://github.com/popjane/free_chatgpt_api)

#### 使用 OpenAI API（需要付費 API key）

```bash
python pdf_translator.py input.pdf --service openai --api-key YOUR_PAID_API_KEY
```

#### 使用 LocalAI

```bash
python pdf_translator.py input.pdf --service localai --base-url http://localhost:8080/v1 --model mistral-7b-instruct
```

#### 禁用自動語言檢測

如果您想禁用自動語言檢測（使用 Google Translate 的自動檢測模式）：

```bash
python pdf_translator.py input.pdf --no-auto-detect
```

## 打包成 Windows 可执行文件 (EXE)

如果您想将程序打包成独立的 Windows 可执行文件（.exe），可以使用 PyInstaller。

### 快速打包（推荐）

**方法一：使用批处理脚本（Windows）**

```bash
# 双击运行或在命令行执行
build_exe.bat
```

**方法二：使用 Python 脚本**

```bash
python build_exe.py
```

### 手动打包

1. 安装 PyInstaller：
```bash
pip install pyinstaller
```

2. 执行打包命令：
```bash
pyinstaller --name="PDFTranslator" --windowed --onefile --hidden-import=PySide6.QtCore --hidden-import=PySide6.QtGui --hidden-import=PySide6.QtWidgets --hidden-import=pdf_translator --hidden-import=deep_translator --hidden-import=langdetect --hidden-import=fitz --collect-all=PySide6 main.py
```

打包完成后，可执行文件位于 `dist\PDFTranslator.exe`

**详细说明请查看**: [BUILD_EXE.md](BUILD_EXE.md)

## 配置選項

可以編輯 `config.py` 文件來修改默認設置：

- `TRANSLATION_SERVICE`: 翻譯服務 ('google', 'freegpt', 'openai' 或 'localai')
- `OPENAI_API_KEY`: API 密鑰（FreeGPT/OpenAI/LocalAI 需要）
- `TRANSLATE_IMAGE_TEXT`: 是否翻譯圖片中的文字（需要 OCR）
- `OUTPUT_SUFFIX`: 輸出文件名後綴
- `API_DELAY`: API 調用之間的延遲時間

## 注意事項

1. **Free ChatGPT API（推薦）**:
   - 完全免費使用，無需付費
   - 需要前往 [https://github.com/popjane/free_chatgpt_api](https://github.com/popjane/free_chatgpt_api) 領取免費 API Key
   - 默認使用 `gpt-3.5-turbo-0125` 模型
   - API 地址：`https://free.v36.cm/v1/`
   - 支持流式響應，翻譯質量較好

2. **自動語言檢測**: 工具會自動檢測 PDF 中的文字語系，支援多種語言
   - 如果檢測失敗，會使用翻譯服務的自動檢測模式
   - 可以通過 `--no-auto-detect` 禁用自動檢測

3. **Google Translate**: 免費使用，但可能有速率限制

4. **OpenAI API**: 需要付費 API key，翻譯質量通常更好

5. **字體**: 工具會自動嘗試使用支援中文的字體，但如果原始 PDF 使用特殊字體，可能需要手動調整

6. **複雜格式**: 對於非常複雜的 PDF（如掃描件、複雜表格），可能需要額外的處理

## 範例

```bash
# 使用 Free ChatGPT API 翻譯 PDF 文件（推薦）
python pdf_translator.py activa_220_230_240_EN.pdf --service freegpt --api-key YOUR_FREE_API_KEY

# 使用 Google Translate 翻譯 PDF 文件
python pdf_translator.py activa_220_230_240_EN.pdf --service google

# 生成的文件: activa_220_230_240_EN_zh-TW.pdf
```

## 技術實現

- **PyMuPDF (fitz)**: 用於 PDF 操作和文本提取
- **PySide6**: 用於圖形化界面（基於 Qt，LGPL 許可證）
- **deep-translator**: 用於 Google Translate API（無 httpx 衝突問題）
- **langdetect**: 用於自動檢測文本語言
- **OpenAI API**: 用於高質量翻譯（FreeGPT/OpenAI/LocalAI，可選）

## 故障排除

### 問題：翻譯失敗
- 檢查網絡連接
- 確認 API key 是否正確（如果使用 FreeGPT/OpenAI/LocalAI）
- 對於 FreeGPT，確保 API Key 是有效的（前往 [https://github.com/popjane/free_chatgpt_api](https://github.com/popjane/free_chatgpt_api) 領取免費 Key）
- 檢查 PDF 文件是否損壞

### 問題：格式不正確
- 某些複雜的 PDF 格式可能無法完全保留
- 嘗試使用不同的翻譯服務

### 問題：中文顯示亂碼
- 確保系統支援繁體中文字體
- 檢查輸出 PDF 的編碼設置

### 問題：GUI 無法啟動
- 確保已安裝 PySide6：`pip install PySide6`
- 如果安裝失敗，嘗試：`pip install --upgrade pip` 然後重新安裝
- 在 Linux 上可能需要安裝額外的系統依賴：
  ```bash
  # Ubuntu/Debian
  sudo apt-get install libxcb-xinerama0 libxcb-cursor0
  
  # Fedora
  sudo dnf install libxcb xcb-util-cursor
  ```
- 如果 GUI 無法啟動，可以使用命令行模式：`python pdf_translator.py input.pdf`

## 版本更新記錄

### v1.4.0 (最新)
- ✅ **新增 Free ChatGPT API 支持**：使用免費的 ChatGPT API 進行翻譯
  - 完全免費，無需付費 API key
  - 默認使用 `gpt-3.5-turbo-0125` 模型
  - API 地址：`https://free.v36.cm/v1/`
  - 免費 API Key 獲取地址：https://github.com/popjane/free_chatgpt_api
  - 設置為命令行默認服務
  - GUI 界面中設為首選項
- ✅ 改進翻譯服務選擇邏輯
- ✅ 更新文檔和示例

### v1.3.0
- ✅ **新增圖形化界面 (GUI)**：使用 PySide6 提供現代化的圖形界面
  - 文件瀏覽器選擇輸入/輸出文件
  - 翻譯服務選擇（Google Translate / OpenAI / LocalAI）
  - API 密鑰和模型設置
  - 實時進度條和狀態顯示
  - 支援取消翻譯操作
- ✅ 新增 `main.py` 啟動器，支援 GUI 和 CLI 模式切換
- ✅ 改進用戶體驗和錯誤處理

### v1.2.0
- ✅ **新增自動語言檢測功能**：自動識別 PDF 中的文字語系
  - 支援多種語言（英文、日文、法文、德文、西班牙文等）
  - 智能跳過已為中文的內容
  - 提高翻譯準確度
- ✅ 添加語言檢測緩存機制
- ✅ 新增 `--no-auto-detect` 選項以禁用自動檢測

### v1.1.0
- ✅ **修復依賴衝突問題**：將 `googletrans` 替換為 `deep-translator`
  - 解決了與其他包的 `httpx` 版本衝突
  - `deep-translator` 使用 `requests`，相容性更好
  - 功能完全相同，仍然使用 Google Translate API
- ✅ 改進錯誤處理和兼容性
- ✅ 優化代碼結構，支援多種翻譯庫

### v1.0.0
- ✅ 初始版本發布
- ✅ 支援 PDF 翻譯並保留格式
- ✅ 支援 Google Translate 和 OpenAI API

## 授權

此工具僅供個人使用。請遵守相關翻譯服務的使用條款。

