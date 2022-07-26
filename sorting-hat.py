#!/usr/bin/env python3
import os
import random
from contextlib import closing
import json
import urllib
import requests

from discord.ext import commands
import discord

INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.guilds = True

BOT = commands.Bot(command_prefix='/', intents=INTENTS)
TOKEN = os.environ['DISCORD_BOT_TOKEN']
HEADERS = {
    'Authorization': 'Bot {}'.format(TOKEN)
}
LANES = ['TOP', 'JUNGLE', 'MID', 'SUPPORT', 'ADC']
BATTLE_ROLE_ID = 879255314522837012
MEMBER_ROLE_ID = 880070383770951760


def create_api_url(channel_id, message_id=None):
    api_url = 'https://discordapp.com/api/channels/{}/messages'.format(channel_id)
    if message_id:
        api_url = os.path.join(api_url, str(message_id))
    return api_url


@BOT.command()
async def lane(ctx):
    random_lane = random.choice(LANES)
    await ctx.channel.send('```{}```'.format(random_lane))


@BOT.command()
async def team(ctx, cmd=None):
    battle_role = ctx.guild.get_role(BATTLE_ROLE_ID)
    if cmd:
        if cmd == 'setup':
            voice_channel = ctx.author.voice
            if not voice_channel:
                await ctx.channel.send('```ERROR: ボイスチャンネルに入っていません```')
                return
            vc_members = voice_channel.channel.members
            for member in ctx.guild.members:
                if battle_role in member.roles:
                    await member.remove_roles(battle_role)
            for member in vc_members:
                await member.add_roles(battle_role)
        elif cmd == 'reset':
            for member in ctx.guild.members:
                if battle_role in member.roles:
                    await member.remove_roles(battle_role)
        elif cmd == 'update':
            voice_channel = ctx.author.voice
            vc_members = voice_channel.channel.members
            if not voice_channel:
                await ctx.channel.send('```ERROR: ボイスチャンネルに入っていません```')
                return
            for member in ctx.guild.members:
                if battle_role in member.roles:
                    if member.status == 'offline' or member not in vc_members:
                        await member.remove_roles(battle_role)
        return

    channel_id = ctx.channel.id
    role_members = battle_role.members
    role_member_names = [member.name for member in role_members]
    nr_role_members = len(role_members)
    if nr_role_members != 10:
        await ctx.channel.send('```ERROR: 5v5 ロールのメンバー数を10人にしてください（現在{}人）```'.format(nr_role_members))
        return

    random.shuffle(role_member_names)
    team_a = role_member_names[0:5:1]
    team_b = role_member_names[5:10:1]


    msg_team_a = '\n'.join(team_a)
    msg_team_b = '\n'.join(team_b)

    await ctx.channel.send('```=== グリフィンドール===\n{}\n\n=== スリザリン ===\n{}```'.format(msg_team_a, msg_team_b))


@BOT.command()
async def aram(ctx):
    version_url = 'https://ddragon.leagueoflegends.com/api/versions.json'
    with urllib.request.urlopen(version_url) as response:
        body = json.loads(response.read())
    version = body[0]

    champion_url_template = 'https://ddragon.leagueoflegends.com/cdn/{}/data/ja_JP/champion.json'
    champion_url = champion_url_template.format(version)
    with urllib.request.urlopen(champion_url) as response:
        body = json.loads(response.read())
        champions = [(c['title'], c['name']) for c in body['data'].values()]

    champ = random.choice(champions)
    random.choice(champions)
    await ctx.channel.send('```"{}" {}```'.format(champ[0], champ[1]))


def main():
    #BOT.add_listener(on_socket_response)
    BOT.run(TOKEN)


if __name__ == '__main__':
    main()
