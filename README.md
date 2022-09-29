![image (14)](https://user-images.githubusercontent.com/2098517/192717807-5c3dc59a-eb81-47f6-95e2-2ddbb67a5e4f.png)

My kid has an insatiable appetite for minecraft, and wants to play with his friends and his family online. What's more, he wants to play many different modpacks, switching between them almost every day.

This manager makes it trivial to set up and manage multiple modpacks on the same server. It also comes with some convenient quality of life features.

The simplest way to use this is to have clients set up modpacks with Curseforge, download the corresponding server pack, and set it all up with docker. I've provided two example docker compose files for how this can be done with different popular modpacks.

Feel free to fork this repo and set up your own modpacks, or to just borrow code or ideas from it.

## How to use
Store in some folder on your server, and set up a symbolic link for your convenience. Something like this:
```
chmod +x /opt/minecraft/manager.py
ln -s /opt/minecraft/manager.py /usr/bin/minecraft
```

The `modpacks` folder will all your server modpacks, and each mod subfolder must contain these three things:
- An empty `data` folder, which will be hooked up as a volume in the docker-compose file.
- A `docker-compose.yaml` with the configuration needed to set up the server, as well as automated backups. See examples in this repo.
- A `server.zip` that contains the server modpack. You can usually get this from whichever mod manager or launcher you're using on the client.

Please note that all the `server.zip`s in this repo are just empty placeholder files.

## Commands

### minecraft --help
Shows available commands.

![image](https://user-images.githubusercontent.com/2098517/192712797-9eb5d59b-84f5-4d90-bbad-97d8e227f38d.png)

### minecraft load <modpack>
Backup and close down the old modpack, load a new one!

![minecraft_load](https://user-images.githubusercontent.com/2098517/192714327-680ffb9b-0909-4013-9fd9-90afa6c2fb42.gif)

### minecraft list
List all currently available mods.

![image](https://user-images.githubusercontent.com/2098517/192713046-63a874b3-056a-4d9d-a8c0-01aad4016b14.png)

### minecraft logs
Show logs for current running container.
- Use `--tail` to specify how many lines to show
- Use `--follow` if you want a log stream.

![image](https://user-images.githubusercontent.com/2098517/192713703-e8678f5f-c70f-4b93-bd87-a9a1c63625b2.png)

### minecraft status
Shows current modpack, server time, active players and other useful information.

![image](https://user-images.githubusercontent.com/2098517/192713239-8b932954-b101-4c10-aa3f-9dcdcff2cfc4.png)

### minecraft backup
Do an instant backup of the current running server, if possible.
This relies on the server not currently being paused by the auto-pause functionality in minecraft-docker, and on the backup instance actually running.

### minecraft stop
Shut everything down! :boom:
