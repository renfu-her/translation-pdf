#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Translator GUI - PySide6 based graphical user interface
"""

import sys
import os
from pathlib import Path
from typing import Optional, Tuple

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QFileDialog, QProgressBar, QComboBox,
        QLineEdit, QTextEdit, QGroupBox, QMessageBox, QCheckBox
    )
    from PySide6.QtCore import Qt, QThread, Signal
    from PySide6.QtGui import QFont, QIcon
except ImportError:
    print("PySide6 is not installed. Install it with: pip install PySide6")
    sys.exit(1)

from pdf_translator import PDFTranslator


class TranslationWorker(QThread):
    """Worker thread for PDF translation to avoid blocking UI."""
    
    progress_updated = Signal(int, int)  # current_page, total_pages
    status_updated = Signal(str)  # status message
    finished = Signal(bool, str)  # success, message
    error_occurred = Signal(str)  # error message
    
    def __init__(self, translator: PDFTranslator, input_path: str, output_path: str, 
                 translate_images: bool = False):
        super().__init__()
        self.translator = translator
        self.input_path = input_path
        self.output_path = output_path
        self.translate_images = translate_images
        self._cancelled = False
        
    def cancel(self):
        """Cancel the translation process."""
        self._cancelled = True
        
    def run(self):
        """Run the translation in background thread."""
        try:
            import fitz
            import builtins
            
            if not os.path.exists(self.input_path):
                self.error_occurred.emit(f"Input file not found: {self.input_path}")
                return
            
            # Open PDF to get total pages for progress tracking
            doc = fitz.open(self.input_path)
            total_pages = len(doc)
            doc.close()
            
            # Override print function to capture status messages
            original_print = builtins.print
            status_messages = []
            
            def custom_print(*args, **kwargs):
                if args:
                    msg = ' '.join(str(arg) for arg in args)
                    status_messages.append(msg)
                    self.status_updated.emit(msg)
                original_print(*args, **kwargs)
            
            builtins.print = custom_print
            
            try:
                # Create a custom translate_pdf that reports progress
                self._translate_with_progress(total_pages)
                
                if not self._cancelled:
                    self.finished.emit(True, f"翻譯完成！\n輸出文件: {self.output_path}")
                else:
                    self.status_updated.emit("翻譯已取消")
                    
            finally:
                builtins.print = original_print
                
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def _translate_with_progress(self, total_pages: int):
        """Translate PDF with progress reporting."""
        import fitz
        
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Input file not found: {self.input_path}")
        
        self.status_updated.emit(f"正在打開 PDF: {self.input_path}")
        doc = fitz.open(self.input_path)
        
        try:
            for page_num in range(total_pages):
                if self._cancelled:
                    self.status_updated.emit("翻譯已取消")
                    return
                
                self.progress_updated.emit(page_num + 1, total_pages)
                self.status_updated.emit(f"處理中: 第 {page_num + 1}/{total_pages} 頁...")
                
                page = doc[page_num]
                
                # Extract text blocks
                text_blocks = self.translator.extract_text_blocks(page)
                
                # Translate each text block
                for block in text_blocks:
                    if self._cancelled:
                        return
                    
                    original_text = block["text"]
                    
                    # Skip if text is already in Chinese or contains only numbers/symbols
                    if self.translator._is_chinese(original_text) or not self.translator._needs_translation(original_text):
                        continue
                    
                    # Detect language for this text block
                    detected_lang = None
                    if self.translator.auto_detect_language:
                        detected_lang = self.translator.detect_language(original_text)
                        if detected_lang == 'zh':
                            continue  # Already Chinese, skip
                    
                    # Translate text with detected language
                    translated_text = self.translator.translate_text(original_text, source_lang=detected_lang)
                    
                    if translated_text != original_text:
                        # Replace text in PDF
                        self.translator._replace_text_in_page(page, block, translated_text)
                
                # Optionally translate text in images
                if self.translate_images:
                    self.translator._translate_image_text(page)
            
            if not self._cancelled:
                # Save translated PDF
                self.status_updated.emit(f"正在保存翻譯後的 PDF: {self.output_path}")
                doc.save(self.output_path)
                self.status_updated.emit("保存完成")
                
        finally:
            doc.close()


class PDFTranslatorGUI(QMainWindow):
    """Main GUI window for PDF Translator."""
    
    def __init__(self):
        super().__init__()
        self.translator: Optional[PDFTranslator] = None
        self.worker_thread: Optional[TranslationWorker] = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("PDF Translator - 繁體中文轉換工具")
        self.setMinimumSize(600, 500)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("PDF Translator")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        subtitle_label = QLabel("將 PDF 文件轉換為繁體中文")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #666;")
        main_layout.addWidget(subtitle_label)
        
        main_layout.addSpacing(10)
        
        # File selection group
        file_group = QGroupBox("文件選擇")
        file_layout = QVBoxLayout(file_group)
        
        # Input file
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("輸入 PDF:"))
        self.input_file_edit = QLineEdit()
        self.input_file_edit.setPlaceholderText("選擇 PDF 文件...")
        input_layout.addWidget(self.input_file_edit)
        self.input_file_btn = QPushButton("瀏覽...")
        self.input_file_btn.clicked.connect(self.select_input_file)
        input_layout.addWidget(self.input_file_btn)
        file_layout.addLayout(input_layout)
        
        # Output file
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("輸出 PDF:"))
        self.output_file_edit = QLineEdit()
        self.output_file_edit.setPlaceholderText("自動生成輸出文件名...")
        output_layout.addWidget(self.output_file_edit)
        self.output_file_btn = QPushButton("瀏覽...")
        self.output_file_btn.clicked.connect(self.select_output_file)
        output_layout.addWidget(self.output_file_btn)
        file_layout.addLayout(output_layout)
        
        main_layout.addWidget(file_group)
        
        # Translation settings group
        settings_group = QGroupBox("翻譯設置")
        settings_layout = QVBoxLayout(settings_group)
        
        # Translation service
        service_layout = QHBoxLayout()
        service_layout.addWidget(QLabel("翻譯服務:"))
        self.service_combo = QComboBox()
        self.service_combo.addItems(["Free ChatGPT API", "Google Translate", "OpenAI", "LocalAI"])
        self.service_combo.currentTextChanged.connect(self.on_service_changed)
        service_layout.addWidget(self.service_combo)
        service_layout.addStretch()
        settings_layout.addLayout(service_layout)
        
        # API Key (for OpenAI/LocalAI/FreeGPT)
        self.api_key_layout = QHBoxLayout()
        self.api_key_layout.addWidget(QLabel("API Key:"))
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("輸入 API 密鑰（FreeGPT/OpenAI/LocalAI 需要）")
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_layout.addWidget(self.api_key_edit)
        self.api_key_layout.setEnabled(True)  # Enabled for FreeGPT (default)
        settings_layout.addLayout(self.api_key_layout)
        
        # Base URL (for LocalAI/FreeGPT)
        self.base_url_layout = QHBoxLayout()
        self.base_url_layout.addWidget(QLabel("Base URL:"))
        self.base_url_edit = QLineEdit()
        self.base_url_edit.setPlaceholderText("例如: https://free.v36.cm/v1/")
        self.base_url_edit.setText("https://free.v36.cm/v1/")  # Default for FreeGPT
        self.base_url_layout.addWidget(self.base_url_edit)
        self.base_url_layout.setEnabled(True)  # Enabled for FreeGPT (default)
        settings_layout.addLayout(self.base_url_layout)
        
        # Model name (for OpenAI/LocalAI/FreeGPT)
        self.model_layout = QHBoxLayout()
        self.model_layout.addWidget(QLabel("模型名稱:"))
        self.model_edit = QLineEdit()
        self.model_edit.setPlaceholderText("例如: gpt-4o-mini")
        self.model_edit.setText("gpt-4o-mini")  # Default for FreeGPT
        self.model_layout.addWidget(self.model_edit)
        self.model_layout.setEnabled(True)  # Enabled for FreeGPT (default)
        settings_layout.addLayout(self.model_layout)
        
        # Options
        options_layout = QVBoxLayout()
        self.auto_detect_check = QCheckBox("自動檢測語言")
        self.auto_detect_check.setChecked(True)
        options_layout.addWidget(self.auto_detect_check)
        
        self.translate_images_check = QCheckBox("翻譯圖片中的文字（需要 OCR）")
        self.translate_images_check.setChecked(False)
        options_layout.addWidget(self.translate_images_check)
        
        settings_layout.addLayout(options_layout)
        
        main_layout.addWidget(settings_group)
        
        # Progress group
        progress_group = QGroupBox("進度")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("準備就緒")
        self.status_label.setWordWrap(True)
        progress_layout.addWidget(self.status_label)
        
        main_layout.addWidget(progress_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.translate_btn = QPushButton("開始翻譯")
        self.translate_btn.setMinimumHeight(40)
        self.translate_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.translate_btn.clicked.connect(self.start_translation)
        button_layout.addWidget(self.translate_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_translation)
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Connect input file change to auto-generate output path
        self.input_file_edit.textChanged.connect(self.auto_generate_output_path)
        
    def on_service_changed(self, text: str):
        """Handle translation service selection change."""
        is_openai = text == "OpenAI"
        is_localai = text == "LocalAI"
        is_freegpt = text == "Free ChatGPT API"
        is_google = text == "Google Translate"
        
        # Enable/disable API key field
        self.api_key_layout.setEnabled(is_openai or is_localai or is_freegpt)
        
        # Enable/disable base URL field (for LocalAI and FreeGPT)
        self.base_url_layout.setEnabled(is_localai or is_freegpt)
        
        # Enable/disable model field
        self.model_layout.setEnabled(is_openai or is_localai or is_freegpt)
        
        # Set default values for FreeGPT
        if is_freegpt:
            if not self.base_url_edit.text():
                self.base_url_edit.setText("https://free.v36.cm/v1/")
            if not self.model_edit.text():
                self.model_edit.setText("gpt-4o-mini")
        elif is_localai:
            if not self.base_url_edit.text():
                self.base_url_edit.setText("http://localhost:8080/v1")
        elif is_google:
            # Clear API-related fields for Google Translate
            self.base_url_edit.clear()
            self.model_edit.clear()
        
    def select_input_file(self):
        """Open file dialog to select input PDF."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "選擇輸入 PDF 文件",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        if file_path:
            self.input_file_edit.setText(file_path)
            
    def select_output_file(self):
        """Open file dialog to select output PDF."""
        default_path = self.output_file_edit.text() or self.input_file_edit.text()
        if default_path:
            default_dir = os.path.dirname(default_path)
            default_name = os.path.basename(default_path)
        else:
            default_dir = ""
            default_name = ""
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "選擇輸出 PDF 文件",
            os.path.join(default_dir, default_name),
            "PDF Files (*.pdf);;All Files (*)"
        )
        if file_path:
            self.output_file_edit.setText(file_path)
    
    def auto_generate_output_path(self, input_path: str):
        """Auto-generate output path from input path."""
        if not input_path:
            self.output_file_edit.clear()
            return
            
        if self.output_file_edit.text() and not self.output_file_edit.text().startswith(
            os.path.dirname(input_path) if os.path.dirname(input_path) else ""
        ):
            # User has manually set output path, don't override
            return
            
        input_path_obj = Path(input_path)
        if input_path_obj.exists():
            output_path = str(input_path_obj.parent / f"{input_path_obj.stem}_zh-TW.pdf")
            self.output_file_edit.setText(output_path)
    
    def validate_inputs(self) -> Tuple[bool, str]:
        """Validate user inputs."""
        input_path = self.input_file_edit.text().strip()
        if not input_path:
            return False, "請選擇輸入 PDF 文件"
        
        if not os.path.exists(input_path):
            return False, f"輸入文件不存在: {input_path}"
        
        if not input_path.lower().endswith('.pdf'):
            return False, "輸入文件必須是 PDF 格式"
        
        output_path = self.output_file_edit.text().strip()
        if not output_path:
            return False, "請選擇輸出 PDF 文件路徑"
        
        service = self.service_combo.currentText()
        if service in ["OpenAI", "Free ChatGPT API"]:
            api_key = self.api_key_edit.text().strip()
            if not api_key:
                if service == "OpenAI":
                    return False, "使用 OpenAI 服務需要提供 API Key"
                elif service == "Free ChatGPT API":
                    return False, "使用 Free ChatGPT API 服務需要提供 API Key。請前往 https://github.com/popjane/free_chatgpt_api 領取免費 API Key"
        
        return True, ""
    
    def start_translation(self):
        """Start the PDF translation process."""
        # Validate inputs
        valid, error_msg = self.validate_inputs()
        if not valid:
            QMessageBox.warning(self, "輸入錯誤", error_msg)
            return
        
        # Get settings
        input_path = self.input_file_edit.text().strip()
        output_path = self.output_file_edit.text().strip()
        
        service_map = {
            "Google Translate": "google",
            "OpenAI": "openai",
            "LocalAI": "localai",
            "Free ChatGPT API": "freegpt"
        }
        service = service_map[self.service_combo.currentText()]
        
        api_key = self.api_key_edit.text().strip() if self.api_key_layout.isEnabled() else None
        base_url = self.base_url_edit.text().strip() if self.base_url_layout.isEnabled() else None
        model_name = self.model_edit.text().strip() if self.model_layout.isEnabled() else None
        auto_detect = self.auto_detect_check.isChecked()
        translate_images = self.translate_images_check.isChecked()
        
        # Create translator
        try:
            self.translator = PDFTranslator(
                translator_service=service,
                api_key=api_key,
                auto_detect_language=auto_detect,
                base_url=base_url
            )
            if model_name:
                self.translator.model_name = model_name
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"初始化翻譯器失敗: {str(e)}")
            return
        
        # Create worker thread
        self.worker_thread = TranslationWorker(
            self.translator,
            input_path,
            output_path,
            translate_images
        )
        
        # Connect signals
        self.worker_thread.progress_updated.connect(self.update_progress)
        self.worker_thread.status_updated.connect(self.update_status)
        self.worker_thread.finished.connect(self.on_translation_finished)
        self.worker_thread.error_occurred.connect(self.on_translation_error)
        
        # Update UI
        self.translate_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("開始翻譯...")
        
        # Start translation
        self.worker_thread.start()
    
    def cancel_translation(self):
        """Cancel the ongoing translation."""
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "確認取消",
                "確定要取消翻譯嗎？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.worker_thread.cancel()
                self.status_label.setText("正在取消...")
    
    def update_progress(self, current: int, total: int):
        """Update progress bar."""
        progress = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(progress)
        self.status_label.setText(f"處理中: 第 {current}/{total} 頁")
    
    def update_status(self, message: str):
        """Update status label."""
        self.status_label.setText(message)
    
    def on_translation_finished(self, success: bool, message: str):
        """Handle translation completion."""
        self.translate_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        if success:
            QMessageBox.information(self, "完成", message)
            self.progress_bar.setValue(100)
            self.status_label.setText("翻譯完成！")
        else:
            self.status_label.setText("翻譯已取消")
    
    def on_translation_error(self, error_msg: str):
        """Handle translation error."""
        self.translate_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        QMessageBox.critical(self, "翻譯錯誤", f"翻譯過程中發生錯誤:\n{error_msg}")
        self.status_label.setText(f"錯誤: {error_msg}")


def main():
    """Main entry point for GUI application."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = PDFTranslatorGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

