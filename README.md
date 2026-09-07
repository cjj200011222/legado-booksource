# 阅读书源收藏

阅读 (Legado) APP 书源合集。**订阅 all.json 一条链接即可获取全部书源，更新自动同步。**

## 📱 订阅入口（聚合文件，加新书源永不换链接）

| 线路 | 链接 |
|---|---|
| 直连 | `https://raw.githubusercontent.com/cjj200011222/legado-booksource/master/all.json` |
| jsDelivr | `https://cdn.jsdelivr.net/gh/cjj200011222/legado-booksource@master/all.json` |
| jsDelivr 备用 | `https://fastly.jsdelivr.net/gh/cjj200011222/legado-booksource@master/all.json` |
| jsDelivr 备用2 | `https://gcore.jsdelivr.net/gh/cjj200011222/legado-booksource@master/all.json` |
| ghfast 镜像 | `https://ghfast.top/https://raw.githubusercontent.com/cjj200011222/legado-booksource/master/all.json` |

**使用**：阅读 APP → 书源管理 → 右上角 ⋮ → **网站订阅** → 填任一链接。以后仓库更新书源，APP 内点「更新订阅」即可，无需换链接。

## 单源文件（需要单独导入某个时用）

| 书源 | 文件 | 说明 |
|---|---|---|
| 起点中文网·全能版 | [书源/起点中文网·全能版.json](书源/起点中文网·全能版.json) | 搜索/发现/目录/正文全功能；`[女]+书名` 搜女频 |
| 起点系·发现可用版 | [书源/起点系·发现可用版.json](书源/起点系·发现可用版.json) | 21个起点发现可用源（webView过WAF+M站majax），含467/385/343分类大发现页 |
| 知轩藏书 | [书源/知轩藏书书源.json](书源/知轩藏书书源.json)(书源/知轩藏书书源.json) | 书讯发现源（TXT 下载站，无在线正文） |
| 书源精简版 | [书源/书源精简版.json](书源/书源精简版.json) | 起点系 7 个功能不重复的可用源 |
| 书仓优质自筛·清洗版 | [书源/书仓优质自筛·清洗版.json](书源/书仓优质自筛·清洗版.json) | 129 源复筛保留 43 源（起点移动站/聚合API/常规站/JS搜索/发现专用/成人向），2026-09-07 批量实测 |

## 如何添加新书源

1. 把新书源 JSON（单个对象或数组均可）放进 **`书源/`** 目录
2. 提交推送：`git add 书源/ && git commit -m "添加xxx书源" && git push`
3. GitHub Actions 自动重新聚合 `all.json`
4. 手机阅读 APP 里点「更新订阅」完成同步

本地手动聚合（不依赖 Actions）：`powershell -File build-all.ps1`

## 维护说明

- 起点全能源数据全部走 `m.qidian.com`（PC 站已 202 反爬失效）；规则细节见各备忘文档
- 起点 VIP 章节未接官方登录，未登录只能读免费章/试读
- 聚合按 `bookSourceUrl` 去重（先到先得，按文件名排序）
- 更新时间：2026-09-06
