# APOrganizer

APOrganizer is a Discord bot and library which uses SQLite to store and recall YAML and APWorld blobs and metadata for [Archipelago](https://archipelago.gg/) randomizers.

## Installation/Running

You'll need:
* Python 3.13 or above
* A `pip` or a PEP 517-compliant package management tool of your choice like
  `uv`, `pdm`, etc.
* A Discord bot account (see https://discord.com/developers)
* The "guild ID" of the guild you want to add this to
    * To get this information, you'll need to enable Discord developer mode,
      then right click on a server icon and click "Copy Server ID" at the
      bottom.

Clone this repository, then use:

```bash
pip install .
BOT_TOKEN=[your_bot_token_here] aporganizer -g [your_guild_id_here] -d aporganizer.db
```

You can also use the provided Containerfile to build a runnable version and run
it like so, with either Docker or Podman:
```bash
podman build -t aporganizer .
podman run -d --name=aporganizer -v aporganizer:/data -e BOT_TOKEN=[your_bot_token_here] aporganizer -g [your_guild_id_here] -d /data/aporganizer.db
```

