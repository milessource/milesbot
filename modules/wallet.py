from __future__ import annotations

import disnake
from disnake.ext import commands

from config import configuration
from wallet_system import (
    create_database_if_not_exists,
    create_account,
    request_balance,
    create_transaction,
    apply_transaction,
    transfer_money,
    request_transaction_status,)

create_database_if_not_exists()

# TODO: Implement transaction status checking
class Wallet(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.slash_command(name="create_account", description="Create a new account for the shop")
    async def create_account_command(self, inter: disnake.ApplicationCommandInteraction) -> None:
        create_account(inter.author.id)
        await inter.response.send_message("Your account was successfully created.")

    @commands.slash_command(name="wallet", description="View a member's wallet balance")
    async def wallet_check(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member = None) -> None:
        target_member: disnake.Member = member or inter.author
        balance = request_balance(target_member.id)
        if balance is None:
            await inter.response.send_message(f"Member {target_member.mention} does not have an account.")
        else:
            await inter.response.send_message(f"Member {target_member.mention} has `{balance}MILC(s)`.")

    @commands.slash_command(name="buy", description="Purchase a product from the shop")
    async def buy_product(self, inter: disnake.ApplicationCommandInteraction, product_name: str, product_cost: int) -> None:
        if product_cost <= 0:
            await inter.response.send_message("The product cost must be greater than 0.")
            return
        
        transaction_id: str = create_transaction(inter.author.id, product_name, product_cost)
        await inter.response.send_message(
            f"Purchase request created for `{product_name}` costing `{product_cost}`. Transaction ID: `{transaction_id}`")

    @commands.slash_command(name="apply_request", description="Admin | Approve a purchase request")
    async def apply_transaction_command(self, inter: disnake.ApplicationCommandInteraction, transaction_id: str) -> None:
        if inter.author.id in configuration.oids:
            if apply_transaction(transaction_id):
                await inter.response.send_message(f"Transaction with ID `{transaction_id}` has been successfully approved.")
            else:
                await inter.response.send_message(f"Transaction with ID `{transaction_id}` has been declined.")
        else:
            await inter.response.send_message(f"{inter.author.mention}, you do not have permission to perform this action.")

    @commands.slash_command(name="transaction", description="Transfer money between accounts")
    async def transfer_money_command(self, inter: disnake.ApplicationCommandInteraction, to_member: disnake.Member, amount: int) -> None:
        if amount <= 0:
            await inter.response.send_message("The transfer amount must be greater than 0.")
            return

        if transfer_money(inter.author.id, to_member.id, amount):
            await inter.response.send_message(
                f"Successfully transferred `{amount}MILC(s)` from {inter.author.mention} to {to_member.mention}.")
        else:
            await inter.response.send_message("You do not have enough funds for this transaction.")

def setup(bot: commands.Bot) -> None:
    bot.add_cog(Wallet(bot))
