# cursor-plugin

个人用的 Cursor 本地插件。现在只 vendor [mattpocock/skills](https://github.com/mattpocock/skills) 里 `engineering` 和 `productivity` 两个目录（MIT），方便自己装、自己每天同步。不做分发。

## 安装（只在 Cursor 里）

不要把 `/add-plugin ...` 发给 Agent，那只是普通对话，不会装插件。

1. 打开侧边栏 **Customize**
2. 在 Plugins 里找 **Add** / 从 GitHub 添加
3. 贴 `https://github.com/BubblePtr/cursor-plugin`
4. 范围选 **User**，装完后 **Developer: Reload Window**

若斜杠菜单里出现 **Cursor 内置的** `/add-plugin`（不是发给模型的文本），也可以选它再贴同一个 URL。聊天输入 `/grill-me`、`/tdd`、`/ask-matt` 能点到即成功。

Personal 计划从 GitHub 加的插件会钉在当时的 commit 上，仓库每天同步不一定会进已装副本。要换新版本，先在 Customize 里卸掉再加一次。

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
