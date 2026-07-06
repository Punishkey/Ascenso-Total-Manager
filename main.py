import sys
from pathlib import Path
import discord, os, asyncio, typing
from discord.ext import commands
from dotenv import load_dotenv


sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()
TOKEN = typing.cast(str, os.getenv("DISCORD_TOKEN"))

if not TOKEN:
    raise ValueError("¡ERROR FATAL! El TOKEN no está configurado en el archivo .env!")

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, owner_id=118851319984422913)

try:
    from db import database
except ImportError:
    print("ADVERTENCIA: No se pudo importar la base de datos (db).")
    database = None


async def load_extensions():
    """Carga extensiones desde la carpeta ./cogs/ correctamente."""
    logging.info("Iniciando carga de extensiones (Cogs)...")

    cogs_dir = Path("./cogs")
    if not cogs_dir.is_dir():
        logging.error(f"❌ El directorio '{cogs_dir}' no existe.")
        return False

    valid_count = 0
    for file_path in sorted(cogs_dir.glob("*.py")):
        if file_path.name == "__init__.py":
            continue

        module_name = f"cogs.{file_path.stem}"
        filename = file_path.name[:-3]

        try:
            await bot.load_extension(module_name)
            logging.info(f"✅ Cog cargado correctamente: {module_name}")
            valid_count += 1
        except discord.ExtensionNotFound as e:
            logging.error(f"⚠️ No se encontró el módulo '{module_name}'.")
        except commands.NoEntryPointError:
            logging.warning(f"⚠️ El cog '{filename}' no tiene un punto de entrada válido.")
        except Exception as e:
            logging.error(f"❌ Error al cargar {module_name}: {e}")

    return valid_count > 0


@bot.event
async def on_ready():
    logging.info("=" * 45)
    logging.info(f"✅ Bot conectado como {bot.user} (ID: {bot.user.id})")

    if database:
        try:
            database.init_db()
            logging.info("🗄️ Base de datos inicializada correctamente.")
        except Exception as e:
            logging.error(f"❌ ERROR al inicializar base de datos: {e}")
    else:
        logging.warning("⚠️ Advertencia: No se pudo inicializar la base de datos.")

    try:
        await bot.tree.sync()
        logging.info("🌐 Comandos slash sincronizados exitosamente en Discord.")
    except Exception as e:
        logging.error(f"❌ ERROR al sincronizar comandos slash: {e}")


async def main():
    logging.info("Iniciando el bot...")
    try:
        await load_extensions()  # Cargar cogs antes de iniciar el bot
        await bot.start(TOKEN)
        logging.info("🎉 Bot está funcionando correctamente.")
    except ValueError as e:
        logging.critical(f"Error crítico: {e}")
    except KeyboardInterrupt:
        logging.info("El bot ha sido detenido manualmente (Ctrl+C).")
    except Exception as e:
        logging.error(f"⚠️ Error inesperado al iniciar el bot: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.critical(f"Error fatal al iniciar el bot: {e}")
