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

下表由 `tools/gen_index.py` 自动维护（版本与日期来自 `index.json`，
站点与模式来自 `tools/rule_meta.json`），别手改。

<!-- rules-table:start -->
| 规则名 | 站点 | 模式 | 版本 | 最后更新 |
| --- | --- | --- | --- | --- |
| AGE | <https://www.agedm.io> | XPath | 1.5 | 2026-10-21 |
| Akianime | <https://www.akianime.cc> | WebView + XPath | 1.4 | 2026-10-21 |
| omofuna | <https://www.omofuna.com> | XPath | 1.0 | 2026-10-21 |
| omofuni | <https://omofun.in> | XPath | 1.2 | 2026-10-21 |
| 七色番 | <https://www.7sefun.top> | WebView + XPath | 1.3 | 2026-10-21 |
| 月之祠 | <https://www.moonci.com> | API 搜索 + XPath 章节 | 1.1 | 2026-10-21 |
| 次元城 | <https://www.cycani.org> | API | 2.0 | 2026-10-21 |
| 稀饭动漫（新） | <https://next.xifanacg.com> | API | 1.1 | 2026-10-21 |
| 稀饭动漫（旧） | <https://dm1.xfdm.pro> | WebView + XPath | 1.1 | 2026-10-21 |
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
