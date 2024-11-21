from __future__ import annotations

import disnake
from disnake.ext import commands

from config import configuration
from wallet_system import create_database_if_not_exists, create_account, \
    request_balance, create_transaction, apply_transaction, \
        transfer_money, request_transaction_status

create_database_if_not_exists()
# TODO: check transaction status function
class wallet(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot
    
    @commands.slash_command(name="create_account", description="Create new account for shop")
    async def _create_account(self, inter: disnake.ApplicationCommandInteraction) -> None:
        create_account(inter.author.id)
        await inter.response.send_message("Your account successfuly created")
        return None
    
    @commands.slash_command(name="wallet", description="View member wallet yeah")
    async def _wallet_check(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member = None) -> None:
        r_member: disnake.Member = member or inter.author
        balance = request_balance(r_member.id)
        if balance is None:
            await inter.response.send_message(f"Member {r_member.mention} has no account")
            return None
        else:
            await inter.response.send_message(f"Member {r_member.mention} has {balance} milc's")
            return None
    
    @commands.slash_command(name="buy", description="Boy any product in our shop")
    async def _buy_yeah(self, inter: disnake.ApplicationCommandInteraction, product_name: str, product_cost: int) -> None:
        if product_cost <= 0:
            await inter.response.send_message("Cost of product must be greater than 0")
            return None
        
        uuid: str = create_transaction(inter.author.id, product_name, product_cost)
        await inter.response.send_message(f"Requiest to buy {product_name} created, with cost {product_cost} also UUID is {uuid}")
        return None
    
    @commands.slash_command(name="apply_request", description="ADM | apply buy request")
    async def _apply_transaction(self, inter: disnake.ApplicationCommandInteraction, uuid: str) -> None:
        if inter.author.id in configuration.oids:
            if apply_transaction(uuid):
                await inter.response.send_message(f"Rquest to but with UUID {uuid} is seccusfuul")
                return None
            else:
                await inter.response.send_message(f"Buy request wioth UUID {uuid} has declined")
                return None
        else:
            await inter.response.send_message(f"{inter.author.mention} have no permissions")
            return None
        
    @commands.slash_command(name="transactin", description="Accounts transaction")
    async def _transaction(self, inter: disnake.ApplicationCommandInteraction, to_member: disnake.Member, size: int) -> None:
        if size <= 0:
            await inter.response.send_message("Size must be greater than 0")
            return None
        if transfer_money(inter.author.id, to_member.id, size):
            await inter.response.send_message(f"Transaction amount {size} from member {inter.author.mention} to member {to_member.mention} successful")
            return None
        else:
            await inter.response.send_message("You dont have enough money man :(")
        
def setup(bot: commands.Bot) -> None:
    bot.add_cog(wallet(bot))
