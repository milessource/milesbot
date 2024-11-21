from __future__ import annotations

import disnake
from disnake.ext import commands, tasks

from typing import List

from server_system import request_information, request_lenght, is_working, \
    reconnect, request_lenght_names

class server(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot
        
        self._update_status.start()
        
    @tasks.loop(seconds=5)
    async def _update_status(self) -> None:
        reconnect()
        
        lenght = request_lenght()
        await self._bot.change_presence(
            status=disnake.Status.online if is_working else disnake.Status.do_not_disturb, 
            activity=disnake.Activity(type=disnake.ActivityType.watching,
                name=f'online {"~" if lenght is None else lenght[0]}/{"~" if lenght is None else lenght[1]}'))
        return None

    @_update_status.before_loop
    async def _before_update_status(self) -> None:
        await self._bot.wait_until_ready()
        return None
        
    @commands.Cog.listener("on_ready")
    async def _update_ready_status(self) -> None:
        reconnect()
        
        lenght = request_lenght()
        await self._bot.change_presence(
            status=disnake.Status.online if is_working else disnake.Status.do_not_disturb, 
            activity=disnake.Activity(type=disnake.ActivityType.watching,
                name=f'online {"~" if lenght is None else lenght[0]}/{"~" if lenght is None else lenght[1]}'))
        return None
        
    @commands.slash_command(name='online', description='it shows the servers online status')
    async def _onl_slashcommand(self, iter: disnake.ApplicationCommandInteraction) -> None: 
        if not is_working:
            await iter.response.send_message("oops, it looks like something went wrong")
            return None
        
        length = request_lenght()
        length_nicknames = request_lenght_names()
        slashcommand_output: List[str] = []
        
        if length is not None:
            slashcommand_output.append(f'current online count is {length[0]} out of {length[1]} players.\n')
        if length_nicknames is not None:
            slashcommand_output.append(f'nicknames of the players currently on the server are -> {", ".join(length_nicknames)}.')

        await iter.response.send_message("".join(slashcommand_output))
        return None
    
    @commands.slash_command(name='informaion', description='it also displays server information such as version, protocol')
    async def _inf_slashcommand(self, iter: disnake.ApplicationCommandInteraction) -> None: 
        if not is_working:
            await iter.response.send_message("oops, it looks like something went wrong")
            return None
        
        info_tuple = request_information()
        if info_tuple is None:
            await iter.response.send_message("oops, it looks like something went wrong")
            return None
        
        await iter.response.send_message(f"server version {info_tuple[0]} with protocol {info_tuple[1]}, players online: {info_tuple[2]}/{info_tuple[3]}")
        return None
    
def setup(bot: commands.Bot) -> None:
    bot.add_cog(server(bot))
