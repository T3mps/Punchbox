import os
import keep_alive
import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound

client = commands.Bot(command_prefix='$')
usersIn = []


@client.event
async def on_ready():
    print('----------------------------------')
    print(' Initialized Punchbox v 0.1 ALPHA')
    print('----------------------------------')
    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name="KRONOSENGINE.COM"))

    guild = client.get_guild(00000000000000000000)
    working_role = discord.utils.get(guild.roles, name="Working")

    for member in guild.members:
        if working_role in member.roles:
            usersIn.append(member.display_name)


@client.command(aliases=['ping', 'latency'])
async def _ping(ctx):
    await ctx.send(f'{round(client.latency * 1000)}ms')


@client.command(aliases=['clockin', 'cin'], pass_context=True)
@commands.has_role('payroll')
async def _clockin(ctx):
    name = ctx.message.author.nick
    await ctx.message.delete()

    guild_id = ctx.message.guild.id
    guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
    channel = discord.utils.get(guild.text_channels, name="punchbox")

    if (name in usersIn):
        await channel.send(f'{name}, you are already clocked in.')
    else:
        usersIn.append(name)

        role = discord.utils.get(guild.roles, name='Working')
        member = ctx.message.author

        if member is not None:
            await member.add_roles(role)
            await channel.send(f'{name} is now clocked in.')
        else:
            await channel.send(f'{name} could not be clocked in.')


@client.command(aliases=['clockout', 'cout'])
@commands.has_role('payroll')
async def _clockout(ctx):
    name = ctx.message.author.nick
    await ctx.message.delete()

    [guild, channel] = get_context_info(ctx)

    if (name in usersIn):
        usersIn.pop(usersIn.index(name))

        role = discord.utils.get(guild.roles, name='Working')
        member = ctx.message.author

        if member is not None:
            await member.remove_roles(role)
            await channel.send(f'{name} is now clocked out.')
        else:
            await channel.send(f'{name} is stuck.')
    else:
        await channel.send(f'{name}, one must be in before they can be out.')


@client.command(aliases=['who', 'query', 'get'])
async def _who(ctx):
    if (len(usersIn) > 0):
        msg = ''
        for i in usersIn:
            msg += '> ' + i + '\n'

        em = discord.Embed(title=f"On the Clock",
                           description=f"" + msg,
                           color=ctx.author.color)
        await ctx.send(embed=em)
    else:
        await ctx.send('No one is currently on the clock.')


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        em = discord.Embed(title=f"(non)Fatal Error",
                           description=f"Command not found.",
                           color=ctx.author.color)
        await ctx.send(embed=em)
    elif isinstance(error, commands.MissingPermissions):
        em = discord.Embed(
            title=f"Permission Error",
            description=f"You do not have permission to use this command.",
            color=ctx.author.color)
        await ctx.send(embed=em)
    elif isinstance(error, commands.CheckFailure):
        em = discord.Embed(
            title=f"Check Failure",
            description=
            f"You do not meet the requirements to use this command.",
            color=ctx.author.color)
        await ctx.send(embed=em)
    else:
        em = discord.Embed(
            title=f"Unexpected Error",
            description=f"An unexpected error occurred: {str(error)}.",
            color=ctx.author.color)
        await ctx.send(embed=em)


def get_context_info(ctx):
    guild_id = ctx.message.guild.id
    guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
    channel = discord.utils.get(guild.text_channels, name="punchbox")
    return guild, channel


keep_alive.keep_alive()
token = os.environ['Token']
client.run(token)
