# 翻译规范与术语表（article-translate-publish）

完整翻译技术文章时遵循。术语表按"首次出现附英文、之后纯中文"执行；同一篇文章内必须自洽。

## 核心术语表

| 英文 | 译法 | 备注 |
|---|---|---|
| agent | 智能体 | 全篇统一，不译"代理" |
| proactive agent | 主动式智能体 | |
| classifier | 分类器 | 安全语境不译"分级器" |
| safeguard | 防护措施 / 保障机制 | 复数 safeguards → 防护措施 |
| safety training | 安全训练 | |
| research preview | 研究预览 | 产品发布阶段术语 |
| prompt injection | 提示注入 | |
| red team | 红队 | 动词 red-teamed → 接受红队测试 |
| bug bounty | 漏洞悬赏 | |
| penetration test | 渗透测试 | |
| threat model | 威胁模型 | |
| trust boundary | 信任边界 | |
| shadow traffic | 影子流量 | |
| safe harbor | 安全港 | 加引号 |
| responsible disclosure | 负责任披露 | |
| credential(s) | 凭证 | 不译"凭据" |
| sign-in token | 登录令牌 | |
| password / cookie | 密码 / cookie | cookie 保留英文 |
| one-time card | 一次性（虚拟）卡 | |
| placeholder | 占位符 | |
| virtual machine | 虚拟机 | |
| memory | 记忆 | 智能体语境 |
| task list | 任务列表 | |
| approval cadence | 请求批准的频率 / 审批节奏 | 按语境 |
| approval fatigue | 审批疲劳 | 加引号 |
| User-Agent (header) | User-Agent 标头 | 保留英文 |
| auto mode classifier | auto mode 分类器 | 产品功能名，保留英文 |
| Managed Agents | Claude Managed Agents | 产品名不译 |
| discretion | 谨慎（处理） | "handled with discretion" → 以谨慎态度处理 |
| off-limits | 被禁止 | |
| phishing | 钓鱼（攻击） | |
| wipe | 抹除 / 抹掉 | "wipes everything" → 抹掉一切 |
| steer (mid-task) | 引导 | |
| routine | 例行任务 | |
| brief | 简报 / 早报 | 按语境 |

## 风格规则

1. **结论先行、结构对齐**：原文章节顺序、列表层级、图号一一对应，不重排。
2. **长句拆短**：英文多重复句按中文习惯拆成 2–3 句；破折号用"——"。
3. **引号用中文全角**："…"，避免与 JSON 转义冲突（payload 里中文引号无需转义）。
4. **数字、单位、代码、命令、URL、产品名**保留原文。
5. **被动转主动**，消除翻译腔（如 "it shows you" → "它会向你展示"）。
6. **图注处理**：能拿到原图就嵌图 + 中文图注（"图 N｜……"）；拿不到则保留"（图 N 说明：……）"文字描述，不得删图注信息。
7. **附录英文原文必须完整**：按章节分 2–4 个附录章；英文里的双引号在 payload JSON 字符串中要 `\"` 转义。
8. **版权声明**：文末固定带"翻译整理自 XX 官网，仅供学习交流；原文版权归原作者所有" + 原文链接。
9. 拿不准的术语在文中首次出现时保留英文括注，如"一次性密钥（single-use key）"。

## 已发布样例

- 《Claude Duet 安全、隐私与权限机制全解析》（2026-10-25， Anthropic 官网 2026-10-23 文章全译 + 英文原文三章附录 + 5 张官网原图）。
