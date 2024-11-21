from __future__ import annotations

from bot_setup import bot_instance, configuration

if __name__ == "__main__": 
    bot_instance.run(configuration.secure_discord_token)
