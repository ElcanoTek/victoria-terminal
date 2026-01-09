# Victoria Terminal Cleanup Scripts

Automated cleanup scripts for Victoria Terminal runners to manage disk space and remove old containers, images, and files.

## Scripts

### `cleanup-all.sh`

Runs both podman and Victoria folder cleanup in sequence.

```bash
# Run cleanup
./cleanup-all.sh

# Dry run (see what would be cleaned without making changes)
./cleanup-all.sh --dry-run
```

### `cleanup-podman.sh`

Cleans up podman containers, images, and volumes:

- Removes stopped Victoria Terminal containers older than 24 hours
- Removes dangling (untagged) images
- Prunes unused volumes
- Keeps only the latest 2 Victoria Terminal images
- Runs system prune to free up disk space

```bash
# Run podman cleanup
./cleanup-podman.sh

# Dry run
./cleanup-podman.sh --dry-run
```

### `cleanup-victoria.sh`

Cleans up old Victoria folder files using a **whitelist approach**:

**What it does:**
- Removes ALL files older than 7 days (configurable with `--days N`)
- Removes empty directories
- **EXCEPT** files/directories in the protected list below

**Protected paths (never deleted):**
- `protocols/` - Protocol definitions
- `forecasting_data/` - Forecasting data (preserved for analysis)
- `.env` - Environment configuration
- `VICTORIA.md` - Documentation
- `email_last_checked.txt` - Email tracking state
- `.crush/` - Application cache (managed by Victoria Terminal)
- `.cache/` - Application cache (managed by other tools)

**Philosophy:**
Instead of listing what to clean, we list what to protect. Everything else older than N days is fair game. This is simpler, more maintainable, and adapts to new directories automatically.

```bash
# Run Victoria cleanup (uses $HOME/victoria by default)
./cleanup-victoria.sh

# Specify custom Victoria home
./cleanup-victoria.sh --victoria-home /path/to/victoria

# Keep files for 14 days instead of 7
./cleanup-victoria.sh --days 14

# Dry run
./cleanup-victoria.sh --dry-run
```

## Automated Cleanup with Cron

To run cleanup automatically, add a cron job:

```bash
# Edit crontab
crontab -e

# Add one of these lines:

# Run daily at 2 AM
0 2 * * * /home/victoria/victoria-terminal/remote-runner/cleanup-all.sh >> /var/log/victoria-cleanup.log 2>&1

# Run weekly on Sunday at 3 AM
0 3 * * 0 /home/victoria/victoria-terminal/remote-runner/cleanup-all.sh >> /var/log/victoria-cleanup.log 2>&1

# Run twice daily (2 AM and 2 PM)
0 2,14 * * * /home/victoria/victoria-terminal/remote-runner/cleanup-all.sh >> /var/log/victoria-cleanup.log 2>&1
```

## Automated Cleanup with systemd Timer

For systemd-based systems, you can use a timer instead of cron:

### Create the service file

```bash
sudo nano /etc/systemd/system/victoria-cleanup.service
```

```ini
[Unit]
Description=Victoria Terminal Cleanup
After=network.target

[Service]
Type=oneshot
User=victoria
WorkingDirectory=/home/victoria/victoria-terminal/remote-runner
ExecStart=/home/victoria/victoria-terminal/remote-runner/cleanup-all.sh
StandardOutput=journal
StandardError=journal
```

### Create the timer file

```bash
sudo nano /etc/systemd/system/victoria-cleanup.timer
```

```ini
[Unit]
Description=Victoria Terminal Cleanup Timer
Requires=victoria-cleanup.service

[Timer]
# Run daily at 2 AM
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

### Enable and start the timer

```bash
sudo systemctl daemon-reload
sudo systemctl enable victoria-cleanup.timer
sudo systemctl start victoria-cleanup.timer

# Check timer status
sudo systemctl status victoria-cleanup.timer

# List all timers
systemctl list-timers
```

## Monitoring Cleanup

### View cleanup logs (cron)

```bash
tail -f /var/log/victoria-cleanup.log
```

### View cleanup logs (systemd)

```bash
journalctl -u victoria-cleanup.service -f
```

### Check disk usage

```bash
# Podman disk usage
podman system df

# Victoria folder disk usage
du -sh ~/victoria
du -sh ~/victoria/* | sort -hr
```

## Customization

### Adjust retention periods

Edit the scripts to change how long files are kept:

- **Podman containers**: Modify the `24` hours check in `cleanup-podman.sh`
- **Victoria files**: Change `DAYS_TO_KEEP=7` in `cleanup-victoria.sh`
- **Image retention**: Change the `2` in "keep latest 2 versions" in `cleanup-podman.sh`

### Exclude specific files

Add exclusion patterns to the cleanup scripts:

```bash
# Example: Skip files matching a pattern
find "$VICTORIA_HOME/tasks" -name "*.json" ! -name "important-*" -type f -mtime +$DAYS_TO_KEEP
```

## Troubleshooting

### Permission denied errors

Make sure the scripts are executable and run as the correct user:

```bash
chmod +x cleanup-*.sh
# Run as the victoria user, not root
./cleanup-all.sh
```

### Cleanup not running automatically

Check cron/systemd logs:

```bash
# Cron
grep CRON /var/log/syslog

# systemd
systemctl status victoria-cleanup.timer
journalctl -u victoria-cleanup.service
```

### Disk space still high

Run with verbose output to see what's being cleaned:

```bash
./cleanup-all.sh --dry-run
```

Check for large files:

```bash
du -ah ~/victoria | sort -rh | head -20
podman system df -v
```
