import discord
from discord.ext import commands
from beem import Hive
from beem.account import Account
from beem.discussions import Query, Discussions_by_created
import os
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

DISCORD_CHANNEL_IDS = list(map(int, os.getenv('DISCORD_CHANNEL_IDS').split(',')))
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Initialize the Hive API
hive = Hive(node="https://techcoderx.com")

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command(name='lastpost')
async def last_post(ctx, community_tag: str):
    # Check if the command was sent in an allowed channel
    if ctx.channel.id not in DISCORD_CHANNEL_IDS:
        return

    try:

        # Create a Query object for the community tag
        query = Query(limit=1, tag=community_tag)

        # Fetch the last post from the community
        last_post = Discussions_by_created(query)

        # Check if any posts were found
        if last_post:
            # The first (and only) post in the list is the most recent one
            post_url = f"https://hive.blog/@{last_post[0]['author']}/{last_post[0]['permlink']}"
            await ctx.send(f"Last post in {community_tag}:\n"
                           f"Title: {last_post[0]['title']}\n"
                           f"Author: {last_post[0]['author']}\n"
                           f"Link: {post_url}")
        else:
            await ctx.send(f"No posts found in {community_tag}")
    except Exception as e:
        await ctx.send(f'Error fetching last post: {e}')

@bot.command(name='balance')
async def balance(ctx, username: str):
    # Check if the command was sent in an allowed channel
    if ctx.channel.id not in DISCORD_CHANNEL_IDS:
        return

    try:
        

        # Fetch the account information
        account = Account(username, blockchain_instance=hive)
        hive_balance = account['balance']
        hbd_balance = account['hbd_balance']
        hp_balance = account['vesting_shares']

        # Fetch the global properties to get total_vesting_fund_hive and total_vesting_shares
        total_vesting_fund_hive = hive.get_dynamic_global_properties()['total_vesting_fund_hive']['amount']
        total_vesting_shares = hive.get_dynamic_global_properties()['total_vesting_shares']['amount']

        # Calculate Hive Power using the formula
        hp_in_hive = hp_balance * (int(total_vesting_fund_hive) / int(total_vesting_shares))

        # Convert Amount to numeric value
        hp_in_hive_numeric = float(hp_in_hive.amount)

        await ctx.send(f'The balance of {username} is:\n'
                       f'HIVE: {hive_balance}\n'
                       f'HBD: {hbd_balance}\n'
                       f'HP: {hp_in_hive_numeric:.6f} HP')
    except Exception as e:
        await ctx.send(f'Error fetching balance: {e}')

bot.run(BOT_TOKEN)
