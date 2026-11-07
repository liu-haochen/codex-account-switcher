# Codex Account Switcher

A small local GUI for switching between multiple Codex accounts without going through OAuth/2FA every time.

一个本地的小工具，用来在多个 Codex 账号之间快速切换，避免每次重新走 OAuth/2FA 登录。

## Features / 功能

- Show the current Codex account / 显示当前账号
- List saved account snapshots / 列出已保存的账号快照
- Save the current account / 保存当前账号
- One-click switch, with automatic backup of the previous state / 一键切换，自动备份当前状态
- Delete snapshots and open the accounts folder / 删除快照、打开账号目录

## How it works / 原理

Codex stores its login state in `~/.codex/auth.json`, including a `refresh_token` issued by OpenAI.

This tool simply saves each account's `auth.json` as a snapshot and replaces that file when switching. Requests still go directly to the official OpenAI endpoint — there is no proxy, no interception, and no data collection.

Codex 把登录状态保存在 `~/.codex/auth.json`，其中包含 OpenAI 官方签发的 `refresh_token`。本工具只把不同账号的 `auth.json` 保存成快照，切换时替换该文件。请求仍然直连 OpenAI 官方端点，不经过任何代理，也不收集任何数据。

## Requirements / 环境

- Python 3.8+
- tkinter (bundled with Python / Python 自带)
- No third-party dependencies / 无第三方依赖

## Run / 运行

```bash
python codex_account_switcher.py
```

On Windows you can also double-click `run.bat`.

Windows 下也可以双击 `run.bat`。

## Usage / 使用

1. Sign in to account A in Codex, open the tool, click **Save current account**.
2. Sign out, sign in to account B (this one time may require 2FA), save it too.
3. Use **Switch to selected** to swap between them.
4. Restart Codex and run **Reload Window** in VS Code after switching.

1. 在 Codex 里登录账号 A，打开工具，点「保存当前账号」。
2. 退出登录，登录账号 B（这次可能需要 2FA），再保存一次。
3. 之后用「切换到选中」互换。
4. 切换后重启 Codex，并在 VS Code 中执行 Reload Window。

## Security warning / 安全警告

- `~/.codex/accounts/*.json` contains the account's access/refresh token and is equivalent to account credentials.
- Do **not** commit snapshots to git, upload them to cloud storage, or send them to anyone.
- Only save accounts you legally own.
- This project does not collect or upload any data.

- `~/.codex/accounts/*.json` 包含账号的 access/refresh token，等同于账号凭证。
- **不要**把快照提交到 git、上传云盘或发给别人。
- 只保存你自己合法拥有的账号。
- 本项目不收集、不上传任何数据。

## Disclaimer / 免责声明

This tool is for local account switching only. When using multiple accounts, comply with OpenAI's Terms of Service. Any consequences of account sharing, resale, or abuse are the user's responsibility.

本工具仅用于本地账号切换。使用多个账号时请遵守 OpenAI 的服务条款。因账号共享、转售或滥用导致的后果由使用者自行承担。

## License

MIT
