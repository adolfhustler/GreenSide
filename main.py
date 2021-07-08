import discord, os, asyncio, datetime, pytz, requests
import string
import os
import youtube_dl
import DiscordUtils
import json

from discord import Member
from discord.ext import tasks, commands
from discord.utils import get
from discord.ext.commands import has_permissions, MissingPermissions
from itertools import cycle
from random import choice
from prsaw import RandomStuff
from io import BytesIO


intents = discord.Intents(messages=True, guilds=True, members=True).all()
intents.members = True
client = commands.Bot(command_prefix=['gs!', 'Gs!', 'gs$', 'mh!'], intents=intents)
client.remove_command("help")
music = DiscordUtils.Music()
api_key = "jXE1mmAbd0KA"
rs = RandomStuff(async_mode = True, api_key = api_key)
cogs = [music]




@client.event
async def on_ready():
	await client.change_presence(activity=discord.Activity(
	    type=discord.ActivityType.listening, name="gs!help"))
	print("sup")


@client.event
async def on_member_join(member):
	role = discord.utils.get(member.guild.roles, name="Visitor")
	await member.add_roles(role)

@client.event
async def on_voice_state_update(member, prev, cur):
    if client.user in prev.channel.members and len([m for m in prev.channel.members if not m.bot]) == 0:
        channel = discord.utils.get(client.voice_clients, channel=prev.channel)
        await channel.disconnect()


@client.event
async def on_message(message):
    if client.user == message.author:
       return

    if message.channel.name == "chat-with-greenside":
       response = await rs.get_ai_response(message.content)
       
       await message.reply(response)

    await client.process_commands(message)


@client.group(invoke_without_command=True)
async def help(ctx):
	em = discord.Embed(title="Help",
	                   description="Usage - mh!help <command>",
	                   colour=discord.Colour.teal())

	em.add_field(name="Moderation", value="mh!help mod")
	em.add_field(name="Music", value="mh!help music")
	em.set_thumbnail(
	    url=
	    "https://media.discordapp.net/attachments/760917137434476575/857864398420181002/transparetn_2021-06-24_at_10.47.26_PM.png?width=372&height=372"
	)

	await ctx.send(embed=em)


@help.command()
async def mod(ctx):
	em = discord.Embed(title="Moderation commands",
	                   description="Usage of moderation commands",
	                   colour=discord.Colour.green(),
	                   inline=True)

	em.add_field(name="Kick", value="mh!kick <member> <reason>")
	em.add_field(name="Ban", value="mh!ban <member> <reason>")
	em.add_field(name="Mute", value="mh!mute <member> <reason>")
	em.add_field(name="Unmute", value="mh!unmute <member>")
	em.add_field(name="Unban", value="mh!unban <member>")
	em.add_field(name="Warn", value="mh!warn <member> <reason>")
	em.add_field(name="Clear", value="mh!clear <amount of messages>")

	await ctx.send(embed=em)


@help.command()
async def music(ctx):
	embed = discord.Embed(title="Music commands",
	                      description="Usage of music commands")

	embed.add_field(name="Play", value="mh!play/mh!p <song name>")
	embed.add_field(name="Stop", value="mh!stop")
	embed.add_field(name="Pause", value="mh!pause")
	embed.add_field(name="Resume", value="mh!resume")

	await ctx.send(embed=embed)


@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		await ctx.send(":x:You can't do that.")
	elif isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(":x:Please type all the required arguments.")
	elif isinstance(error, commands.CommandNotFound):
		await ctx.send(":x:That isn't a command.")
	elif isinstance(error, commands.MemberNotFound):
		await ctx.send("Member not found.")
	else:
		raise error


@client.command()
async def invite(ctx):
	embed = discord.Embed(
	    title="Invite MyHabitat Bot to your server",
	    description='[Invite](https://www.greensiders.ml/mhbot)',
	    colour=discord.Colour.green())
	await ctx.send(embed=embed)


@client.command()
async def links(ctx):
	await ctx.send(
	    "MyHabitat official website: https://www.greensiders.ml/home")


@client.command()
async def ping(ctx):
	await ctx.send(f'Latency is {round(client.latency * 1000)}ms')


@client.command()
@has_permissions(manage_messages=True)
async def clear(ctx, amount=1):
	await ctx.channel.purge(limit=amount)


@client.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
	em = discord.Embed(title=f'{member.name} was kicked',
	                   description="Reason: " + reason,
	                   colour=discord.Colour.red())
	embed = discord.Embed(
	    title=f'You were kicked from {ctx.message.guild.name}',
	    description="Reason: " + reason,
	    colour=discord.Colour.red())
	try:
		await member.kick(reason=reason)
		await ctx.send(embed=em)
	except:
		await ctx.send(":x:You can't ban an administrator.")

	try:
		await member.send(embed=embed)
	except:
		await ctx.send("The member's DMs are off so I couldn't DM them.")


@client.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
	em = discord.Embed(title=f'{member.name} was banned',
	                   description="Reason: " + reason,
	                   colour=discord.Colour.red())
	embed = discord.Embed(
	    title=f'You were banned from {ctx.message.guild.name}',
	    description="Reason: " + reason,
	    colour=discord.Colour.red())
	try:
		await member.send(embed=embed)
	except:
		await ctx.send("The member's DMs are off so I couldn't DM them.")
	try:
		await member.ban(reason=reason)
		await ctx.send(embed=em)
	except:
		await ctx.send(":x:You can't ban an administrator.")


@client.command()
@has_permissions(ban_members=True)
async def unmute(ctx, member: discord.Member, *, reason="No reason provided"):
	em = discord.Embed(title=f'{member.name} was unmuted',
	                   description="Reason: " + reason,
	                   colour=discord.Colour.red())
	muted = discord.utils.get(ctx.guild.roles, name="Muted")
	await member.remove_roles(muted)
	await ctx.send(embed=em)


@client.command()
async def unban(ctx, *, member):
	banned_users = await ctx.guild.bans()
	member_name, member_discriminator = member.split('#')
	embed = discord.Embed(title=f'{member_name} was unbanned',
	                      colour=discord.Colour.green())

	for ban_entry in banned_users:
		user = ban_entry.user

	if (user.name, user.discriminator) == (member_name, member_discriminator):
		await ctx.guild.unban(user)
		await ctx.send(embed=embed)
		return


@client.command()
@has_permissions(ban_members=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
	em = discord.Embed(title=f'{member.name} was warned',
	                   description="Reason: " + reason,
	                   colour=discord.Colour.orange())
	embed = discord.Embed(title="You were warned",
	                      description="Reason: " + reason,
	                      colour=discord.Colour.orange())
	warned = discord.utils.get(ctx.guild.roles, name="Warning")
	guild = ctx.guild
	if not warned:
		warned = await guild.create_roles(name="Warned")

	await member.add_roles(warned)
	await ctx.send(embed=em)
	await member.send(embed=embed)


@client.command()
async def stop(ctx):
	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
	voice.stop()
	await ctx.send("Stopped the current song")


@client.command()
async def pause(ctx):
	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
	if voice.is_playing():
		voice.pause()
		await ctx.send(":pause_button:Paused the current song.")
	else:
		await ctx.send("The bot is not playing anything currently!")


@client.command()
async def resume(ctx):
	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
	if voice.is_paused():
		voice.resume()
		await ctx.send("Resumed the current song.")
	else:
		await ctx.send("The audio is not paused!")


@client.command()
@commands.has_permissions(administrator=True)
async def alert(ctx, member: discord.Member, *, reason="No reason provided"):
	embed = discord.Embed(title=f'{member.name} was alerted',
	                      description="Reason: " + reason,
	                      colour=discord.Colour.teal())
	em = discord.Embed(title=f'You were alerted in {ctx.message.guild.name}',
	                   description="Reason: " + reason,
	                   colour=discord.Colour.teal())
	await ctx.send(embed=embed)
	await member.send(embed=em)


@client.command(aliases=['tempmute'])
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason="No reason provided"):
	guild = ctx.guild
	muted = discord.utils.get(ctx.guild.roles, name="Muted")
	if not muted:
		muted = await ctx.guild.create_roles(name="Muted")

	for channel in guild.channels:
		await channel.set_permissions(muted,
		                              speak=False,
		                              send_messages=False,
		                              read_message_history=True,
		                              read_messages=True)

	embed = discord.Embed(title=f"{member.name} was muted",
	                      description=f"Reason: {reason}",
	                      colour=discord.Colour.red())

	em = discord.Embed(title=f"You were muted in {ctx.message.guild.name}",
	                   description=f"Reason: {reason}",
	                   colour=discord.Colour.red())

	await member.add_roles(muted)
	await ctx.send(embed=embed)
	await member.send(embed=em)


@client.command()
@commands.has_permissions(administrator=True)
async def report(ctx, member: discord.Member, *, reason="no reason bruh"):
	em = discord.Embed(
	    title=f":police_car:A new report has arrived",
	    description=
	    f"{ctx.message.author.mention} reported {member.mention} for " +
	    reason,
	    colour=discord.Colour.orange())
	channel = client.get_channel(855022757245616178)
	await ctx.channel.purge(limit=1)
	await ctx.send(
	    f"{ctx.message.author.mention} Thanks for reporting, a staff member will look into it soon."
	)
	await channel.send(embed=em)


@client.command()
async def acceptreport(ctx, member: discord.Member , *,  reason="no reason bruh"):
	channel = client.get_channel(855027526924369951)
	await ctx.send(f"alright check discord server reports channel now")
	await channel.send(
	    f"{member.mention} Thank you for reporting! A staff has handled the situation"
	)


async def open_account(user):

    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0

    with open('mainbank.json','w') as f:
        json.dump(users,f)

    return True


async def get_bank_data():
    with open('mainbank.json','r') as f:
        users = json.load(f)

    return users


async def update_bank(user,change=0,mode = 'wallet'):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open('mainbank.json','w') as f:
        json.dump(users,f)
    bal = users[str(user.id)]['wallet'],users[str(user.id)]['bank']
    return bal

@client.command(aliases=['bal'])
async def balance(ctx):
    await open_account(ctx.author)
    user = ctx.author

    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]

    em = discord.Embed(title=f'{ctx.author.name} Balance',color = discord.Color.red())
    em.add_field(name="Wallet Balance", value=wallet_amt)
    await ctx.send(embed= em)


@client.command(aliases=['sm'])
async def send(ctx,member : discord.Member,amount = None):
    await open_account(ctx.author)
    await open_account(member)
    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)
    if amount == 'all':
        amount = bal[0]

    amount = int(amount)
    embed = discord.Embed(title=f'{ctx.author} You gave {member} {amount} coins', colour=discord.Colour.green())

    if amount > bal[0]:
        await ctx.send('You do not have sufficient balance')
        return
    if amount < 0:
        await ctx.send('Amount must be positive!')
        return

    await update_bank(ctx.author,-1*amount,'wallet')
    await update_bank(member,amount,'wallet')
    await ctx.send(embed=embed)
    await member.send(f"You received {amount} coins from {ctx.author}!")


async def remove_bank(user,change=0,mode = 'wallet'):
    users = await get_bank_data()

    users[str(user.id)]['wallet'] -= change

    with open('mainbank.json','w') as f:
        json.dump(users,f)
    bal = users[str(user.id)]['wallet']
    return bal

@client.command(aliases=['removecoins'])
@commands.has_any_role("salehin")
async def remove(ctx,member : discord.Member,amount = None):
    await open_account(ctx.author)
    await open_account(member)
    if amount == None:
        await ctx.send("Please enter the amount")
        return
    bal = await remove_bank(member)
    if amount == 'all':
        amount = bal[0]
    amount = int(amount)
    embed = discord.Embed(title=f'{ctx.author} You removed {amount} coins from {member}', colour=discord.Colour.green())
    if amount < 0:
        await ctx.send('Amount must be positive!')
        return

    await update_bank(member,-1*amount,'wallet')
    await ctx.send(embed=embed)
    await member.send(f"{amount} GreenSide coins were removed from your wallet")



@client.command()
async def join(ctx):
	voicetrue = ctx.author.voice
	if voicetrue is None:
		return await ctx.send("Connect to a voice channel first!")
	await ctx.author.voice.channel.connect()
	await ctx.send("Joined your voice channel")

@client.command()
async def leave(ctx):
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send('Left your voice channel')
    else:
        await ctx.send("I'm not in a voice channel, use the join command to make me")






client.run('ODExNDQ3MzI4OTcxNDIzNzQ0.YCyVNw.-njUg6EwEA-Z0sRuMCNZGhqt358')