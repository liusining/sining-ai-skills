---
name: snell-surge-deploy
description: Use when deploying a Snell proxy server on a Linux VPS and configuring a local Surge profile to connect through it. Triggers on Snell setup, Snell deployment, Surge proxy configuration, or VPS proxy installation.
---

# Snell + Surge Deployment

Deploy Snell server on a remote Linux VPS via SSH, then update a local Surge config with the generated proxy entry.

## Mandatory User Inputs

Before starting, ask for and confirm ALL of these:

| Input | Example | Required |
|-------|---------|----------|
| SSH username | `root` | Yes |
| Server address | `203.0.113.50` or `my-vps.example.com` | Yes |
| Surge config file path | `/Users/me/Surge/my.conf` | Yes |
| Proxy display name | `HK-Snell-01` | Yes |

**SSH authentication:** Recommend SSH key login (`ssh -i ~/.ssh/key <username>@<server>`). If the user has a key configured, use it. If not, password auth is acceptable but advise them to set up key-based auth afterward. If the user provides a custom key path, use `-i <path>`.

Connect with: `ssh <username>@<server_address>`

If any required input is missing, **stop and ask**.

**Execution context:** Steps 1–6 run inside the SSH session on the remote server. Step 7 runs on the local machine. When switching from remote to local, exit the SSH session first.

## Constraints

- Use manual flow: download, unzip, configure, systemd service.
- Do NOT expose `psk` in chat output — redact in all responses.
- All remote commands run via SSH from the local machine (or in an SSH session).

## Architecture and URL Detection

**The agent MUST detect the server's OS and architecture automatically.** Do not ask the user — run detection commands on the server.

### Detect Architecture

```bash
uname -m
```

| `uname -m` output | Architecture | Package suffix |
|-------------------|-------------|----------------|
| `x86_64` | amd64 | `linux-amd64` |
| `i386` / `i686` | i386 | `linux-i386` |
| `aarch64` | ARM 64-bit | `linux-aarch64` |
| `armv7l` | ARM 32-bit | `linux-armv7l` |

If `uname -m` returns an unrecognized value (e.g. `mips64`, `ppc64`), **stop and tell the user** — Snell does not provide binaries for that architecture.

### Snell Download URLs (v5.0.1 default)

Construct the URL from the detected architecture:

```
https://dl.nssurge.com/snell/snell-server-v5.0.1-linux-<arch>.zip
```

Full URLs:
- `https://dl.nssurge.com/snell/snell-server-v5.0.1-linux-amd64.zip`
- `https://dl.nssurge.com/snell/snell-server-v5.0.1-linux-i386.zip`
- `https://dl.nssurge.com/snell/snell-server-v5.0.1-linux-aarch64.zip`
- `https://dl.nssurge.com/snell/snell-server-v5.0.1-linux-armv7l.zip`

**Version check:** Optionally check https://kb.nssurge.com/surge-knowledge-base/release-notes/snell for a newer version. If unavailable or unclear, use v5.0.1.

## Deployment Workflow

### Step 1: Preflight — SSH and Environment

```bash
# Connect to server
ssh <username>@<server_address>

# Get root privileges
sudo -i

# Detect OS and architecture
uname -m
cat /etc/os-release
```

#### SSH Password Login Check

Check if password authentication is still enabled:

```bash
grep -i "^PasswordAuthentication" /etc/ssh/sshd_config
```

If the output shows `PasswordAuthentication yes` (or the line is absent, which means it defaults to yes), **recommend disabling it** to the user. Explain that password login is vulnerable to brute-force attacks and SSH key is more secure.

If the user agrees, disable password login:

```bash
# Ensure the user has a working SSH key before proceeding — otherwise they will be locked out
# Test by opening a second terminal and connecting with key auth first

# Edit sshd_config
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#\?ChallengeResponseAuthentication.*/ChallengeResponseAuthentication no/' /etc/ssh/sshd_config

# Restart SSH service to apply
systemctl restart sshd
```

**WARNING:** Before restarting sshd, confirm the user can log in with their SSH key in a separate session. If key auth is not set up, disabling password login will lock them out. If the user declines or has no key configured, skip this step and continue.

Check for required tools and install any that are missing:

```bash
# Check if wget and unzip are available
which wget unzip
```

If either is missing, install them. Detect the package manager and use the appropriate command:

```bash
# Debian/Ubuntu (APT)
apt update && apt install -y wget unzip

# RHEL/CentOS/Fedora (DNF)
dnf install -y wget unzip

# Older CentOS (YUM)
yum install -y wget unzip
```

The agent MUST install missing tools automatically — do not ask the user or skip this step.

Verify `systemd` is available:
```bash
systemctl --version
```

### Step 2: Download and Install Snell Binary

```bash
# Download (use detected architecture)
wget https://dl.nssurge.com/snell/snell-server-v5.0.1-linux-<arch>.zip

# Unzip to /usr/local/bin
unzip snell-server-v5.0.1-linux-<arch>.zip -d /usr/local/bin

# Make executable
chmod +x /usr/local/bin/snell-server
```

### Step 3: Generate Configuration

```bash
# Create config directory
mkdir -p /etc/snell

# Use the built-in wizard to generate config (recommended)
snell-server --wizard -c /etc/snell/snell-server.conf
```

The wizard generates a config like:
```ini
[snell-server]
listen = 0.0.0.0:<port>
psk = <generated-key>
ipv6 = false
```

Parameters:
- `listen`: Bind address and port (0.0.0.0 = all interfaces)
- `psk`: Pre-shared key for authentication (auto-generated by wizard)
- `ipv6`: Set to `true` if IPv6 support is needed

### Step 4: Create Systemd Service

```bash
cat > /lib/systemd/system/snell.service << 'EOF'
[Unit]
Description=Snell Proxy Service
After=network.target

[Service]
Type=simple
User=nobody
Group=nogroup
LimitNOFILE=32768
ExecStart=/usr/local/bin/snell-server -c /etc/snell/snell-server.conf
AmbientCapabilities=CAP_NET_BIND_SERVICE
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=snell-server

[Install]
WantedBy=multi-user.target
EOF
```

**Note:** On CentOS 7 or systems without `nogroup`, change `Group=nogroup` to `Group=nobody`.

### Step 5: Start and Enable Service

```bash
systemctl daemon-reload
systemctl enable snell
systemctl start snell
```

Verify it's running:
```bash
systemctl status snell
```

Confirm the port is listening:
```bash
ss -tlnp | grep snell
```

### Step 6: Firewall Hardening

Recommend locking down the server so that **only the Snell port and SSH port are open**. All other ports should be blocked.

Ask the user if they can provide a confirmed, static IP address for SSH access.

- **If they provide an IP:** restrict SSH to that IP only, open Snell to all.
- **If they cannot provide an IP:** open SSH to all (but still close everything else), and skip the SSH restriction.

#### UFW (Debian/Ubuntu)

```bash
# Reset to clean state (if needed)
ufw --force reset

# Default: deny all incoming, allow all outgoing
ufw default deny incoming
ufw default allow outgoing

# Allow Snell port from all IPs
ufw allow <snell_port>/tcp

# SSH — restricted to user IP (if provided)
ufw allow from <user_ip> to any port 22 proto tcp
# OR if no specific IP:
# ufw allow 22/tcp

# Enable firewall
ufw --force enable
ufw status verbose
```

#### firewalld (CentOS/RHEL/Fedora)

```bash
# Set default zone to drop (block everything)
firewall-cmd --set-default-zone=drop

# Allow Snell port from all IPs
firewall-cmd --permanent --zone=drop --add-port=<snell_port>/tcp

# SSH — restricted to user IP (if provided)
firewall-cmd --permanent --new-zone=ssh-only 2>/dev/null || true
firewall-cmd --permanent --zone=ssh-only --add-source=<user_ip>/32
firewall-cmd --permanent --zone=ssh-only --add-port=22/tcp
# OR if no specific IP:
# firewall-cmd --permanent --zone=drop --add-port=22/tcp

firewall-cmd --reload
firewall-cmd --list-all
```

#### iptables (fallback)

```bash
# Flush existing rules
iptables -F

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT

# Allow Snell port from all IPs
iptables -A INPUT -p tcp --dport <snell_port> -j ACCEPT

# SSH — restricted to user IP (if provided)
iptables -A INPUT -p tcp --dport 22 -s <user_ip> -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j DROP
# OR if no specific IP:
# iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Drop everything else
iptables -A INPUT -j DROP

# Persist rules across reboot
# Debian/Ubuntu
apt install -y iptables-persistent
netfilter-persistent save

# CentOS/RHEL
yum install -y iptables-services
service iptables save
systemctl enable iptables
```

**Note:** UFW and firewalld rules persist automatically. iptables rules are **lost on reboot** unless saved with the commands above.

**WARNING:** Before applying firewall rules, double-check the SSH IP with the user and recommend testing connectivity in a second SSH session before closing the current one. A wrong IP will lock them out.

### Step 7: Read Server Config for Surge

```bash
cat /etc/snell/snell-server.conf
```

Extract `listen` port and `psk` from the output. **Do NOT display psk in chat.**

### Step 8: Update Local Surge Config

Exit the SSH session and return to the local machine:

1. **Backup** the Surge config file first.
2. Read the existing config to find the `[Proxy]` section.
3. Add or update the proxy entry:

```ini
<Proxy Name> = snell, <server_address>, <port>, psk=<psk>, version=5, tfo=true
```

- `version=5` for Snell v5.x (use `4` for v4.x)
- `tfo=true` enables TCP Fast Open
- Keep edits strictly inside the `[Proxy]` block.
- If a proxy with the same name already exists, do NOT overwrite it. Append a numeric suffix instead (e.g., `HK-Snell-01` → `HK-Snell-01-2`).
- If the `[Proxy]` section doesn't exist, create it.

### Step 9: Report Results

Report to the user (with secrets redacted):
- Service status (active/inactive)
- Listening port
- Surge config backup path
- Proxy name added/updated
- **Redact psk in all output**

## Service Management Reference

```bash
systemctl start snell    # Start
systemctl stop snell     # Stop
systemctl restart snell  # Restart
systemctl status snell   # Check status
systemctl enable snell   # Enable on boot
systemctl disable snell  # Disable on boot
```

## Error Handling

- If `snell-server --wizard` fails, check binary permissions and path.
- If `systemctl start snell` fails, check `journalctl -u snell -n 20` for logs.
- If the port is already in use, pick a different port and update the config.
- If local Surge config update fails, **restore the backup immediately** and report rollback.
- On CentOS/RHEL: if service fails with group error, change `Group=nogroup` to `Group=nobody`.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Forgetting `chmod +x` on binary | Binary won't execute; always run `chmod +x /usr/local/bin/snell-server` |
| Wrong architecture package | Always detect with `uname -m` first, never assume |
| `nogroup` doesn't exist on CentOS | Use `Group=nobody` instead |
| Exposing psk in chat | Always redact; only write to config files |
| Using old version number in Surge | Match `version=` to the major version installed (5 for v5.x) |
| Not backing up Surge config | Always backup before editing |
