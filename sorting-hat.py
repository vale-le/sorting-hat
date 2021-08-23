#!/usr/bin/env python3
import os
import random
from contextlib import closing
import json
import urllib
import aiohttp
import requests

import mysql.connector as mc
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


def new_cursor(use_dict=True):
    cnx = mc.connect(
        unix_socket='/var/run/mysqld/mysqld.sock',
        user='discord_bot',
        database='discord_bot',
        autocommit=True
    )
    cur = cnx.cursor(dictionary=use_dict)
    cur._strong_reference_to_cnx = cnx
    return closing(cur)


def create_api_url(channel_id, message_id=None):
    api_url = 'https://discordapp.com/api/channels/{}/messages'.format(channel_id)
    if message_id:
        api_url = os.path.join(api_url, str(message_id))
    return api_url


def post_result_button(channel_id):
    with new_cursor() as cur:
        cur.execute('SELECT battle_id FROM battle_history ORDER BY battle_id DESC LIMIT 1')
        latest_battle_id = cur.fetchone()['battle_id']
    patch_url = create_api_url(channel_id, str(latest_battle_id))
    patch_json = {
        'components': [
            {
                'type': 1,
                'components': [
                    {
                        'type': 2,
                        'label': 'グリフィンドール',
                        'style': 1,
                        'custom_id': 'グリフィンドール',
                        'disabled': True
                    },
                    {
                        'type': 2,
                        'label': 'スリザリン',
                        'style': 3,
                        'custom_id': 'スリザリン',
                        'disabled': True
                    },
                    {
                        'type': 2,
                        'label': '無効試合',
                        'style': 2,
                        'custom_id': '無効試合',
                        'disabled': True
                    },
                    {
                        'type': 2,
                        'label': '修正',
                        'style': 2,
                        'custom_id': '修正',
                        'disabled': True
                    },
                ]
            }
        ]
    }
    requests.patch(patch_url, headers=HEADERS, json=patch_json)

    post_url = create_api_url(channel_id)
    result_json = {
        'content': 'Select a WINNER',
        'components': [
            {
                'type': 1,
                'components': [
                    {
                        'type': 2,
                        'label': 'グリフィンドール',
                        'style': 1,
                        'custom_id': 'グリフィンドール',
                    },
                    {
                        'type': 2,
                        'label': 'スリザリン',
                        'style': 3,
                        'custom_id': 'スリザリン',
                    },
                    {
                        'type': 2,
                        'label': '無効試合',
                        'style': 2,
                        'custom_id': '無効試合',
                    },

                ]
            }
        ]
    }
    return requests.post(post_url, headers=HEADERS, json=result_json)


async def on_socket_response(msg):
    if msg['t'] != "INTERACTION_CREATE":
        return
    if '879118846596890724' not in msg['d']['member']['roles']:
        return

    winner = msg['d']['data']['custom_id']
    channel_id = msg['d']['channel_id']
    message_id = msg['d']['message']['id']

    post_url = create_api_url(channel_id)
    patch_url = create_api_url(channel_id, message_id)

    if winner == '無効試合':
        post_json = {
            'content': 'DRAW (#{})'.format(message_id),
            'components': [
                {
                    'type': 1,
                    'components': [
                        {
                            'type': 2,
                            'label': 'グリフィンドール',
                            'style': 1,
                            'custom_id': 'グリフィンドール',
                            'disabled': True
                        },
                        {
                            'type': 2,
                            'label': 'スリザリン',
                            'style': 3,
                            'custom_id': 'スリザリン',
                            'disabled': True
                        },
                        {
                            'type': 2,
                            'label': '無効試合',
                            'style': 2,
                            'custom_id': '無効試合',
                            'disabled': True
                        },
                        {
                            'type': 2,
                            'label': '修正',
                            'style': 2,
                            'custom_id': '修正',
                            'disabled': False
                        },
                    ]
                }
            ]
        }
    elif winner == '修正':
        post_json = {
            'content': 'Select a WINNER (#{})'.format(message_id),
            'components': [
                {
                    'type': 1,
                    'components': [
                        {
                            'type': 2,
                            'label': 'グリフィンドール',
                            'style': 1,
                            'custom_id': 'グリフィンドール',
                            'disabled': False
                        },
                        {
                            'type': 2,
                            'label': 'スリザリン',
                            'style': 3,
                            'custom_id': 'スリザリン',
                            'disabled': False
                        },
                        {
                            'type': 2,
                            'label': '無効試合',
                            'style': 2,
                            'custom_id': '無効試合',
                            'disabled': False
                        },
                    ]
                }
            ]
        }
    else:
        post_json = {
            'content': '{} WIN! (#{})'.format(winner, message_id),
            'components': [
                {
                    'type': 1,
                    'components': [
                        {
                            'type': 2,
                            'label': 'グリフィンドール',
                            'style': 1,
                            'custom_id': 'グリフィンドール',
                            'disabled': True
                        },
                        {
                            'type': 2,
                            'label': 'スリザリン',
                            'style': 3,
                            'custom_id': 'スリザリン',
                            'disabled': True
                        },
                        {
                            'type': 2,
                            'label': '無効試合',
                            'style': 2,
                            'custom_id': '無効試合',
                            'disabled': True
                        },
                        {
                            'type': 2,
                            'label': '修正',
                            'style': 2,
                            'custom_id': '修正',
                            'disabled': False
                        },
                    ]
                }
            ]
        }

    requests.patch(patch_url, headers=HEADERS, json=post_json)
    await notify_callback(msg['d']['id'], msg['d']['token'])


    with new_cursor() as cur:
        if winner == '無効試合':
            cur.execute('UPDATE battle_history SET win = -1 WHERE battle_id = %s', (message_id,))
        elif winner == '修正':
            cur.execute('UPDATE battle_point SET point = point - 1 WHERE player in (SELECT player FROM battle_history WHERE battle_id = %s AND win = 1)', (message_id,))
            cur.execute('UPDATE battle_point SET point = point + 1 WHERE player in (SELECT player FROM battle_history WHERE battle_id = %s AND win = 0)', (message_id,))
            cur.execute('UPDATE battle_history SET win = 0 WHERE battle_id = %s', (message_id,))
        else:
            cur.execute('UPDATE battle_history SET win = 1 WHERE battle_id = %s AND team = %s', (message_id, winner))
            cur.execute('UPDATE battle_point SET point = point + 1 WHERE point < 20 AND player in (SELECT player FROM battle_history WHERE battle_id = %s AND team = %s)', (message_id, winner))
            cur.execute('UPDATE battle_point SET point = point - 1 WHERE point > 0 AND player in (SELECT player FROM battle_history WHERE battle_id = %s AND team != %s)', (message_id, winner))


async def notify_callback(interaction_id, token, content=None):
    url = "https://discord.com/api/v8/interactions/{}/{}/callback".format(interaction_id, token)
    callback_json = {
        'type': 4,
        'data': {
            'content': content
        }
    }
    async with aiohttp.ClientSession() as s:
        async with s.post(url, json=callback_json) as r:
            if 200 <= r.status < 300:
                return


@BOT.command()
async def lane(ctx):
    random_lane = random.choice(LANES)
    await ctx.channel.send('```{}```'.format(random_lane))


@BOT.command()
async def rank(ctx):
    with new_cursor() as cur:
        cur.execute('SELECT player, point FROM battle_point ORDER BY point DESC')
        score_list = cur.fetchall()
        msg = '=== POINT RANKING ===\n'
        for score in score_list:
            msg += '{}: {}pt\n'.format(score['player'], score['point'])
        await ctx.channel.send('```{}```'.format(msg))


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

    with new_cursor(use_dict=False) as cur:
        cur.execute('SELECT player FROM battle_point')
        registerd_players = [out[0] for out in cur.fetchall()]
        for member in role_member_names:
            if not member in registerd_players:
                cur.execute('INSERT INTO battle_point VALUE (%s, 10)', (member,))

    with new_cursor() as cur:
        in_p = ','.join(list(map(lambda x: '%s', role_member_names)))
        cur.execute('SELECT * FROM battle_point WHERE player IN ({})'.format(in_p), (*role_member_names,))
        battle_point = cur.fetchall()
    battle_point.sort(key=lambda x: x['point'], reverse=True)

    team_a = {'members': {}, 'score': 0}
    team_b = {'members': {}, 'score': 0}

    for i in range(nr_role_members):
        if len(team_b['members']) == 5 or (team_a['score'] <= team_b['score'] and len(team_a['members']) < 5):
            team_a['members'][battle_point[i]['player']] = battle_point[i]['point']
            team_a['score'] += battle_point[i]['point']
        else:
            team_b['members'][battle_point[i]['player']] = battle_point[i]['point']
            team_b['score'] += battle_point[i]['point']

    msg_team_a = '\n'.join('{} ({}pt)'.format(name, point) for name, point in team_a['members'].items())
    msg_team_b = '\n'.join('{} ({}pt)'.format(name, point) for name, point in team_b['members'].items())

    await ctx.channel.send('```=== グリフィンドール ({}pt) ===\n{}\n\n=== スリザリン ({}pt) ===\n{}```'.format(team_a['score'], msg_team_a, team_b['score'], msg_team_b))

    r = post_result_button(channel_id)
    battle_id = json.loads(r.text)['id']
    with new_cursor() as cur:
        for member in team_a['members']:
            cur.execute('INSERT INTO battle_history VALUE (%s, %s, %s, 0)', (battle_id, member, 'グリフィンドール'))
        for member in team_b['members']:
            cur.execute('INSERT INTO battle_history VALUE (%s, %s, %s, 0)', (battle_id, member, 'スリザリン'))


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
    BOT.add_listener(on_socket_response)
    BOT.run(TOKEN)


if __name__ == '__main__':
    main()
