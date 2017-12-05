import pubgapi
from pubgapi import PLAYER
import discord
from discord.ext import commands
import sqlite3
import re
import configparser

client = discord.Client()

command_prefix = '??'

bot = commands.Bot(command_prefix, description="DelphinadBot rewritten in python3")


@client.event
async def on_ready():
    print('Logged in as ' + client.user.name)
    print("I'm really lazy and don't feel like adding support for multiple servers on the same bot, so the bot only works once per server... or at least with the statistics")
    status = check_database()
    print(status)
    print('test')

@client.event
async def on_message(message):
    if type(message.channel) is discord.Channel:
        if message.content.startswith(command_prefix):
            message_content = message.content.replace(command_prefix, '')
            args = message_content.split(' ')
            if message_content.startswith("pubg"):
                await client.send_typing(message.channel)
                await client.send_message(message.channel, pubg_stats(args))
            elif message_content.startswith('roles'):
                await client.send_message("I'll fix this later")
            elif message_content.startswith("disconnect"):
                client.close();
            elif message_content.startswith("channelid"):
                await client.send_message('Id for channel is: ' + message.channel_id)
            elif message_content.startswith('mentions'):
                await client.send_message(message.channel, get_mentions())

        elif '<@!' in message.content:
            add_to_new_mention(message.content[message.content.index('<@!'): message.content.index('>')+1])

    elif type(message.channel) is discord.PrivateChannel:
        if message.content.startswith(command_prefix):
            message.content = message.content[2:]
            args = message.content.split(' ')
            if message.content.startswith('sql'):
                del args[0]
                query = ''
                for x in args:
                    query = query + x + ' '
                sql = sqlite3.connect('server_stats.db')
                c = sql.cursor()
                c.execute(query)
                result = str(c.fetchall())
                await client.send_message(message.channel, 'Sent query successfully: ' + query + '\nResults: ' + result)


def pubg_stats(args):
    player_region = args[2]
    player_mode = args[3]
    player = PLAYER(api, args[1], args[2], args[3], args[4])
    if player.error == "mode":
        return "Please fix your mode input"
    elif player.error == "region":
        return "Please fix your region input"
    elif player.error == "api":
        return "PUBG API is currently down."

    message1 = "```Stats for " + args[1]
    message1 = message1 + " are as follows in the queue type: " + player_mode + ' in region: ' + player_region
    message1 = message1 + '\nRating: ' + player.rating + '\nKills: ' + player.total_kills
    message1 = message1 + '\nKDR: ' + player.kdr
    message1 = message1 + '\nKills Per Game: ' + player.kills_per_game
    message1 = message1 + '\nWins: ' + player.wins_this_season
    message1 = message1 + '\nRounds Played: ' + player.rounds_played
    message1 = message1 + '\nMost Kills: ' + player.most_kills
    winrate = float(player.wins_this_season) / float(player.rounds_played)
    message1 = message1 + '\nLongest Kill: ' + player.longest_kill + "\nWin Percent: " + str(winrate) + " ```"
    return message1


def add_to_new_mention(mentioned_id):
    sql = sqlite3.connect('server_stats.db')
    c = sql.cursor()
    prohibited = [';']
    if any(x in prohibited for x in mentioned_id):
        return
    c.execute('SELECT amount FROM mentions WHERE user_id=\"' + mentioned_id + '\";')
    amount = c.fetchone()
    if amount is None or amount is 'None':
        c.execute('INSERT I??NTO mentions values (\"' + mentioned_id + '\", 1);')
    else:
        amount = str(amount)
        amount = (int(re.search(r'\d+', amount).group()) + 1)
        c.execute('UPDATE mentions set amount=' + str(amount) + ' WHERE user_id=\"' + mentioned_id + '\";')
    sql.commit()
    sql.close()


def get_mentions():
    sql = sqlite3.connect('server_stats.db')
    c = sql.cursor()
    c.execute('SELECT * FROM mentions LIMIT 15;')
    results = c.fetchall()
    sorted_message = str(sorted(results, reverse=True, key=lambda results: results[1]))
    sorted_message = sorted_message.replace('[', '')
    sorted_message = sorted_message.replace('(', '')
    sorted_message = sorted_message.replace('),', '\n')
    sorted_message = sorted_message.replace(')', '')
    sorted_message = sorted_message.replace(']', '')
    sorted_message = sorted_message.replace("'", '')
    sorted_message = sorted_message.replace('>,', '> ,')
    message = "```Leaderboard:\n " + sorted_message + " ```"
    return message

def check_database():
    sql = sqlite3.connect('server_stats.db')
    c = sql.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS mentions (user_id text,amount int);''')
    c.execute('''CREATE TABLE IF NOT EXISTS words (word text,amount int);''')
    sql.commit()
    sql.close()
    return 'true'


def check_config(dictionary, setting):
    config = configparser.ConfigParser()
    config.read('server_settings.ini')
    return config[dictionary][setting]

api = pubgapi.PUBGAPI(check_config('api_keys','pubg_api'), '2017-pre6')
client.run(check_config('api_keys', 'discord_api_key'))


