- On server copy all files except sh to ~/.config/systemd/user/
- Give sh files in this folder execution permissions
- Execute:
``` bash
systemctl --user daemon-reload
systemctl --user enable --now nightly-updates.timer
systemctl --user start nightly-updates.target # manually run the update
```