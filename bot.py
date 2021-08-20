#!/usr/bin/env python3
import os
from time import time

import discord
from discord.ext import commands
from discord_components import DiscordComponents
from dotenv import load_dotenv

from utils import *
import logging


intents = discord.Intents(messages=True, guilds=True, members=True, voice_states=True)
bot = commands.Bot(command_prefix='-', intents=intents)
start_time = time()
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
logging.basicConfig(level=logging.INFO)


@bot.event
async def on_ready():
    """Initializes cogs on bot startup

    Sets up Discord components
    Begins logging
    Loads all cogs
    Sets status
    Finishes startup log
    """

    # Set up Discord Components
    DiscordComponents(bot)

    # Startup status
    await bot.change_presence(activity=discord.Game('Booting'), status=discord.Status.dnd)

    # Start logging
    await log(bot, '\n\n\n\n\n', False)
    await log(bot, '###################################')
    await log(bot, '# BOT STARTING FROM FULL SHUTDOWN #')
    await log(bot, '###################################')

    # Load all cogs
    await bot.change_presence(activity=discord.Game(f'Loading Cogs'), status=discord.Status.idle)
    for file in os.listdir('Cogs'):
        if not file.startswith('__') and file.endswith('.py'):
            try:
                bot.load_extension(f'Cogs.{file[:-3]}')
                await log(bot, f'Loaded cog: {file[:-3]}')
            except commands.errors.NoEntryPointError:
                pass

    # Show the bot as online
    await bot.change_presence(activity=discord.Game('Raider Up!'), status=discord.Status.online, afk=False)
    await log(bot, 'Bot is online')

    # Print startup duration
    await log(bot, '#########################')
    await log(bot, '# BOT STARTUP COMPLETED #')
    await log(bot, '#########################\n')
    await log(bot, f'Started in {round(time() - start_time, 1)} seconds')


@bot.event
async def on_command_error(ctx, error):
    """Generic error handler

    If a command errors with a MissingRequiredArgument, MissingRole, or CommandNotFound error, triggers custom error message.
    If other error type, sends message with error statement
    """
    author, message = ctx.author, ctx.message.content

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Missing required arguement')
        await ctx.send_help()
        await log(bot, f'{author} attempted to run `{message}` but failed because they were missing a required argument')

    elif isinstance(error, commands.MissingRole):
        await ctx.send('Missing role')
        await log(bot, f'{author} attempted to run `{message}` but failed because they were missing a required role')

    elif isinstance(error, commands.CommandNotFound):
        await log(bot, f'{author} attempted to run `{message}` but failed because the command was not found')

    else:
        await ctx.send(f'Unexpected error: {error}')
        await log(bot, f'{author} attempted to run `{message}` but failed because of an unexpected error: {error}')


if __name__ == '__main__':
    # Run bot from key given by command line argument
    bot.run(TOKEN)
