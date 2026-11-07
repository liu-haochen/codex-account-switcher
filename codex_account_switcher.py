#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Codex 账号切换器（tkinter）

- 显示当前 auth.json 对应的账号
- 列出 accounts/ 下已保存的账号快照
- 保存当前账号、切换账号、刷新、打开目录、删除快照

不会显示或打印任何 token。切换前会自动把当前 auth.json 备份为 _current_backup.json。
"""

import base64
import json
import os
import shutil
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

CODEX_DIR = Path.home() / ".codex"
AUTH_FILE = CODEX_DIR / "auth.json"
ACCOUNTS_DIR = CODEX_DIR / "accounts"
BACKUP_FILE = ACCOUNTS_DIR / "_current_backup.json"


def decode_id_token(tokens: dict) -> str:
    """从 id_token (JWT) 里取出 email，不验证签名。"""
    raw = tokens.get("id_token") if isinstance(tokens, dict) else None
    if not raw:
        return ""
    try:
        payload = raw.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload))
        return data.get("email") or data.get("preferred_username") or ""
    except Exception:
        return ""


def read_auth(path: Path) -> dict:
    """读取 auth.json，失败返回空结构。"""
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def account_info(path: Path) -> dict:
    data = read_auth(path)
    tokens = data.get("tokens") or {}
    mode = data.get("auth_mode") or "unknown"
    account_id = tokens.get("account_id") or ""
    email = decode_id_token(tokens)
    if not email and mode == "apikey":
        email = "API key 模式"
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
    except Exception:
        mtime = ""
    return {
        "mode": mode,
        "account_id": account_id,
        "email": email,
        "mtime": mtime,
    }


class CodexAccountSwitcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Codex 账号切换器")
        self.geometry("780x470")
        self.minsize(680, 400)

        ACCOUNTS_DIR.mkdir(parents=True, exist_ok=True)

        self.current_id = ""
        self.rows = []

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        style = ttk.Style(self)
        try:
            style.theme_use("vista")
        except tk.TclError:
            pass

        top = ttk.LabelFrame(self, text="当前账号", padding=10)
        top.pack(fill="x", padx=12, pady=(12, 6))

        self.current_var = tk.StringVar(value="读取中…")
        self.current_detail_var = tk.StringVar(value="")
        ttk.Label(top, textvariable=self.current_var, font=("", 12, "bold")).pack(anchor="w")
        ttk.Label(top, textvariable=self.current_detail_var, foreground="#666").pack(anchor="w", pady=(2, 0))

        mid = ttk.LabelFrame(self, text="已有账号快照", padding=8)
        mid.pack(fill="both", expand=True, padx=12, pady=6)

        columns = ("name", "email", "account_id", "mtime")
        self.tree = ttk.Treeview(mid, columns=columns, show="headings", selectmode="browse")
        headings = {
            "name": ("名称", 150),
            "email": ("邮箱", 200),
            "account_id": ("账号 ID", 220),
            "mtime": ("保存时间", 130),
        }
        for col, (text, width) in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="w")

        scroll = ttk.Scrollbar(mid, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=12, pady=(6, 4))

        ttk.Button(bottom, text="保存当前账号", command=self.save_current).pack(side="left", padx=(0, 6))
        ttk.Button(bottom, text="切换到选中", command=self.switch_selected).pack(side="left", padx=6)
        ttk.Button(bottom, text="刷新", command=self.refresh).pack(side="left", padx=6)
        ttk.Button(bottom, text="打开账号目录", command=self.open_dir).pack(side="left", padx=6)
        ttk.Button(bottom, text="删除选中", command=self.delete_selected).pack(side="right")

        self.status_var = tk.StringVar(value="")
        ttk.Label(self, textvariable=self.status_var, foreground="#0a7", padding=(12, 2)).pack(fill="x", side="bottom")

        self.tree.bind("<Double-1>", lambda _e: self.switch_selected())

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        self.rows = []

        cur = account_info(AUTH_FILE) if AUTH_FILE.exists() else {}
        self.current_id = cur.get("account_id", "")
        if AUTH_FILE.exists():
            email = cur.get("email") or "（未识别）"
            self.current_var.set(f"{email}")
            detail = f"模式：{cur.get('mode')}    账号 ID：{cur.get('account_id') or '—'}    更新：{cur.get('mtime')}"
            self.current_detail_var.set(detail)
        else:
            self.current_var.set("未登录 / 找不到 auth.json")
            self.current_detail_var.set(str(AUTH_FILE))

        snapshots = sorted(
            [p for p in ACCOUNTS_DIR.glob("*.json") if p.name != "_current_backup.json"],
            key=lambda p: p.name.lower(),
        )
        for path in snapshots:
            info = account_info(path)
            name = path.stem
            mark = "  ← 当前" if info["account_id"] and info["account_id"] == self.current_id else ""
            iid = self.tree.insert(
                "",
                "end",
                values=(name + mark, info["email"], info["account_id"], info["mtime"]),
            )
            self.rows.append((iid, name, info))

        self.status_var.set(f"共 {len(snapshots)} 个快照")

    def _selected_name(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先选中一个账号快照。")
            return None
        for iid, name, _info in self.rows:
            if iid == sel[0]:
                return name
        return None

    def save_current(self):
        if not AUTH_FILE.exists():
            messagebox.showerror("错误", f"找不到 {AUTH_FILE}，请先在 Codex 里登录。")
            return
        info = account_info(AUTH_FILE)
        default = info["email"].split("@")[0] if info["email"] and "@" in info["email"] else datetime.now().strftime("account-%Y%m%d-%H%M")
        default = "".join(c for c in default if c.isalnum() or c in "-_") or "account"
        name = simpledialog.askstring("保存当前账号", "给这个账号起个名字（只支持字母、数字、-、_）：", initialvalue=default, parent=self)
        if not name:
            return
        name = name.strip()
        if not name or any(c in name for c in '\\/:*?"<>|'):
            messagebox.showerror("错误", "名称不合法。")
            return
        target = ACCOUNTS_DIR / f"{name}.json"
        if target.exists() and not messagebox.askyesno("覆盖确认", f"{name}.json 已存在，要覆盖吗？"):
            return
        shutil.copy2(AUTH_FILE, target)
        self.status_var.set(f"已保存：{target.name}")
        self.refresh()

    def switch_selected(self):
        name = self._selected_name()
        if not name:
            return
        target = ACCOUNTS_DIR / f"{name}.json"
        if not target.exists():
            messagebox.showerror("错误", f"找不到 {target.name}")
            return
        if not messagebox.askyesno("切换确认", f"切换到账号「{name}」？\n\n切换后请重启 Codex 客户端，并在 VS Code 中 Reload Window。"):
            return
        try:
            if AUTH_FILE.exists():
                shutil.copy2(AUTH_FILE, BACKUP_FILE)
            shutil.copy2(target, AUTH_FILE)
        except Exception as e:
            messagebox.showerror("切换失败", str(e))
            return
        self.status_var.set(f"已切换到：{name}（请重启 Codex / Reload VS Code）")
        messagebox.showinfo("切换完成", "已切换账号。\n\n请重启 Codex 客户端，并在 VS Code 中执行 Reload Window。")
        self.refresh()

    def delete_selected(self):
        name = self._selected_name()
        if not name:
            return
        target = ACCOUNTS_DIR / f"{name}.json"
        if not messagebox.askyesno("删除确认", f"删除账号快照「{name}」？\n\n只删除快照文件，不影响当前登录。"):
            return
        try:
            target.unlink()
        except Exception as e:
            messagebox.showerror("删除失败", str(e))
            return
        self.status_var.set(f"已删除：{name}")
        self.refresh()

    def open_dir(self):
        ACCOUNTS_DIR.mkdir(parents=True, exist_ok=True)
        os.startfile(str(ACCOUNTS_DIR))


if __name__ == "__main__":
    app = CodexAccountSwitcher()
    app.mainloop()
