# 构建并生成 Pagefind 搜索索引
# 1. 先执行 Astro 构建，生成静态文件到 dist 目录
# 2. 然后运行 Pagefind，对 dist 目录的内容建立搜索索引
#    索引文件将输出到 dist/_pagefind/ 目录下

npm run build
npx pagefind --site dist --output-subdir ./_pagefind
