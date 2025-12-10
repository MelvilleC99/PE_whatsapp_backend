# MySQL Restart Script

## Problem
After restarting your Mac, DBngin shows MySQL as "running" (green dot) but TablePlus can't connect.

## Solution
Run this script to properly restart MySQL:

```bash
cd /Users/melville/Documents/PE_whatsapp_backend
./scripts/restart_mysql.sh
```

## What it does
1. Checks if MySQL is actually running
2. Kills any zombie processes
3. Cleans up stale PID files
4. Starts MySQL on port 3307
5. Verifies it started successfully

## Quick Access
You can also run it from anywhere:

```bash
/Users/melville/Documents/PE_whatsapp_backend/scripts/restart_mysql.sh
```

Or add an alias to your `~/.zshrc`:

```bash
alias restart-mysql="/Users/melville/Documents/PE_whatsapp_backend/scripts/restart_mysql.sh"
```

Then just type `restart-mysql` in any terminal!

## TablePlus Connection
After running the script, connect with:
- Host: `127.0.0.1`
- Port: `3307`
- User: `root`
- Password: (empty or check DBngin)
