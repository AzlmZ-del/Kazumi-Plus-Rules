# KazumiRules

个人维护的 [Kazumi](https://github.com/Predidit/Kazumi) 视频源（规则）仓库。

## 怎么用

在 Kazumi 里打开 **设置 → 规则仓库 → 管理规则仓库 → ＋**，填这个地址：

```
https://raw.githubusercontent.com/AzlmZ-del/KazumiRules/main/
```

也可以直接粘贴 `index.json` 的完整地址，两种写法等价。

> 仓库必须保持**公开**：Kazumi 是匿名拉取 `raw.githubusercontent.com`，私有仓库读不到。

## 收录的源

| 规则名 | 站点 | 模式 | 状态 |
|---|---|---|---|
| `Lanerc` | <https://omofun.in> | XPath | ✅ 正常 |
| `Omofun` | <https://www.omofuna.com> | XPath | ⚠️ 站点有安全验证，首次访问需在 WebView 里过验证 |
| `次元城` | <https://www.cycani.org> | API | ⚠️ 搜索与章节可用，播放地址需登录（401） |

`次元城` 是纯 API 模式规则，`searchMode` / `chapterMode` 均为 `api`，
不走 WebView。它的 `auth` 段指向 `POST /api/auth/login`，`@username` /
`@password` 是占位符，首次使用时 Kazumi 会弹登录框要求填真实账号；
登录后取 `$.data.token`，接口返回 401 时自动重新登录。

`Omofun` 的搜索页会被「系统安全验证」拦截，规则里已带验证码配置
（`captchaDetectValue: mx-mac_msg_jump`）。Kazumi 会走 WebView 验证流程，
但这套流程依赖站点前端，站点改版就可能失效。

## 仓库结构

```
.
├── index.json            # 规则索引（自动生成，不要手改）
├── Lanerc.json           # 规则文件，文件名必须等于 name 字段
├── Omofun.json
└── tools/gen_index.py    # 索引生成脚本
```

Kazumi 的约定：

- `index.json` 是一个 **JSON 数组**，每条形如
  `{name, version, useNativePlayer, antiCrawlerEnabled, author, lastUpdate}`
- 单条规则的文件名必须等于它的 `name` 字段，即 `<name>.json`，与 `index.json` 同目录
- `lastUpdate` 是**毫秒**时间戳，用来判断本地规则是否需要更新

## 新增或修改一条规则

1. 在根目录放一个 `<name>.json`，`name` 字段与文件名保持一致
2. 改完跑一次：

   ```bash
   python tools/gen_index.py
   ```

   它会扫描所有规则文件，重写 `index.json`，`lastUpdate` 取该文件的最后一次
   git 提交时间（未提交的文件回退到修改时间）。这样重新 clone 仓库不会把
   所有时间戳一起刷新。
3. 提交并推送。推上去之后 GitHub Actions 会再跑一次脚本兜底，
   `index.json` 有变化就自动提交。

只校验不写盘：

```bash
python tools/gen_index.py --check
```

## 免责声明

本仓库只收录公开可访问的站点规则，不含任何视频内容。规则失效、站点关闭、
接口变更都属正常，随缘维护。
