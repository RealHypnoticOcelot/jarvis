from discord.ext import commands
import asyncio
import discord
import re
import random
import typing

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="j!", intents=intents, status=discord.Status.do_not_disturb, activity=discord.Game(name="j!help"), help_command=None)
api_keys = {
    "owner_id": 000000000000000000, # Replace this with your user ID
    "bot_token": "XXYYzZ" # Replace this with your bot token
}

@bot.event
async def on_ready():
    print(f'Bot connected, logged in as {bot.user}, ID {bot.user.id}')

ignored = (commands.CommandNotFound, commands.BadLiteralArgument, commands.MissingRequiredArgument)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, ignored):
        return
    elif isinstance(error, commands.CheckFailure):
        await ctx.reply("No Permissions!", ephemeral=True, mention_author=False)
    else:
        raise error

@bot.command()
async def resync(ctx: commands.Context):
    if ctx.author.id == api_keys['owner_id']:
        await bot.tree.sync()
        await ctx.reply(content="Resynced slash commands!", mention_author=False)

@bot.command()
async def guildcount(ctx: commands.Context):
    if ctx.author.id == api_keys['owner_id']:
        await ctx.reply(f"I'm in {len(bot.guilds)} guilds!", mention_author=False)

@bot.hybrid_command(name="help", with_app_command=True, description="Get help with the bot!")
async def help(ctx: commands.Context):
    embed = discord.Embed(
        color=discord.Color.from_str("#ae7066"), 
        title=f"How do I use J.A.R.V.I.S.?", 
        description=f"Using Jarvis is easy! Simply enter a message starting with `jarvis`, and Jarvis will respond as if it's a command!\n**For example:**\n```ansi\n\u001b[0;40;36mjarvis, hack into the mainframe\n```\n**Would return:**\n```ansi\n\u001b[0;40;31mhacking into the mainframe\n```\nJarvis also protects against mentioning users, so you don't have to worry about the bot double pinging, or mentioning @everyone.\n\nNeed help? Found a bug? Join [my server](<https://discord.gg/ADMajgMsDX>) and I'll help you out!").set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(mention_author=False, embed=embed)

# Check for the delete command
def indms_or_hasperms(ctx: commands.Context):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        return True
    return ctx.channel.permissions_for(ctx.message.author).manage_messages
    
@bot.hybrid_command(name="delete", description="Delete JARVIS' messages!")
@commands.check(indms_or_hasperms)
async def delete(ctx: commands.Context, count: int):
    await ctx.reply(f"Deleting {count} messages!", mention_author=False, ephemeral=True)
    messages = []
    if ctx.prefix != "/":
        count += 1
    async for i in ctx.channel.history():
        if i.author == bot.user:
            messages.append(i)
        for i in range(count):
            if messages != []:
                await messages[0].delete()
                await asyncio.sleep(1)
                messages.pop(0)

@bot.hybrid_command(name="echo", with_app_command=True, description="Send a message to another channel through the bot!")
@commands.check(indms_or_hasperms)
@commands.guild_only()
async def echo(ctx: commands.Context, channel: discord.TextChannel, *, msg: str, attachment: typing.Optional[discord.Attachment] = None):
    if attachment != None:
        attachment = await attachment.to_file()
        await channel.send(msg, file=attachment)
    else:
        await channel.send(msg)
    await ctx.reply(content=f"Sent message to {channel.mention}!", mention_author=False, ephemeral=True)

def clear_pings(result):
    if result.group(0) == "@everyone":
        return "`@everyone`"
    return "`@here`"

async def mentionstrip(guild, list):
    mentions = []
    caught = 0
    matchedmentions = re.findall(r'<@(\d+)>', list)
    for i in matchedmentions:
        member = await guild.fetch_member(i)
        if member != None:
            displayname = member.display_name
            mentions.append((f"<@{i}>", displayname))
    matchedroles = re.findall(r'<@&(\d+)>', list)
    for i in matchedroles:
        for x in guild.roles:
            if x.id == int(i):
                rolename = x.name
                mentions.append((f"<@&{i}>", rolename))
    for i in mentions: # replace mentions with sanitized versions
        if str(i[0]) in list:
            newname = "`@" + str(i[1]) + "`"
            list = list.replace(str(i[0]), newname)
    list = re.sub(r'@everyone|@here', clear_pings, list) # sanitize @everyone and @here
    return list 

@bot.event
async def on_message(message):
    if message.author != bot.user: # If the message is not from a bot
        if message.content.lower().startswith('jarvis'):
            def ingFrom(s): # Present participle function I copied from https://gist.github.com/arjun921/5f38259ea056fdc35617cb7449fb234e
                for x in s:
                    li.append(x)
                if li[len(li)-1]=='e' and li[len(li)-2]!='i':
                    del li[len(li)-1]
                    li.append("ing")
                elif li[len(li)-1]=='e' and li[len(li)-2]=='i':
                    del li[len(li)-1]
                    del li[len(li)-1]
                    li.append("ying")
                    """To Check"""
                elif li[len(li)-2] in 'aeiou' and li[len(li)-1] not in 'aeiou':
                    temp = li[len(li)-1]
                    del li[len(li)-1]
                    li.append(temp)
                    li.append(temp)
                    li.append("ing")
                elif li[len(li)-1] in 'aeiouy':
                    li.append("ing")
                else:
                    li.append("ing")
                return "".join(li)
            li=[]
            
            final = message.content.lower().split() # converts the string into a ["list", "of", "words"]
            final.pop(0) # removes "jarvis" from the string
            if len(final) != 0: # if jarvis wasn't the only word in the string
                final[0] = ingFrom(final[0]) # converts the first word into the present participle

                final = " ".join(final) # convert ['this', 'list'] into 'this list'

                # now our message is a string ready to be manipulated
                final = await mentionstrip(message.guild, final) # sanitize mentions

                def swap_words(result): # replaces first person with second person and vice versa
                    match result.group(0).lower():
                        case "i" | "me":
                            return "you"
                        case "you":
                            return "me"
                        case "my":
                            return "your"
                        case "your":
                            return "my"
                        case "myself":
                            return "yourself"
                        case "yourself":
                            return "myself"
                        case "am":
                            return "are"
                        case "are":
                            return "am"
                            
                final = re.sub(r'\b(i|me|you|my|your|myself|yourself|am|are)\b', swap_words, final)
                
                def replace_links(result):
                    return f"<{result.group(0)}>"
                
                if message.guild:
                    if not message.channel.permissions_for(message.author).embed_links:
                        final = re.sub(r'https?:\/\/(www\.)?.+\.\S+', replace_links, final)

                if final.endswith("?"):
                    final = random.choice(["yes", "no"])

                try:
                    await message.channel.send(content=final, reference=message, mention_author=False, allowed_mentions=None) # send the final message
                except discord.HTTPException:
                    await message.channel.send("`Cannot send message! Response is >2000 characters!`", reference=message, mention_author=False, allowed_mentions=None)
        await bot.process_commands(message)

bot.run(api_keys['bot_token'])
