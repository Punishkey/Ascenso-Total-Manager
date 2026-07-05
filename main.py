from pathlib import Path

import discord
import os
import asyncio

import typing
from discord.ext import commands
from dotenv import load_dotenv

try:
    from db import database
except ImportError:
    print("ADVERTENCIA: No se pudo importar la base de datos (db). Asegúrate de que el archivo exista.")
    database = None

# --- Configuración y Setup Inicial ---

load_dotenv()
TOKEN = typing.cast(str, os.getenv("DISCORD_TOKEN"))

if not TOKEN:
    raise ValueError("¡ERROR FATAL! El TOKEN no está configurado en el archivo .env!")

# Configuración de logging
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuración de intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Inicialización del Bot
bot = commands.Bot(command_prefix='!', intents=intents, owner_id=118851319984422913)


async def load_extensions():
    """
    Carga todos los módulos (cogs) de la carpeta 'cogs' de manera robusta.
    Incluye manejo de errores para que un cog fallido no detenga el bot.
    """
    logging.info("Iniciando carga de extensiones (Cogs)...")

    cogs_dir = Path("./cogs")
    if not cogs_dir.is_dir():
        logging.error(f"El directorio '{cogs_dir}' no se encontró.")
        return

    for file_path in cogs_dir.glob('*.py'):  # Usamos glob para encontrar todos los *.py
        if file_path.name != "__init__.py":
            continue
        filename = file_path.name[:-3]
        module_name = f'cogs.{filename}'

        try:
            await bot.load_extension(module_name)
            logging.info(f'✅ Cog cargado exitosamente: {file_path.name}')
        except commands.ExtensionNotFound:
            logging.warning(
                f"⚠️ Falló al encontrar el módulo '{module_name}'. Asegúrate de que la estructura sea correcta.")
        except Exception as e:
            # Este bloque captura errores internos del cog (sintaxis, etc.)
            logging.error(f"❌ ERROR FATAL al cargar el Cog {file_path.name}: {e}")


@bot.event
async def on_ready():
    """
    Evento disparado cuando el bot se conecta exitosamente a Discord.
    Se inicializan la base de datos y los comandos slash.
    """
    logging.info('====================================')
    logging.info(f'✅ Bot conectado como {bot.user} (ID: {bot.user.id})')

    # Inicialización de DB con manejo de errores
    if database:
        try:
            database.init_db()
            logging.info('🗄️ Base de datos inicializada correctamente.')
        except Exception as e:
            logging.error(f'❌ ERROR al inicializar la base de datos: {e}')
    else:
        logging.warning("⚠️ Advertencia: No se pudo inicializar el módulo de base de datos.")

    try:
        # Sincronización de comandos (Slash Commands)
        await bot.tree.sync()
        logging.info('🌐 Comandos slash sincronizados exitosamente en Discord.')
    except Exception as e:
        logging.error(f'❌ ERROR al sincronizar comandos slash: {e}')


async def main():
    """Función principal asíncrona que ejecuta el bot."""
    await load_extensions()  # Cargar módulos primero
    await bot.start(TOKEN)


if __name__ == "__main__":
    try:
        # Ejecución de la lógica principal y manejo de errores general
        asyncio.run(main())
    except ValueError as e:
        logging.critical(str(e))  # Captura el error del TOKEN
    except KeyboardInterrupt:
        logging.info("El bot ha sido detenido manualmente por el usuario (Ctrl+C).")