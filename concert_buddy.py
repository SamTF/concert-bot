### IMPORTS        ############################################################
from typing import Literal
# import punk_scraper
import discord
from discord.ext import commands, tasks
from discord import app_commands


###### CONSTANTS        ##########################################################
TOKEN_FILE = '.concert_buddy.token'


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
    await bot.change_presence(activity=discord.Game('🤘 Rockin\' out 🤘'))


###### COMMANDS        #######################################################
@bot.hybrid_command(name = 'concerts', description = 'Check out all the cool concerts in the area!')
@app_commands.describe(time_period = 'Check for concerts how far out?')
@app_commands.choices(time_period=[
    app_commands.Choice(name='weekly', value='weekly'),
    app_commands.Choice(name='monthly', value='monthly'),
    app_commands.Choice(name='all', value='all'),
])
@app_commands.guilds(discord.Object(id=349267379991347200))
async def concerts(ctx, time_period:app_commands.Choice[str], fruits: Literal['apple', 'banana', 'cherry']):
    await ctx.send(f"test test test **{time_period.value}:** *{fruits}*")


###### RUNNING THE BOT #################################################
if __name__ == "__main__":
    print("_____________CONCERT BUDDY INITIALISED_____________")
    with open(TOKEN_FILE, 'r') as f:
        token = f.read()
    
    bot.run(token)