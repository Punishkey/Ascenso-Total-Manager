import discord
import os
import asyncio
import typing
from discord.ext import commands
from dotenv import load_dotenv
import database

# Configuración de variables
load_dotenv()
TOKEN = typing.cast(str, os.getenv("DISCORD_TOKEN"))

if not TOKEN:
    raise ValueError("¡El TOKEN no está configurado en el archivo .env!")

# Configuración de intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

async def load_extensions():
    # Busca todos los archivos .py en la carpeta 'cogs'
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            # Carga el cog (ejemplo: cogs.players)
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'Cog cargado: {filename}')

@bot.event
async def on_ready():
    database.init_db()
    print(f'Bot conectado como {bot.user}')

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())