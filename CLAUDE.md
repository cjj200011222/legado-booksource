# 项目记忆：阅读(Legado)书源制作

工作目录 `g:\cursorprogram\阅读书源制作`。全局约定（中文回复/中文文档名、WebSearch 禁用改走 tavily 等）见全局 CLAUDE.md，此处不重复。

## 真机 Web 服务调试（判定书源唯一精准手段，必须优先用）

用户手机上的阅读 APP 开着 Web 服务。手机和电脑同一局域网、APP「我的→Web 服务」开启时，可直接连真机调试书源——**判定"XX源能不能用"一律走这里，禁止用本机 curl 猜死活**。

- **HTTP API**：`http://192.168.5.10:1122/`（IP 可能随网络变化，先访问导航页确认 `<title>Legado web 导航</title>`）
  - `GET /getBookshelf` — 书架
  - `GET /getBookSource?url={URL编码的书源URL}` — 单源查询（全量 getBookSources 会超时，不用）
  - `GET /getChapterList?url={bookUrl}` / `GET /getBookContent?url={bookUrl}&index=1` — 目录/正文
  - 未配对路径返回占位文本 `web/xxx` 是前端路由，不是报错
- **WebSocket 调试（核心）**：`ws://192.168.5.10:1123/bookSourceDebug`
  - 发送 `{"key":"搜索词","tag":"书源URL"}`，接收逐步调试日志（搜索→详情→目录→正文每步的 ┌获取xxx/└结果），以 1000 正常关闭结束
  - 判定：日志含 `搜索页解析完成`/`目录列表解析完成`/`正文页解析完成` 即对应环节可用；`列表大小:N` 看结果数；`Exception` 行看死因
  - Python：`pip install websockets`，asyncio + `websockets.connect()` 发 JSON 收文本流
- **本机注意**：访问局域网 IP 必须 `curl --noproxy '*'`（本机代理 127.0.0.1:7890 会拦）
- **实时管理手机源**（改完即生效，无需订阅更新）：
  - `POST /saveBookSource`（**单对象**；数组会被当多源解析失败）写入/覆盖单个源
  - `POST /saveBookSources`（数组）批量写入，同 URL 旧源自动覆盖；54 源分 6 批每批 10 个约几十秒
  - `POST /deleteBookSources`（数组 `[{"bookSourceUrl": "…"}]`）删除
  - 删除时按**真机上实际存在的 URL 精确匹配**——源名可能带前导空格/emoji（` 起点中文网·全能版` 就因此漏删过一次），最稳做法：先 `GET /getBookSources` 拉全量（37MB/约 5 秒，手机 6800+ 源时才能成功，短超时会失败）拿准确清单再删，删后复查
  - 全量拉取偶发 chunked 超时：重试即可；确认单个源存在与否用 `getBookSource?url=` 单查（快且稳）
- **为什么**：起点 PC 站有 WAF JS 挑战（probe.js 202 页），本机 curl 永远拿不到数据，但真机 webView 执行 JS 就能过——**本机拿不到 ≠ 源不能用**；只有真机调试也失败才是真死

## 项目现状（2026-09-07）

- 仓库：`cjj200011222/legado-booksource`（GitHub），订阅入口 `all.json` 由 Actions 自动聚合 `书源/` 目录（本地可跑 `build-all.ps1`）
- 订阅链接（jsDelivr 有 12-24h 缓存，急用 raw/ghfast）：
  - `https://raw.githubusercontent.com/cjj200011222/legado-booksource/master/all.json`
- 书源文件：起点系·发现可用版(13源) / 书源精简版(5源) / 书仓优质自筛·清洗版(41源) / 知轩藏书(1源)
- 全能版聚合源已废弃（用户决定），git 历史里仍有
- 真机复测结论：🥥起点中文网/起点(部分可看)/🎉修复版/优+/搜书专用/书荒完本全链路可用；编辑发现版/vip章节/男女频标签/0714/同人小说网真死（详见《起点全能版书源制作备忘.md》）

## 关键经验

- Legado 规则字段名必须官方（coverUrl 不是 cover），写错静默丢弃零报错
- 书源 JS 规则用 Rhino 引擎实测（`els.each` 在 Rhino 不存在——for 循环替代）；先从真机验证过的源复制结构再改
- 起点可用通道：M 站 m.qidian.com 纯 HTTP / wxapp 目录 API 免登录 / majax 发现 API 需 `_csrfToken` 拼 URL / PC 站需 webView
- git 提交前检查临时测试文件（_t.json 等）勿入仓库
