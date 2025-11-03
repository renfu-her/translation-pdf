# 打包成 Windows 可执行文件 (EXE) 说明

## 方法一：使用自动构建脚本（推荐）

### Windows 批处理文件

直接双击运行 `build_exe.bat`，或在命令行执行：

```bash
build_exe.bat
```

### Python 脚本

```bash
python build_exe.py
```

## 方法二：手动使用 PyInstaller

### 1. 安装 PyInstaller

```bash
pip install pyinstaller
```

### 2. 打包命令

**单文件模式（推荐，一个独立的 exe 文件）：**

```bash
pyinstaller --name="PDFTranslator" ^
    --windowed ^
    --onefile ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtGui ^
    --hidden-import=PySide6.QtWidgets ^
    --hidden-import=pdf_translator ^
    --hidden-import=deep_translator ^
    --hidden-import=langdetect ^
    --hidden-import=fitz ^
    --collect-all=PySide6 ^
    main.py
```

**目录模式（更快启动，但包含多个文件）：**

```bash
pyinstaller --name="PDFTranslator" ^
    --windowed ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtGui ^
    --hidden-import=PySide6.QtWidgets ^
    --hidden-import=pdf_translator ^
    --hidden-import=deep_translator ^
    --hidden-import=langdetect ^
    --hidden-import=fitz ^
    --collect-all=PySide6 ^
    main.py
```

### 3. 使用 spec 文件（高级）

如果您需要自定义打包选项，可以修改 `PDFTranslator.spec` 文件，然后运行：

```bash
pyinstaller PDFTranslator.spec
```

## 打包后的文件位置

打包完成后，可执行文件位于：

- **单文件模式**: `dist\PDFTranslator.exe`
- **目录模式**: `dist\PDFTranslator\PDFTranslator.exe`

## 注意事项

1. **文件大小**: 单文件模式会生成较大的 exe（通常 50-100MB），因为包含了所有依赖
2. **首次启动**: 首次启动可能较慢（几秒钟），因为需要解压临时文件
3. **杀毒软件**: 某些杀毒软件可能会误报，这是正常现象（PyInstaller 打包的程序常见）
4. **Windows 版本**: 建议在 Windows 10 或更高版本上测试

## 测试打包后的程序

1. 将 `PDFTranslator.exe` 复制到新文件夹
2. 双击运行，测试 GUI 功能
3. 尝试翻译一个 PDF 文件

## 分发

打包后的 `PDFTranslator.exe` 可以独立分发，不需要安装 Python 或其他依赖。

## 故障排除

### 问题：打包失败

- 确保所有依赖都已安装：`pip install -r requirements.txt`
- 确保 PyInstaller 版本是最新的：`pip install --upgrade pyinstaller`
- 检查是否有模块导入错误

### 问题：exe 运行时报错 "ModuleNotFoundError"

- 在打包命令中添加 `--hidden-import=模块名`
- 检查是否有遗漏的依赖

### 问题：exe 启动后立即关闭

- 使用目录模式打包（不使用 `--onefile`），查看错误信息
- 或者添加 `--console` 参数查看控制台输出：
  ```bash
  pyinstaller --name="PDFTranslator" --console --onefile main.py
  ```

### 问题：exe 文件太大

- 使用目录模式可以减少文件大小
- 使用 UPX 压缩（已在 spec 文件中启用）

## 可选：添加图标

如果您有图标文件（.ico），可以在打包时添加：

```bash
pyinstaller --name="PDFTranslator" --windowed --onefile --icon=icon.ico main.py
```

将 `icon.ico` 放在项目根目录。

