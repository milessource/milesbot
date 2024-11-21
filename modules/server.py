from __future__ import annotations

import disnake
from disnake.ext import commands, tasks

from typing import List

from server_system import (
    request_information,
    request_lenght,
    is_working,
    reconnect,
    request_lenght_names,)

class Server(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self._update_status.start()

    @tasks.loop(seconds=5)
    async def _update_status(self) -> None:
        reconnect()
        length = request_lenght()
        status = disnake.Status.online if is_working else disnake.Status.do_not_disturb
        online_info = f"{'~' if length is None else length[0]}/{'~' if length is None else length[1]}"
        
        await self.bot.change_presence(
            status=status,
            activity=disnake.Activity(
                type=disnake.ActivityType.watching,
                name=f"online {online_info}",))

    @_update_status.before_loop
    async def _before_update_status(self) -> None:
        await self.bot.wait_until_ready()

    @commands.Cog.listener("on_ready")
    async def _update_ready_status(self) -> None:
        reconnect()
        length = request_lenght()
        status = disnake.Status.online if is_working else disnake.Status.do_not_disturb
        online_info = f"{'~' if length is None else length[0]}/{'~' if length is None else length[1]}"
        
        await self.bot.change_presence(
            status=status,
            activity=disnake.Activity(
                type=disnake.ActivityType.watching,
                name=f"online {online_info}",))

    @commands.slash_command(name="online", description="Displays the server's online status")
    async def _online_status(self, inter: disnake.ApplicationCommandInteraction) -> None:
        if not is_working:
            await inter.response.send_message("Oops, it looks like something went wrong.")
            return
        
        length = request_lenght()
        length_nicknames = request_lenght_names()
        output: List[str] = []

        if length is not None:
            output.append(f"Current online count: {length[0]} out of {length[1]} players.\n")
        if length_nicknames is not None:
            output.append(f"Players currently online: {', '.join(length_nicknames)}.")

        await inter.response.send_message("".join(output))

    @commands.slash_command(name="information", description="Displays server information such as version and protocol")
    async def _server_information(self, inter: disnake.ApplicationCommandInteraction) -> None:
        if not is_working:
            await inter.response.send_message("Oops, it looks like something went wrong.")
            return
        
        info = request_information()
        if info is None:
            await inter.response.send_message("Oops, it looks like something went wrong.")
            return
        
        version, protocol, current_players, max_players = info
        await inter.response.send_message(
            f"Server version: {version}, protocol: {protocol}, players online: {current_players}/{max_players}.")

def setup(bot: commands.Bot) -> None:
    bot.add_cog(Server(bot))
