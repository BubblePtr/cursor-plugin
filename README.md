# cursor-plugin

个人用的 Cursor 本地插件。现在只 vendor [mattpocock/skills](https://github.com/mattpocock/skills) 里 `engineering` 和 `productivity` 两个目录（MIT），方便自己装、自己每天同步。不做分发。

## 本机安装

```bash
./scripts/install.sh
```

软链到 `~/.cursor/plugins/local/cursor-plugin`，然后 **Developer: Reload Window**。

## 同步

```bash
python3 scripts/sync.py          # 拉上游 main，覆盖 vendor 的 skill
python3 scripts/test_sync.py     # 同步逻辑的单元测试
```

每天 09:00（本机时区）由 launchd 跑 `scripts/daily-sync.sh`：同步、有变更就提交并尝试 push。GitHub Action 在 01:00 UTC（北京时间 09:00）做同样的事，笔记本没开机时远端也会更新。

```bash
./scripts/install-launchd.sh     # 注册本机定时任务
```

## 许可

本仓包装层按 MIT。vendored skill 的版权仍归 Matt Pocock，见 `LICENSE.mattpocock`。
