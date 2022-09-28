# minecraft-manager
Some tools I use to host and manage my own personal minecraft servers.

## How to use
Store in some folder on your server, and set up a symbolic link for your convenience. Something like this:
```
chmod +x /opt/minecraft/manager.py
ln -s /opt/minecraft/manager.py /usr/bin/minecraft
```

Once that's done, you can use the following commands:
- `minecraft --help`: Show available commands
- `minecraft backup`: Do an instant backup of the current running server, if not paused.
- `minecraft list`: List all currently available mods.
- `minecraft logs`: Show logs for current running container. Use `--tail` to specify how many lines to show, and `--follow` if you want a stream.
- `minecraft status`: Shows current modpack, server time, active players and other useful information.
- `minecraft stop`: Stop the current server completely.
- `minecraft load <modpack>`: Backup and close down the old modpack, load a new one! 
