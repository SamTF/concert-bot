### IMPORTS        ############################################################
### My modules
import punk_scraper
import thumb_scraper

### Stdlib
from datetime import datetime
from typing import Literal
import re

### Discord
import discord
from discord.ext import commands, tasks
from discord import app_commands


###### CONSTANTS        ##########################################################
TOKEN_FILE = '.concert_buddy.token'
CONCERTS = None


###### DISCORD STUFF ############################################################
### Creating the bot!
class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='🤘', intents=intents)

    # on_ready event l think
    async def setup_hook(self) -> None:
        await self.tree.sync(guild=discord.Object(id=349267379991347200))
        print(f'Synced slash commands for {self.user} @ server 349267379991347200')
    
    # error handling
    async def on_command_error(self, ctx, error) -> None:
        await ctx.reply(error, ephemeral=True)

bot = Bot()


###### EVENTS        ##########################################################
# Runs this when the bot becomes online
@bot.event
async def on_ready():
    print("Ready to rock out!")
    print(bot.user.name)

    global CONCERTS
    CONCERTS = punk_scraper.fetch_concerts()

    await bot.change_presence(activity=discord.Game('🤘 Rockin\' out 🤘'))


###### COMMANDS        #######################################################
### /concerts
@bot.hybrid_command(name = 'concerts', description = 'Check out all the cool concerts in the area!')
@app_commands.describe(time_period = 'Check for concerts how far out?')
@app_commands.choices(time_period=[
    app_commands.Choice(name='weekly', value='weekly'),
    app_commands.Choice(name='monthly', value='monthly'),
    app_commands.Choice(name='all', value='all'),
])
@app_commands.guilds(discord.Object(id=349267379991347200))
async def concerts(ctx, time_period:app_commands.Choice[str], fruits: Literal['apple', 'banana', 'cherry']):
    '''
    Displays shorthand information for all concerts taking place in the requested period of time.
    '''
    today = datetime.today()

    print(f'>>> Requesting {time_period.value} concerts by {ctx.author.name}')

    concerts = []

    match time_period.value:
        case 'weekly':
            concerts = [c for c in CONCERTS.values() if (c.date - today).days <= 7]
        case 'monthly':
            concerts = [c for c in CONCERTS.values() if c.date.month == today.month]
        case _:
            concerts = CONCERTS.values()
    
    msg = ''
    for c in concerts:
        msg += c.shorthand + '\n'

    print(msg)

    await ctx.send(f"{msg}")


### /concert
@bot.hybrid_command(name = 'concert', description = 'Display detailed info on one specific concert')
@app_commands.guilds(discord.Object(id=349267379991347200))
async def concert(ctx, concert_id: int):
    '''
    Display detailed info on one specific concert
    '''

    # checking if ID exists
    if not concert_id in CONCERTS:
        await ctx.send(f'No concert with ID **{concert_id}** was found. Try again :)')
        return
    
    concert = CONCERTS[concert_id]
    date_str = datetime.strftime(concert.date, '%d/%m/%y')
    band = re.sub("\(.*$", "", concert.band[0]).title().strip()

    # sending concert info as an embed
    embed = discord.Embed(
        title=band,
        description=concert,
        colour=0xff0062,
        url="http://www.punkstelle.de/"
    )

    await ctx.send(embed = embed)



###### RUNNING THE BOT #################################################
if __name__ == "__main__":
    print("_____________CONCERT BUDDY INITIALISED_____________")
    with open(TOKEN_FILE, 'r') as f:
        token = f.read()
    
    bot.run(token)