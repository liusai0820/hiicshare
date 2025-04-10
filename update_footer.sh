#!/bin/bash

# 列出需要修改的文件
files=(
  "html-ppt/3-chain2.html"
  "html-ppt/3-chain3.html"
  "html-ppt/3-chain4.html"
  "html-ppt/4-aislide1.html"
  "html-ppt/4-aislide2.html"
  "html-ppt/4-aislide3.html"
)

# 新的footer内容
new_footer='<div class="footer">\n<div>AI赋能工作效率提升实践分享</div>\n</div>'

# 遍历并更新每个文件
for file in "${files[@]}"; do
  echo "处理文件: $file"
  # 使用sed替换footer内容
  sed -i '' -E 's|<div class="footer">[[:space:]]*<div>[^<]*</div>[[:space:]]*</div>|'"$new_footer"'|g' "$file"
  if [ $? -eq 0 ]; then
    echo "✅ 成功更新: $file"
  else
    echo "❌ 更新失败: $file"
  fi
done

echo "所有文件处理完成！" 