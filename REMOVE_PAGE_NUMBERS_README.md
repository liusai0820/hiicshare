# HTML页码移除工具

这个工具用于移除HTML文件中的页码和导航相关代码，使得HTML文件更适合进行合并或其他处理。

## 功能特点

- 移除所有页码元素（具有`page-number`类的div）
- 移除页面导航控制元素（具有`page-controls`类的div）
- 移除导航按钮（带有`onclick="prevSlide()"`或`onclick="nextSlide()"`属性的元素）
- 移除页码span元素（具有`current-page`或`total-pages`类的span）
- 移除页码相关的JavaScript函数（包含`nextSlide`、`prevSlide`或`updatePagination`的脚本）

## 安装

1. 确保已安装Python 3
2. 安装依赖项：

```bash
pip install beautifulsoup4
```

## 使用方法

### 处理单个文件（覆盖原文件）

```bash
python remove_page_numbers.py 路径/到/你的文件.html
```

### 处理单个文件（输出到新文件）

```bash
python remove_page_numbers.py -o 输出文件.html 输入文件.html
```

### 处理目录中的所有HTML文件

```bash
python remove_page_numbers.py -d 目录路径
```

### 处理目录中的所有HTML文件并输出到新目录

```bash
python remove_page_numbers.py -d 输入目录 -o 输出目录
```

### 处理html-ppt目录中的所有HTML文件

```bash
python remove_page_numbers.py --all
```

### 处理html-ppt目录中的所有HTML文件并输出到新目录

```bash
python remove_page_numbers.py --all -o 输出目录
```

## 示例

移除`html-ppt/2-lobe1.html`中的页码：

```bash
python remove_page_numbers.py html-ppt/2-lobe1.html
```

移除`html-ppt`目录中所有HTML文件的页码：

```bash
python remove_page_numbers.py --all
```

## 与HTML拆分工具结合使用

这个工具可以与之前创建的HTML幻灯片拆分工具结合使用：

1. 首先使用`split_html_slides.py`将多页HTML拆分为单页文件
2. 然后使用`remove_page_numbers.py`移除拆分后文件中的页码元素
3. 最后，这些没有页码的单页文件可以更容易地合并或进行其他处理 