# 来源与更新说明

本项目已记下四个提问箱，所有主页均在 `sources.json`，后续更新以该文件为准。

| 账号 | 原站主页 | 当前已翻译公开回答 |
| --- | --- | --- |
| 🤤 · jaegyeolhabb | https://spin-spin.com/jaegyeolhabb | 21 |
| ryu…n · s0810s0527s | https://spin-spin.com/s0810s0527s | 720 |
| 미돌 · JMT_GOOD | https://spin-spin.com/JMT_GOOD | 2030 |

| 뜨 · biyo_yobi | https://spin-spin.com/biyo_yobi | 70 |

## 更新约定

可先运行 `python scripts/fetch_public.py s0810s0527s`（或替换为另一账号），抓取结果写入被Git忽略的 `work/spin-<handle>/`，不会直接覆盖已翻译网站。

完成翻译后，可运行 `python scripts/add_account.py <handle>`，或用 `--capture-dir` 显式指定抓取文件目录。该工具合并已存在的全部账号，保留其他账号数据；任何未翻译占位内容都会阻止正式构建。接口中存在空回答时，保留完整性报告并排除该项，不把它算作已回答问答。

1. 重新读取主页元数据与公开 `replyCounter`，核对账号是否存在以及当前公开计数。
2. 使用 `getRepliedLetters` 分页，`page` 是从0开始的页码，`limit=100`。持续到空页，保存最后一页/计数证据。
3. 以问题ID对照 `archives/<handle>.json`，仅翻译新增或正文变化的问答，保留已核对的旧译文及稳定链接。
4. 仅读取公开已回答内容；未公开、删除和订阅专享内容不在当前归档范围内。
5. 对齐每条问题和对应回答，保留图片与原文，未知CP简称/作品名不擅自补成人名。
6. 更新 `accounts.js`、该账号的JSON/Markdown、抓取报告及 `sources.json` 的时间和条数。不要覆盖其他账号的数据。
7. 检查多账号切换、搜索、排序、收藏隔离、锚点和手机布局后，提交同一仓库的 main 分支。GitHub Pages 自动部署。

主页和清单只是持久保存的来源记录，不会自动监控或更新；收到更新请求时再抓取。
