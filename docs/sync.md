# 同步说明

上游是 [mattpocock/skills](https://github.com/mattpocock/skills)。**只同步 `skills/engineering/` 和 `skills/productivity/`** 下带 `SKILL.md` 的目录，不带 `deprecated/`、`in-progress/`、`misc/`。上游 `plugin.json` 只用来读版本号等元数据，不再当 allowlist。

`scripts/sync.py` 会：

1. 浅克隆或 `fetch` 到 `.cache/mattpocock-skills/`（gitignored）
2. 扫上述两个桶，删掉本仓 `skills/` 后逐个 `copytree`
3. 重写 `.cursor-plugin/plugin.json` 和 `sources.lock.json`
4. 复制上游 `LICENSE` 为 `LICENSE.mattpocock`

`sources.lock.json` 钉死 SHA、版本和 skill 列表，方便核对当天同步了什么。
