from datetime import datetime

import discord
from discord.ext import commands


class BotSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ###### ================================== ######
    ######              Commands              ######
    ###### ================================== ######

    @commands.command()
    @commands.has_role('cse-support')
    async def status(self, ctx, *, status):
        status = status.strip()
        if status.lower() == 'none':
            await self.bot.change_presence(activity=None)
            await log(f'Custom status disabled')
        elif len(status) <= 128:
            await self.bot.change_presence(activity=discord.Game(status))
            await log(f'Status changed to "{status}"')

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'{round(self.bot.latency * 1000)} ms')


def setup(bot):
    bot.add_cog(BotSettings(bot))


async def log(string, timestamp=True):
    if timestamp:
        print(f'[{str(datetime.now())[:-7]}]', end=' ')
    print(string)