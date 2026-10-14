# Deployment

The bot runs on the VM as a systemd service.

| Item | Value |
| --- | --- |
| Install folder | `/opt/textparserbot/` |
| Service name | `textparserbot.service` |
| Source | `https://github.com/Furina823/TextParserBot` (`main` branch) |

## Updating the bot

1. On the dev machine, commit and push to `main`:
   ```
   git push
   ```

2. On the VM, pull and restart:
   ```
   cd /opt/textparserbot
   git pull
   sudo systemctl restart textparserbot.service
   ```

3. Check it started:
   ```
   sudo systemctl status textparserbot.service
   journalctl -u textparserbot.service -n 30 --no-pager
   ```
   The log should end with `Synced N command(s)`. Slash commands sync on every start, so a restart is enough for command changes too.

If `git pull` says `Already up to date`, the change has not been pushed yet.

## Useful commands

```
sudo systemctl stop textparserbot.service       # stop the bot
sudo systemctl start textparserbot.service      # start the bot
systemctl cat textparserbot.service             # show the service file
journalctl -u textparserbot.service -f          # follow the live log
```

## Notes

- `.env` (bot token, channel and role IDs) lives only on the VM, in `/opt/textparserbot/`. It is not in git; see `.env-example` for the keys.
- Character data is stored per server in `data/<guild_id>.json` on the VM. `git pull` does not touch it, but back it up before large changes.
