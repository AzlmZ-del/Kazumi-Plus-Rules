# Kazumi-Plus-Rules

个人自用的 [Kazumi](https://github.com/Predidit/Kazumi) 视频源（规则）仓库，
配套魔改版 App [**Kazumi Plus**](https://github.com/AzlmZ-del/Kazumi-Plus)。

> **这不是官方项目，也没有向上游贡献的打算。** 规则只按自己手头的源维护，
> 失效、改版、停更都属正常。

## 声明

**一、仓库是个人自用。** 与上游作者、官方仓库无关，不代表任何官方立场。
收录标准就是「我自己在用的源」，不追求覆盖面，也不保证任何一条长期可用。
站点关站、接口改版、风控升级导致规则失效时，不承诺修复时间。

**二、配套使用的是一个魔改版 App。** 基于 [`Predidit/Kazumi`](https://github.com/Predidit/Kazumi)
二次修改，fork 后改名为 [`AzlmZ-del/Kazumi-Plus`](https://github.com/AzlmZ-del/Kazumi-Plus)，
安装后显示为 **Kazumi Plus**。相对官方版多了这些功能，全部是个人需求驱动的，
**没有向上游提 PR**：

- **多规则仓库**：可同时挂多个第三方仓库，规则条目记录来源，目录聚合、同名去重、
  按仓库地址路由下载，另有独立的管理页
- **规则登录与令牌**：规则可声明登录接口，凭据本地保存、令牌缓存，401 自动重登；
  规则还能声明播放接口，绕开 WebView 直接取直链
- **详情页**：剧集页签、已播出/未播出区分、讨论行内展开或独立页面、「内部打开」
- **Bangumi**：R18 条目搜索、无中文名条目可选保留、镜像取不到时回落官方接口
- **独立 applicationId**：修改版与官方版可同时安装

**三、不提供任何视频内容。** 规则只描述公开站点的搜索、章节、播放接口，
仓库里没有任何视频文件、字幕或账号。

**四、别商用，别到处传。**

## 怎么用

在 Kazumi 里打开 **设置 → 规则仓库 → 管理规则仓库 → ＋**，填这个地址：

```
https://raw.githubusercontent.com/AzlmZ-del/Kazumi-Plus-Rules/main/
```

也可以直接粘贴 `index.json` 的完整地址，两种写法等价。

> 仓库必须保持**公开**：Kazumi 是匿名拉取 `raw.githubusercontent.com`，私有仓库读不到。

> 推送后 `raw.githubusercontent.com` 有 `max-age=300` 的 CDN 缓存，**最多要等 5 分钟**
> 才能在客户端看到新规则。别以为没推上去又重推一遍。

## 收录的源

| 规则名 | 站点 | 模式 | 状态 |
|---|---|---|---|
| `omofuni` | <https://omofun.in> | XPath | ✅ 正常 |
| `omofuna` | <https://www.omofuna.com> | XPath | ⚠️ 站点有安全验证，首次访问需在 WebView 里过验证 |
| `月之祠` | <https://www.moonci.com> | API 搜索 + XPath 章节 | ✅ 正常 |
| `次元城` | <https://www.cycani.org> | API | ⚠️ 搜索与章节可用，播放地址需登录（401） |

`月之祠` 的搜索走站点自带的 `index.php/ajax/suggest` 接口（`searchMode: api`），
章节列表用 XPath 解析 `hl-plays-list`，播放仍走 WebView + 原生播放器。

`次元城` 是纯 API 模式规则，`searchMode` / `chapterMode` 均为 `api`，
不走 WebView。它的 `auth` 段指向 `POST /api/auth/login`，`@username` /
`@password` 是占位符，首次使用时 Kazumi 会弹登录框要求填真实账号；
登录后取 `$.data.token`，接口返回 401 时自动重新登录。

`omofuna` 的搜索页会被「系统安全验证」拦截，规则里已带验证码配置
（`captchaDetectValue: mx-mac_msg_jump`）。Kazumi 会走 WebView 验证流程，
但这套流程依赖站点前端，站点改版就可能失效。

## 更新记录

下表由 `tools/gen_index.py` 自动维护（数据来自 `index.json`），别手改。

<!-- rules-table:start -->
| 规则名 | 版本 | 最后更新 |
| --- | --- | --- |
| omofuna | 1.0 | 2026-10-21 |
| omofuni | 1.2 | 2026-10-21 |
| 月之祠 | 1.1 | 2026-10-21 |
| 次元城 | 2.0 | 2026-10-21 |
<!-- rules-table:end -->

## 与官方版的兼容性

`index.json` 与规则文件的**基础格式**完全按上游约定写，官方原版也能挂这个仓库。
但下面这些字段只有 **Kazumi Plus** 认识，官方版会直接忽略：

| 字段 | 用途 |
|---|---|
| `auth` | 规则登录流程、`tokenPath`、`refreshOnStatus` |
| `searchApiConfig` / `chapterApiConfig` | API 模式取数（`searchMode: api`） |
| `episodePage` / `play` | 播放直链接口 |
| `antiCrawlerConfig` | 验证码流程 |

所以 `omofuni`、`omofuna` 这类 XPath 规则在官方版上能正常用；
`次元城` 这种纯 API 规则**必须配 Kazumi Plus**，官方版装了也搜不出东西。

## 仓库结构

```
.
├── index.json            # 规则索引（自动生成，不要手改）
├── omofuni.json          # 规则文件，文件名必须等于 name 字段
├── omofuna.json
├── 月之祠.json
├── 次元城.json
├── tools/gen_index.py    # 索引生成脚本
└── .github/workflows/    # 推送后自动重算索引
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

   它会扫描所有规则文件，重写 `index.json`，同时刷新上面「更新记录」那张表。
   `lastUpdate` 取该文件的最后一次 git 提交时间（未提交的文件回退到修改时间）。
   这样重新 clone 仓库不会把所有时间戳一起刷新。
3. 提交并推送。推上去之后 GitHub Actions 会再跑一次脚本兜底，
   `index.json` 有变化就自动提交。

只校验不写盘：

```bash
python tools/gen_index.py --check
```
