# PDF 繁體中文轉換工具

這是一個可以將 PDF 文件轉換為繁體中文的工具，同時保留原始的格式、字體、佈局和圖片。

## 功能特點

- ✅ 保留原始 PDF 格式（字體、大小、顏色、佈局）
- ✅ **自動檢測原始語言**：智能識別 PDF 中的文字語系（英文、日文、法文等）
- ✅ 自動翻譯為繁體中文
- ✅ 支援 Google Translate 和 OpenAI API
- ✅ 翻譯緩存機制，避免重複翻譯
- ✅ 保持圖片和圖形不變
- ✅ 智能識別中文內容，跳過已翻譯的文本

## 安裝依賴

### 基本安裝（使用 Google Translate，推薦）

```bash
pip install -r requirements.txt
```

這個版本使用 `deep-translator` 庫，避免了與其他包的 `httpx` 版本衝突問題。

### 如果需要使用 OpenAI API

```bash
pip install openai
```

**注意**：OpenAI 是可選依賴。工具默認使用 Google Translate（免費），無需 API key。

## 使用方法

### 基本使用

```bash
python pdf_translator.py input.pdf
```

這會自動生成 `input_zh-TW.pdf` 文件。

### 指定輸出文件名

```bash
python pdf_translator.py input.pdf -o output.pdf
```

### 使用 OpenAI API（需要 API key）

```bash
python pdf_translator.py input.pdf --service openai --api-key YOUR_API_KEY
```

### 禁用自動語言檢測

如果您想禁用自動語言檢測（使用 Google Translate 的自動檢測模式）：

```bash
python pdf_translator.py input.pdf --no-auto-detect
```

## 配置選項

可以編輯 `config.py` 文件來修改默認設置：

- `TRANSLATION_SERVICE`: 翻譯服務 ('google' 或 'openai')
- `OPENAI_API_KEY`: OpenAI API 密鑰
- `TRANSLATE_IMAGE_TEXT`: 是否翻譯圖片中的文字（需要 OCR）
- `OUTPUT_SUFFIX`: 輸出文件名後綴
- `API_DELAY`: API 調用之間的延遲時間

## 注意事項

1. **自動語言檢測**: 工具會自動檢測 PDF 中的文字語系，支援多種語言
   - 如果檢測失敗，會使用 Google Translate 的自動檢測模式
   - 可以通過 `--no-auto-detect` 禁用自動檢測
2. **Google Translate**: 免費使用，但可能有速率限制
3. **OpenAI API**: 需要付費 API key，翻譯質量通常更好
4. **字體**: 工具會自動嘗試使用支援中文的字體，但如果原始 PDF 使用特殊字體，可能需要手動調整
5. **複雜格式**: 對於非常複雜的 PDF（如掃描件、複雜表格），可能需要額外的處理

## 範例

```bash
# 翻譯 PDF 文件
python pdf_translator.py activa_220_230_240_EN.pdf

# 生成的文件: activa_220_230_240_EN_zh-TW.pdf
```

## 技術實現

- **PyMuPDF (fitz)**: 用於 PDF 操作和文本提取
- **deep-translator**: 用於 Google Translate API（無 httpx 衝突問題）
- **langdetect**: 用於自動檢測文本語言
- **OpenAI API**: 用於高質量翻譯（可選）

## 故障排除

### 問題：翻譯失敗
- 檢查網絡連接
- 確認 API key 是否正確（如果使用 OpenAI）
- 檢查 PDF 文件是否損壞

### 問題：格式不正確
- 某些複雜的 PDF 格式可能無法完全保留
- 嘗試使用不同的翻譯服務

### 問題：中文顯示亂碼
- 確保系統支援繁體中文字體
- 檢查輸出 PDF 的編碼設置

## 版本更新記錄

### v1.2.0 (最新)
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

