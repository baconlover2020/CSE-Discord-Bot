from discord.ext import commands
from utils import *


def setup(bot):
    bot.add_cog(Listeners(bot))


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.channel.name == 'i-made-a-pr' and ctx.author != self.bot.user:
            await ctx.add_reaction("💩")
