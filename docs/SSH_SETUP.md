# SSH Key Management for Git Operations

The `git-ai.sh` script requires proper SSH key caching to function without password prompts. This document explains setup options.

## Why SSH Key Caching?

The git-ai.sh script performs automated git operations (commit, push, pull) with AI attribution. Without SSH key caching, you'll be prompted for your SSH key passphrase on every operation, breaking the automation flow.

## Option 1: SSH Agent with Keychain (Recommended for macOS/Linux)

### macOS Setup

macOS includes built-in keychain integration:

```bash
# Add to ~/.ssh/config
Host *
  AddKeysToAgent yes
  UseKeychain yes
  IdentityFile ~/.ssh/id_ed25519  # or your key path
```

```bash
# Add key to keychain (one-time)
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

### Linux Setup with keychain

Install keychain utility:

```bash
# Ubuntu/Debian
sudo apt install keychain

# Arch
sudo pacman -S keychain

# Fedora
sudo dnf install keychain
```

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# Keychain setup
eval $(keychain --eval --quiet --agents ssh id_ed25519)

# Helper functions (optional but recommended)
kc-start() {
    eval $(keychain --eval --agents ssh id_ed25519)
    echo "SSH agent started with keychain"
}

kc-status() {
    keychain --list
}
```

Reload your shell:
```bash
source ~/.zshrc  # or ~/.bashrc
```

Start keychain:
```bash
kc-start
# Enter your SSH key passphrase once
```

## Option 2: KDE Wallet / GNOME Keyring (Linux GUI)

If using a desktop environment, you may already have keyring integration:

### GNOME Keyring
Usually enabled by default on GNOME desktops. Ensure `gnome-keyring` package is installed.

### KDE Wallet
Enable SSH agent integration in KDE System Settings → SSH Agent.

## Option 3: Windows Setup

### Using Git Bash
Git Bash includes SSH agent support:

```bash
# Start agent (in Git Bash)
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

### Using Windows OpenSSH Service

Windows 10+ includes OpenSSH:

```powershell
# Start OpenSSH Authentication Agent service
Set-Service ssh-agent -StartupType Automatic
Start-Service ssh-agent

# Add key
ssh-add $HOME\.ssh\id_ed25519
```

## Verifying Setup

Test that SSH key caching is working:

```bash
# This should NOT prompt for passphrase if caching works
ssh -T git@github.com
```

Expected output:
```
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

## Troubleshooting

### "Could not open a connection to your authentication agent"

SSH agent isn't running. Start it:
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

### Still Prompting for Passphrase

1. Check if key is loaded: `ssh-add -l`
2. If not listed, add it: `ssh-add ~/.ssh/id_ed25519`
3. Verify keychain/agent is configured in your shell rc file

### Permission Errors

Ensure SSH key has correct permissions:
```bash
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
chmod 700 ~/.ssh
```

## Alternative: Passwordless SSH Key (Not Recommended)

You can create an SSH key without a passphrase, but this is **not recommended** for security reasons:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com" -N ""
```

This eliminates the need for SSH key caching but leaves your key unprotected if your machine is compromised.

## Testing git-ai.sh

Once SSH caching is set up:

```bash
# Test git operations (should not prompt for passphrase)
./scripts/git-ai.sh status
./scripts/git-ai.sh pull
```

If these work without prompting, your setup is correct!

## Further Reading

- [GitHub SSH Documentation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [SSH Agent Forwarding](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/using-ssh-agent-forwarding)
- [Keychain Project](https://www.funtoo.org/Funtoo:Keychain)
