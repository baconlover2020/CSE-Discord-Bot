#!/usr/bin/env python
import json
import os
from datetime import datetime
from os.path import exists
from pathlib import Path
from random import randint
from sys import argv
from time import sleep, time

import discord
from bing_image_downloader import downloader
from discord.ext import commands

from diceParser import parse

##### ======= #####
##### GLOBALS #####
##### ======= #####
client = discord.Client()
client = commands.Bot(command_prefix='/')
invites = {}
invites_json = None
start_time = time()


##### =========== #####
##### CORE EVENTS #####
##### =========== #####
@client.event
async def on_ready():
    global invites_json
    # Get invite links
    for guild in client.guilds:
        invites[guild.id] = await guild.invites()
    await log('Invites synced')

    # Load JSON
    with open('invites.json', 'r') as f:
        invites_json = json.loads(f.read())
    await log('JSON loaded')

    # Show the bot as online
    await client.change_presence(activity=discord.Game('Refactoring...'), status=None, afk=False)
    await log('Bot is online')

    # Print startup duration
    await log(f'Started in {round(time() - start_time, 1)} seconds')


@client.event
async def on_command_error(ctx, error):
    author, message = ctx.author, ctx.message

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Missing required arguement')
        await ctx.send_help()

    elif isinstance(error, commands.MissingRole):
        await ctx.send('Missing role')

    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(error)

    else:
        await ctx.send(f'Unexpected error: {error}')
        print(error)


##### ================= #####
##### INVITE MANAGEMENT #####
##### ================= #####
@client.event
async def on_member_join(member):
    invites_before_join = invites[member.guild.id]
    invites_after_join = await member.guild.invites()

    # Figure out which invite link was used
    for invite in invites_before_join:
        if invite.uses < find_invite_by_code(invites_after_join, invite.code).uses:
            await log(f'Member {member.name} joined')
            await log(f'Invite Code: {invite.code}')
            invites[member.guild.id] = invites_after_join

            # Assign role (and notify if prospective student)
            for link in invites_json.keys():
                if invite.code in link:
                    role = discord.utils.get(member.guild.roles, id=invites_json[link]['roleID'])
                    await member.add_roles(role)
                    await log(f'{invites_json[link]["purpose"]} {member.name} has joined')

                    # If prospective student, message in Prospective Student General
                    prospective_student_general_channel_id = 702895094881058896
                    prospective_student_general_channel = client.get_channel(prospective_student_general_channel_id)
                    channel = client.get_channel(702895094881058896)
                    await channel.send(f'Hello, {member.mention}')
            break


##### ================ #####
##### STUDENT COMAMNDS #####
##### ================ #####
@client.command()
async def support(ctx):
    await ctx.send(f'This is a feature currently being developed. For now, if you have a question for CSE Support, @ them or email them at cse-support.wright.edu')


@client.command()
async def corgme(ctx, number=-1):
    # Check if corgis dir exists
    if not exists('corgis'):
        downloadcorgis(100)

    # Get images from directory
    images = []
    for path in Path('corgis').rglob('*.*'):
        images.append('corgis/corgi/' + path.name)

    # Pick a random image
    if number != -1 and (0 < number < len(images)):
        image = images[number]
    else:
        image = images[randint(0, len(images) - 1)]

    # Send image
    await ctx.send(file=discord.File(image))


@client.command()
async def poll(ctx, question, *options: str):
    # Need between 2 and 10 options for a poll
    if not (1 < len(options) <= 10):
        return

    # Define reactions
    if len(options) == 2 and options[0] == 'yes' and options[1] == 'no':
        reactions = ['✅', '❌']
    else:
        reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']

    description = []
    for i, option in enumerate(options):
        description += '\n {} {}'.format(reactions[i], option)
    embed = discord.Embed(title=question, description=''.join(description))

    react_message = await ctx.send(embed=embed)
    for reaction in reactions[:len(options)]:
        await react_message.add_reaction(reaction)


@client.command()
async def helloworld(ctx, language='random'):
    outputs = {'python': '```python\nprint("Hello World!")```',
               'c++': '```c++\n#include <iostream>\n\nint main() {\n    std::cout << "Hello world!" << std::endl;\n}```',
               'java': '```java\npublic class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println("Hello world!");\n    }\n}```',
               'c': '```c\n#include <stdio.h>\n\nint main() {\n    printf("Hello world!\\n");\n    return 0;\n}```',
               'bash': '```bash\necho "Hello world!"```',
               'javascript': '```javascript\nconsole.log("Hello world!");```',
               'brainfuck': '```\n++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.```',
               'rust': '```rust\nfn main() {\n    println!("Hello World!");\n}```',
               'matlab': '```matlab\ndisp(\'hello world\')```',
               'html': '```html\n<!DOCTYPE html>\n\n<html>\n  <head>\n    <title>Hello world!</title>\n    <meta charset="utf-8" />\n  </head>\n\n  <body>\n    <p>Wait a minute. This isn\'t a programming language!</p>\n  </body>\n</html>```',
               'csharp': '```csharp\nnamespace CSEBot {\n    class HelloWorld {\n        static void Main(string[] args) {\n            System.Console.WriteLine("Hello World!");\n        }\n    }\n}```',
               'vb': '```vb\nImports System\n\nModule Module1\n    Sub Main()\n        Console.WriteLine("Hello World!")\n        Console.WriteLine("Press Enter Key to Exit.")\n        Console.ReadLine()\n    End Sub\nEnd Module```',
               'r': '```r\nprint("Hello World!", quote = FALSE)```',
               'go': '```go\npackage main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello world!")\n}```',
               'swift': '```swift\nimport Swift\nprint("Hello world!")```',
               'haskell': '```haskell\nmodule Main where\nmain = putStrLn "Hello World"```',
               'befunge': '```befunge\n64+"!dlrow olleH">:#,_@````',
               'perl': '```perl\nprint "Hello world!"```',
               'php': '```php\n<?php\necho \'Hello World\';\n?>```',
               'lisp': '```lisp\n(DEFUN hello ()\n  (PRINT (LIST \'HELLO \'WORLD))\n)\n(hello)```',
               'basic': '```basic\n10 PRINT "Hello World"\n20 END```',
               'cobol': '```cobol\n       identification division.\n       program-id. cobol.\n       procedure division.\n       main.\n           display \'Hello world!\' end-display.\n           stop run.```'}

    # If invalid input, make it random
    language = language.lower()
    if language != 'random' and language not in outputs.keys():
        language = 'random'

    # If random, pick random language
    if language == 'random':
        languages = [i for i in outputs.keys()]
        language = languages[randint(0, len(languages) - 1)]

    await ctx.send(f'{language}\n{outputs[language]}')


@client.command()
async def roll(ctx, *options):
    # Credit goes to Alan Fleming for the module that powers this command
    # https://github.com/AlanCFleming/DiceParser
    if len(options) > 0:
        try:
            dice = ' '.join(options)
            output = parse(dice)
            if len(output[0]) > 100:
                await ctx.send(output[1])
            else:
                await ctx.send(f'{output[0]}\n{output[1]}')
        except Exception:
            await ctx.send('Invalid input')


##### ============== #####
##### ADMIN COMMANDS #####
##### ============== #####
@client.command()
@commands.has_role('cse-support')
async def clear(ctx, amount=''):
    if amount == 'all':
        await ctx.send(f'Clearing all messages from this channel')
        amount = 999999999999999999999999999999999999999999
    elif amount == '':
        await ctx.send(f'No args passed. Use `/clear AMOUNT` to clear AMOUNT messages. Use `/clear all` to clear all messages from this channel')
        return
    else:
        await ctx.send(f'Clearing {amount} messages from this channel')
    sleep(1)
    await ctx.channel.purge(limit=int(float(amount)) + 2)


@client.command()
@commands.has_role('cse-support')
async def downloadcorgis(ctx, amount):
    try:
        amount = int(amount)
        await ctx.send(f'Downloading {amount} images')
    except Exception:
        amount = 100
        await ctx.send(f'Invalid parameter, downloading {amount} images')
    downloader.download('corgi',
                        limit=amount,
                        output_dir='corgis',
                        adult_filter_off=False,
                        force_replace=False)


@client.command()
@commands.has_role('cse-support')
async def status(ctx, *, status):
    status = status.strip()
    if status.lower() == 'none':
        await client.change_presence(activity=None)
        await log(f'Custom status disabled')
    elif len(status) <= 128:
        await client.change_presence(activity=discord.Game(status))
        await log(f'Status changed to "{status}"')


@client.command()
async def ping(ctx):
    await ctx.send(f'{round(client.latency * 1000)} ms')


##### ================= #####
##### UTILITY FUNCTIONS #####
##### ================= #####
async def log(string, timestamp=True):
    if timestamp:
        print(f'[{str(datetime.now())[:-7]}]', end=' ')
    print(string)


def find_invite_by_code(invite_list, code):
    for invite in invite_list:
        if invite.code == code:
            return invite


if __name__ == '__main__':
    # Run bot from key given by command line argument
    client.run(argv[1])
