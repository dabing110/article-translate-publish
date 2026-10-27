# article-translate-publish

把技术文章**处理成稿 → 嵌图 → 生成封面 → 推送到微信公众号草稿箱**的可复用流水线。以 skill 形式交付，配四个实测脚本。

含两条支线：

- **A 翻译类**：外文文章完整中译、附英文原文。
- **B 原创整理类**：参考资料 + 自己的笔记/实践，自己立论点成文。

最初为翻译 Anthropic 工程博客而写，后来逐步扩展到四类原文来源（官网博客 / 机构报告 / arXiv 论文 / GitHub 仓库），已实际跑通 20+ 篇公众号稿件。

## 它解决什么

手工做一遍这件事会遇到一堆文档里查不到的坑：

- X/Twitter 链接在 GFW 下抓不到，得绕到官网原文
- 正文图不嵌进去，公众号里只剩一行图注文字
- 封面传本地路径能建稿、发布时报 `invalid media_id`
- 单篇正文超过约 22KB，服务端 5 秒超时直接失败
- 正文图超过 2 张，发布转异步，而且**没有状态查询接口**
- 写完发现错别字——但没有改稿接口，只能整篇重建重发

这些都写进了 `SKILL.md`，并附故障速查表。

## 目录结构

```
SKILL.md                              两条支线 + 七步流程 + 来源矩阵 + 取图技巧 + 平台硬约束 + 故障速查
references/translation-style.md       术语表与翻译风格规则（A 类）
references/original-article-playbook.md  原创整理类规范：立论点、结构重排、配图三来源、封面叠字（B 类）
scripts/extract_figures.py            抓原文 HTML，按出现顺序提取配图清单（url + alt + 上下文）
scripts/compress_images.py            转 JPEG、长边 ≤1200px、压缩到 <1MB
scripts/pad_cover_235.py              封面 pad 成公众号 2.35:1（边缘延展，不裁切）
scripts/validate_payload.py           建稿前自检（标题字数、摘要字数、chapters 结构、封面直链）
```

## 安装

```bash
cp -r article-translate-publish ~/.workbuddy/skills/
```

或放到你的 Claude Code / Cursor skills 目录下。

## 七步流程

| 步 | 做什么 | 关键约束 |
|---|---|---|
| 1 | 定位原文 | X 直连失败不重试，改用搜索找官网原文 |
| 2 | 抓全文 | 按 h2/h3/p/li/table/figure 切分，保留图注与表格 |
| 3 | 完整中译 | 章节层级一一对应，文末附英文原文节选 |
| 4 | 生成封面 | pad 到 2.35:1，走上传通道拿公网直链 |
| 5 | 嵌入原图 | 单张 ≤1MB，`image.url` 写相对路径 |
| 6 | 建稿 | title ≤30 字、abstract ≤100 字、单篇 ≤约 22KB |
| 7 | 推草稿箱 | **只到草稿箱，群发一律人工** |

## 原文来源矩阵

| 来源 | 抓法 |
|---|---|
| 官网博客 | curl 抓 HTML 按标签切分，配图在自家 CDN |
| 机构报告 + 博客 | 博客与论文都抓；配图常在 `cdn.prod.website-files.com` |
| arXiv 论文 | `arxiv.org/html/<id>v1`；图是 SVG，需渲染成 PNG |
| GitHub 仓库 | **github.com 被封，但 api.github.com 放行且免 PAT** |

GitHub 一路的三条经验写在 `SKILL.md`：图片走 api 的 raw 通道、失败换 jsdelivr、以及**必须核对作者 profile**（转述的国籍、身份经常是错的）。

## 脱敏说明

这是公开仓库版本，已移除：

- 公众号 account_id（改为 `<YOUR_ACCOUNT_ID>` 占位）
- 已发布稿件的 info_id / publish_id 索引（该文件只留本地）
- 公众号名称

发布平台侧的接口细节（字数上限、超时、异步规则）属于可公开的服务行为，保留，因为这正是复用价值所在。

## 许可

MIT。版权归 dabing110。翻译稿的原文版权归各自作者，本仓库只收录流程与脚本。
