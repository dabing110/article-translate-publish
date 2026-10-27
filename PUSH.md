# 推送到 GitHub（PAT 到位后执行）

本机 `github.com` 的 git 与网页通道被封，只有 `api.github.com` 放行，因此不走 `git push`，改用 PAT + Contents API。

## 1. 准备 PAT（一步到位链接）

打开下面这个链接，`public_repo` scope 与备注名都已预填，直接滚到底点 **Generate token**：

**https://github.com/settings/tokens/new?scopes=public_repo&description=article-translate-publish**

手动路径：GitHub 右上角头像 → **Settings** → 左侧最下方 **Developer settings** → **Personal access tokens → Tokens (classic)** → **Generate new token (classic)**。

| 项 | 填什么 |
|---|---|
| Note | `article-translate-publish` |
| Expiration | 选 **7 days**（最短够用；推完就 Revoke） |
| Scopes | 只勾 **`public_repo`** —— 一项即可，不要勾 `repo`（那会给出私有仓库权限） |

`public_repo` 的含义是「读写你名下的公开仓库」，正好覆盖建仓库 + 传文件，是这件事的最小权限。

生成后**立刻复制**（关掉页面就再也看不到）：形如 `ghp_xxxxxxxxxxxx`。

三条安全约定：

- 只在当前 shell 用**环境变量**传入，不要拼进命令行——会进 shell 历史
- 不要贴进任何文件、聊天记录或仓库
- 推完回到同一页面点 **Delete / Revoke**

> 备选：想进一步缩小范围可用 fine-grained token（<https://github.com/settings/personal-access-tokens/new>），但它要求先指定具体仓库，而本流程是推送时才新建仓库，所以 classic 更顺手。

## 2. 预演文件清单

```bash
export PATH="/usr/bin:/bin:/c/Windows/System32:$PATH"
"C:/Users/admin/.workbuddy/binaries/python/versions/3.13.12/python.exe" \
  "C:/Users/admin/.workbuddy/skills/github-push-via-api/scripts/push_via_api.py" \
  --src "C:/Users/admin/WorkBuddy/2026-10-25-09-39-57/github-dist/article-translate-publish" \
  --repo article-translate-publish --dry-run
```

确认清单里**没有** `references/published-index.md`。

## 3. 正式推送

token 用 `-s` 静默读入（不回显、不进 shell 历史），别直接 `export GH_TOKEN="ghp_xxx"`：

```bash
export PATH="/usr/bin:/bin:/c/Windows/System32:$PATH"
read -s -r -p "Paste PAT: " GH_TOKEN && echo && export GH_TOKEN
"C:/Users/admin/.workbuddy/binaries/python/versions/3.13.12/python.exe" \
  "C:/Users/admin/.workbuddy/skills/github-push-via-api/scripts/push_via_api.py" \
  --src "C:/Users/admin/WorkBuddy/2026-10-25-09-39-57/github-dist/article-translate-publish" \
  --repo article-translate-publish \
  --desc "技术文章处理成稿、嵌图封面、推送微信公众号草稿箱的可复用流水线"
```

跑完输出里会有仓库地址。

## 4. 加 topics（可选）

```bash
curl -s -X PUT -H "Authorization: Bearer $GH_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/dabing110/article-translate-publish/topics \
  -d '{"names":["wechat","translation","automation","ai-agent","skill"]}'
```

## 5. 收尾

- 校验无损：比对远端 blob sha 与本地 `git hash-object`
- Revoke token
