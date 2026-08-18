# 同步说明

上游是 [mattpocock/skills](https://github.com/mattpocock/skills)。只拷 `.claude-plugin/plugin.json` 里列出的 promoted skill，不带 `deprecated/`、`in-progress/`、`misc/`。

`scripts/sync.py` 会：

1. 浅克隆或 `fetch` 到 `.cache/mattpocock-skills/`（gitignored）
2. 删掉本仓 `skills/` 后按清单逐个 `copytree`
3. 重写 `.cursor-plugin/plugin.json` 和 `sources.lock.json`
4. 复制上游 `LICENSE` 为 `LICENSE.mattpocock`

`sources.lock.json` 钉死 SHA、版本和 skill 列表，方便核对当天同步了什么。
