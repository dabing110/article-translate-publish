---
name: article-translate-publish
description: 技术文章发布到微信公众号，含两条支线。①翻译类：外文技术文章完整中译并发布。当用户给出 X/Twitter 推文链接、英文官网文章链接，或说"翻译这篇发公众号 / 完整翻译并发布 / 附上英文原文"时使用。②原创整理类：用户给参考资料+自己的笔记/截图，或先把方案做成了 md，再说"整理成公众号 / 整理成一个公众号，主题XX"。覆盖全流程：GFW 下定位原文、分类处理、配图（官网原图/自绘/实跑生成）、封面生成、言序建稿并推送到公众号草稿箱。触发词：翻译发布、公众号翻译、外文文章翻译、整理成公众号、原创整理、方案转文章、translate and publish。
agent_created: true
---

# 技术文章发布到公众号（article-translate-publish）

本技能有**两条支线**，动手前先判断走哪条：

| 支线 | 输入特征 | 骨架来源 | 规范 |
|---|---|---|---|
| **A 翻译类** | 给出一个外文原文链接 | 照搬原文结构 | 本文 Step 1–6 + `references/translation-style.md` |
| **B 原创整理类** | 参考资料 + 自己的笔记/截图；或先做了方案 md 再要成文；或只给主题 | **自己立论点、自己排结构** | Step 3–6 + **`references/original-article-playbook.md`（必读）** |

B 类最容易做砸的方式，就是把方案文档换个标题直接搬上去——那是清单体，读者记不住任何一条。

翻译类：把外文技术文章**完整翻译**成中文、附英文原文、嵌入官网配图，发布到微信公众号草稿箱。2026-10-25 基于 Claude Duet 安全文章的真实发布流程沉淀。适用输入：X 推文链接（正文常在被引用的官网链接里）、官网文章 URL、或"把某主题的文章翻译发公众号"。

## 总流程（7 步）

1. 定位原文（X 直连失败 → 搜索兜底）
2. WebFetch 抓全文
3. 完整中译 + 文末附英文原文
4. 生成封面并上传
5. 提取并嵌入官网原图
6. 建稿（create_article）
7. 发布草稿箱（publish_article）+ 验证

每步的脚本用 `${CLAUDE_SKILL_DIR}/scripts/` 引用；翻译规范见 `references/translation-style.md`。

## Step 1 定位原文

- WebFetch 直接抓 x.com / twitter.com 在沙箱代理下会 `fetch failed`，**不要重试**。
- 改用 WebSearch：搜「文章主题 + 官方站点名」（如 `Claude Duet Anthropic security privacy`），从结果里认领官网原文 URL（claude.com / openai.com 等官方域）。
- 拿到 URL 后 WebFetch 全文，prompt 明确要求：**逐字提取完整原文，保留所有章节标题与图注，不要摘要**。

## Step 2 翻译

完整翻译，不摘要、不删段。规则（详见 references/translation-style.md）：

- 章节结构、列表层级、图号与原版一一对应
- 术语查术语表保持统一；专有名词首次出现附英文（如"研究预览（research preview）"）
- 原文配图有 URL 就嵌原图（Step 5）；确实拿不到图时保留"（图 N 说明：……）"文字描述占位
- 文末附**完整英文原文**：按章节分 2–4 个附录章（如"附录 · 英文原文（上/中/下）"），避免单章过长
- 文末注明：出处链接 + "翻译整理自 XX 官网，仅供学习交流；原文版权归原作者所有"

**长文拆系列**（用户明确要求或原文超过约 1.5 万英文词时主动建议）：

- 按原文逻辑结构均分 3–5 篇，每篇文末附**该篇对应的**英文原文（不是全文重复）
- 每篇 title 带期号：如"XXX 全解析①：……""XXX 全解析④上：……"；intro/摘要里交代系列导航（第 X 篇讲什么、共几篇）
- 封面：一张主封面 + PIL 期号徽章派生（底部居中胶囊：第 X 篇 · 副题 + n/N），避免每篇重新生成消耗积分
- 拆篇后单篇 chapters 必须 ≤约 15KB（服务端 5s 超时红线）；篇内附录英文原文同样只收该篇范围

## Step 3 封面

1. ImageGen 生成封面。**会消耗积分（约 5–10 点），先用文字告知用户再生成**。
   prompt 模板：极简科技编辑风 + 品牌色暖底 + 主题元素（盾牌/机器人/锁等）+ 顶部大号标题「产品名」+ 下方小字中文副题；尺寸 `1536x1024`。中文标题可正常渲染。
2. 生成后必须 Read 检查：文字乱码/畸形就重生成。
3. **标题文字的两种做法，按长度选**：

   - 短标题（英文产品名 + 一行短副题）→ 让 ImageGen 直接渲染，省事。
   - **中文长标题 / 有主副两行 → 让 ImageGen 只出背景（prompt 写明「不出现任何文字或字母」），标题用 PIL 叠上去**。ImageGen 渲染长中文句会出现字形错乱、副标题挤到标题、位置不可控；PIL 叠加则字形绝不会错、位置精确可控、改字不用重新生成（省积分）。详见 `references/original-article-playbook.md` 第四节，含描边写法与两个已踩的坑（两行间距、模糊延展的竖直接缝）。

4. pad 成公众号标准封面比例 2.35:1——**pad 不裁切**（标题在顶部，中心裁切会丢题）：

```bash
python "${CLAUDE_SKILL_DIR}/scripts/pad_cover_235.py" --in <生成的图> --out cover.jpg
```

4. `get_upload_channel(scene="cover")` → curl multipart 上传 → 取返回的 `data.url` 作 `cover_img`：

```bash
curl -s -X POST "<upload_url>" -F "file=@cover.jpg"
```

## Step 4 嵌入配图

**默认要嵌图**——真实项目里用户发现"图片没有嵌入文章里"只有文字描述，这是本技能重点防御点。

翻译类只用官网原图；**原创整理类通常不够，得三路凑：官方图 / 自绘示意图 / 自己实跑生成**，其中「实跑生成」说服力最强（图注能写死真实数字）。做法见 `references/original-article-playbook.md` 第三节。

```bash
# 1. 抓原文 HTML，提取配图清单（url + alt + 上下文，按出现顺序）
python "${CLAUDE_SKILL_DIR}/scripts/extract_figures.py" --url <原文URL> --out figs_manifest.json [--download figs/]

# 2. 压缩：转 JPEG、长边≤1200px、单张<1MB（言序正文图硬限）
python "${CLAUDE_SKILL_DIR}/scripts/compress_images.py" --dir figs/ --max-kb 1000

# 3. 逐张上传：get_upload_channel(scene="body") → curl -F "file=@..." → 记录 file_path
```

要点：

- **上传通道是一次性的**：`get_upload_channel` 返回的 ticket 只能传一张图，第二张会返回 `ret=10001 上传通道无效或已过期`。每张图都要重新申请通道（循环调工具即可，5 分钟有效期不是瓶颈）。
- 下载**逐张顺序 curl**；本环境并行后台 curl 不可靠（会丢文件）。
- 正文 `image` 块的 url **写 file_path**（形如 `mcp/20261025/xxx.jpg`），不写公网 url——言序工具文档明确推荐，服务端自行解析；封面才用公网 url。
- 插图位置与原文图号一致；每图配一条中文图注 paragraph（"图 N｜……"），替换原来的纯文字图注段。
- 上传完 `curl -I` 验证所有图片 URL 全部 200 再建稿（异步发布的成败取决于图片可达性）。
- **代码/配置示例（YAML、JSON）用图片呈现**：用 PIL 渲染成深色代码风图片（等宽字体 consola、行号、语法着色、长边 1200px）后上传嵌入。一是公众号无 code 块、段落保留缩行不可靠；二是图片化彻底避开 JSON 转义地狱。参考实现见本次 evals 系列的 render_yaml.py 模式。

## Step 5 建稿

**先把 payload 写成 JSON 文件再校验，最后才粘贴进 create_article**（手写 10KB JSON 转义极易出错）：

```bash
python "${CLAUDE_SKILL_DIR}/scripts/validate_payload.py" --payload article.json
```

payload 为扁平结构（`title`/`abstract`/`cover_img`/`intro`/`chapters` 同级，勿套 `content`）；每章 `{"type":"chapter","title":...,"blocks":[...]}`；块仅 `paragraph`/`image`/`list`/`table`，章节不嵌套，content 纯文本。

言序硬约束（全部踩过坑）：

| 项 | 规则 |
|---|---|
| title | ≤30 字，超限直接被拒且不报具体长度 |
| abstract | ≤100 字 |
| chapters | **传 JSON 字符串**（曾遇原生数组被拒 must be array,string）；chapters 是"字符串套 JSON"两层结构，工具参数里英文直引号必须写三层转义（反斜杠+反斜杠+引号）——只写两层会让服务端二次解析失败，报"chapters 须为 JSON 数组字符串"。**2026-10-25 实测：工具签名已支持原生数组，5 篇均以原生数组（`[{"type":"chapter",...}]`）建稿成功，优先用原生数组彻底避开转义问题** |
| 单篇体量 | create_article 服务端约 5s 超时：chapters 超约 20KB 会 PacRpcClient timeout。长文必须拆篇，单篇 chapters 控制在约 15KB 内 |
| cover_img | 必须上传通道的公网直链；**传本地路径建稿成功但 publish 报 invalid media_id** |
| 正文图 | 单张 ≤1MB；超过 2 张时 publish 转异步 |
| 建稿前 | **通读全文查错别字**——言序无改稿接口，建稿后的错字只能整篇重建重发，旧稿滞留需用户后台手删 |

## Step 6 发布草稿箱

| 工具 | 要点 |
|---|---|
| `list_wechat_accounts` | 确认账号；只有一个号时 publish 的 account_id 可省略 |
| `list_theme_styles` | 系统 6 套主题（neon/terminal/blackgold/magma/cobalt/violet） |
| `publish_article` | 传 info_id + account_id + theme_id |

- **本账号 `default_theme_id=null`，必须显式传 theme_id**；AI/大模型/前沿科技话题用 `neon`（霓虹脉冲），深度稿可用 `blackgold`（曜金质感）。
- 同步成功标志：`status=1` + `media_id`。
- 正文图 >2 张 → `async=true, status=0 pending`，**言序无发布记录查询工具**。兜底：`curl -I` 确认图片全部 200 后，告知用户稍后到草稿箱确认。
- **群发红线**：任何自动化只推到草稿箱；群发永远由用户在公众号后台人工点击，每次发布后都要提醒。

## 账号发布约定（换成你自己的公众号）

- account_id：`<YOUR_ACCOUNT_ID>`（首次用 `list_wechat_accounts` 取回后填这里，不要提交真实值）
- 主题：无默认 → 显式 theme_id（AI 话题 neon）
- 言序**无草稿删除/更新接口**：重复建稿会在草稿箱留多份；改稿 = 整篇重建 + 重发 + 用户后台删旧稿。重跑前先确认是否已建稿。
- 旧稿清理只能用户在公众号后台操作，交付时明确告知哪篇是旧稿（按发布时间与 info_id 区分）。
- **发布后建议维护一份本地索引**（标题 / info_id / publish_id / 同步或异步 / 配图数 / 原文来源）：用于回答「哪篇发过、用的什么主题、哪篇异步待确认」。该索引含账号标识，**不要提交到公开仓库**。

## B 类：原创整理类支线

**完整规范见 `references/original-article-playbook.md`。** A 类的 Step 3–6（封面 / 配图 / 建稿 / 发布）在 B 类同样适用，差异集中在前面三步：

| 环节 | A 翻译类 | B 原创整理类 |
|---|---|---|
| 骨架 | 照搬原文章节 | **自己立论点 + 自己排结构** |
| 资料 | 一篇主原文 | 多篇资料 + 自己的实践/笔记/方案 md |
| 配图 | 官网原图 | 官方图 + 自绘 + **实跑生成**（三类都要声明出处） |
| 封面 | ImageGen 直接渲染标题 | **ImageGen 只出背景，PIL 叠中文标题** |
| 文末 | 附英文原文 | **参考文献逐条列 + 配图出处逐张交代 + 时间锚点 + 非官方声明** |

三条最容易翻车的（详见 playbook）：

1. **没论点就动笔** → 写成清单体。检验法：把论点放 intro 首句，每章都要能回答「这章怎么支撑它」，答不上来就删。
2. **结构照搬方案目录** → 方案目录是给执行者看的（分工具、分步骤），文章要有推进感（立论 → 证明 → 转折 → 落地 → 划界）。务必把「证明闭环成立」的证据提前到第 3 章左右。
3. **数字来源不分等级** → 官方数据 / 实测数据 / 个人估算混在一起。第三类**必须声明「为个人估算，非实测、不构成承诺」**，漏了就是最危险的一类错误。

另外 B 类**没有原文兜底**，发布前必须逐项核：版本号、发布日期、开源许可、工具能力边界、人名地名。写错一个版本号，整篇可信度归零。

## 原文来源矩阵（2026-10-27 补）

同一套流水线，来源已经跑通四类。**先判断来源类型，再用对应抓法**：

| 来源 | 抓法 | 已验证案例 |
|---|---|---|
| 官网博客（anthropic.com / claude.com / openai.com） | `curl -sL` 抓 HTML，按 h2/h3/p/li/table/figure 切分；配图在自家 CDN（assets.claude.com 等） | Claude Duet、evals、agents |
| 机构报告 + 博客（如 aisi.gov.uk） | 博客比论文好读，两者都抓；配图常托管在 `cdn.prod.website-files.com` | ReproBAIT |
| arXiv 论文 | `curl -sL https://arxiv.org/html/<id>v1`（见下方取图技巧） | ReproBAIT |
| **GitHub 仓库** | **github.com 网页被 GFW 封，但 api.github.com 放行且免 PAT** | Hallmark、JSON-SCADA |

### GitHub 仓库抓法（重点）

```bash
# 单个文件原始内容（含图片二进制）
curl -sL -H "Accept: application/vnd.github.raw" \
  https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref=master -o out.bin

# 仓库元数据：星数、语言、license、created_at、pushed_at、最近 release
curl -s https://api.github.com/repos/{owner}/{repo}
curl -s https://api.github.com/repos/{owner}/{repo}/releases/latest
```

- 要读的文件通常是：`README.md`、`SKILL.md`、`docs/*.md`、截图目录（README 里 `<img src>` 直接给出路径）。
- **图片下载走 api 的 raw 通道**；失败时改走 `cdn.jsdelivr.net/gh/{owner}/{repo}@{sha}/{path}`（jsdelivr 在白名单里），`raw.githubusercontent.com` 在沙箱常超时，别作为首选。
- 文件名带空格：URL 里写 `%20`，落盘改成下划线，避免后续 shell 出错。
- **事实必须核对作者 profile**（`https://api.github.com/users/{login}`）：用户转述的二手信息经常有错——JSON-SCADA 那次口述是「加拿大工程师」，profile 实际是巴西。存疑时正文只写中性表述，并在交付时回问用户。

### 开源项目类文章的通用结构

是什么 → 技术栈/依赖版本 → 硬战绩（用 README 自述的真实数据） → 架构 → 功能或协议表 → 界面截图（带中文图注） → **冷静看局限**（alpha、维护者人数、资源占用、许可证传染性、roadmap 未完成项） → 五分钟上手（docker 一行命令 / 在线 demo） → 附录英文原文节选。

## 取图来源技巧（2026-10-27 补）

- **arXiv HTML 全文**：`curl -sL https://arxiv.org/html/<id>v1 -o x.html`，正文用正则抽文本、`<table>` 转 `|` 分隔行（见 reprobait-article/extract.py）。
- **arXiv 的图是 SVG `<object>`**，路径相对 `/html/<id>/`：`https://arxiv.org/html/<id>v1/<figure>.svg`。**不是** `.../<id>v1/<id>v1/x.svg`，`.png` 一律 404。
- **SVG → PNG**：用 playwright 渲染，别截图（清晰度差）。读 SVG 头部的 `width="548pt" height="197pt"`，按 3.2 倍设 viewport + `device_scale_factor=2`，白底元素截图；产物再走 compress_images.py。模板见 reprobait-article/render_svg.py。
- **机构博客**（如 aisi.gov.uk）配图常托管在 `cdn.prod.website-files.com`，直接 curl 下载即可；博客正文往往比论文更好读，两者一起抓。

## 故障速查

| 现象 | 处置 |
|---|---|
| WebFetch X/Twitter 链接 failed | GFW 封锁，不重试；WebSearch 定位官网原文 |
| 封面文字乱码 / 副标题挤到标题 | 中文长标题改走 PIL 叠加（ImageGen 只出背景） |
| 正文中露出 `**` 星号 | 言序不解析 markdown 粗体；在构建脚本里 `sed -i 's/\*\*//g'` 清一遍再生成 payload |
| 自绘示意图中文变豆腐块 | 别用「SVG 嵌文字 + 浏览器渲染」，直接 PIL 画并指定字体文件 |
| 封面模糊延展有竖直接缝 | paste 后对拼接边缘做羽化过渡 |
| publish 报 `invalid media_id` | 封面用了本地路径；改走上传通道公网直链 |
| 建稿被拒不报原因 | 九成是 title>30 或 abstract>100；先跑 validate_payload.py |
| 建稿报"chapters 须为 JSON 数组字符串" | 工具参数里 chapters 的英文直引号转义层数不对（应三层）；或参数被传输层截断——重传时逐字核对 |
| create_article 报 `PacRpcClient request timed out`（5000ms） | 单篇 chapters 太大（>约20KB）；拆篇后重建，单篇控制在约 15KB 内 |
| 异步发布后无法确认状态 | curl -I 验证图片 200，请用户稍后在草稿箱确认 |
| `mcp__yanxu__*` 工具搜不到 | 会话 MCP 未建连，重试无效；降级写待发状态，请用户在 GUI 侧发一句话触发重连后补跑 |

## 安全边界

- 只读公开网页；翻译稿标注出处与版权，声明仅供学习交流。
- 外部写入仅限公众号草稿箱：不群发、不回复、不删除任何已有内容。
- 图片只用原文官网配图或自生成封面，不用第三方有版权风险的素材。
