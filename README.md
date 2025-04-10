# HTML幻灯片拆分工具

这个工具用于将多页HTML幻灯片拆分成单独的HTML文件，每个文件包含一个幻灯片。

## 功能特点

- 将多页HTML演示文稿拆分为单独的HTML文件
- 保留原始HTML的样式和结构
- 自动为拆分后的文件命名（原文件名+页码）
- 支持批量处理多个文件

## 安装

1. 确保已安装Python 3
2. 安装依赖项：

```bash
pip install -r requirements.txt
```

## 使用方法

### 处理特定文件

```bash
python split_html_slides.py 路径/到/你的文件.html
```

### 处理多个文件

```bash
python split_html_slides.py 文件1.html 文件2.html 文件3.html
```

### 指定输出目录

```bash
python split_html_slides.py -o 输出目录 文件.html
```

### 处理预设的目标文件

```bash
python split_html_slides.py --all
```

这将处理`html-ppt`目录中的特定文件（2-lobe.html, 3-chain.html, 4-aislide.html, 5-xie.html）。

## 示例

将`html-ppt/2-lobe.html`拆分为单独的幻灯片：

```bash
python split_html_slides.py html-ppt/2-lobe.html
```

这将在同一目录中创建`2-lobe1.html`、`2-lobe2.html`等文件。 