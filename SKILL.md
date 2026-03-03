---
name: snell-surge-deploy
description: Deploy a Snell proxy server (Snell 代理协议 / Snell 翻墙协议) on Linux VPS, then update a local Surge [Proxy] entry with the generated key. Use for Snell-to-Surge setup.
---

# Snell + Surge Deployment

Deploy Snell on a server and connect it to a local Surge profile.

## Mandatory user inputs

Before local config editing, ask for and confirm:
- Config file path (e.g. `/Users/.../xxx.conf`)
- System Proxy name (the key shown in `[Proxy]`)

If either is missing, stop and ask the user.

Also confirm:
- SSH target and auth method
- Snell package URL and server architecture

## Constraints

- Do not use one-click deployment scripts.
- Use manual flow: download → unzip → wizard.
- Do not expose `psk` in chat output.

## Workflow

1. Preflight: verify SSH, OS/arch, and required tools (`unzip`, `systemd`).
2. Install: download Snell package, unzip binary to `/usr/local/bin`, `chmod +x`.
3. Configure: run `snell-server --wizard -c /etc/snell/snell-server.conf`.
4. Service: create `snell.service`, run `systemctl daemon-reload`, `enable --now snell`, verify active/listening.
5. Surge update:
   - Backup config file first.
   - Read `listen` and `psk` from server config.
   - Add/update one `[Proxy]` line:

   ```ini
   <System Proxy Name> = snell, <server_ip>, <port>, psk=<psk>, version=<major>, tfo=true
   ```

   - Keep edits inside `[Proxy]` block.
6. Report sanitized results (status/port/backup path), redact secrets.

## Error handling

- If wizard or service start fails, report non-secret error summary.
- If local config update fails, restore backup and report rollback.
