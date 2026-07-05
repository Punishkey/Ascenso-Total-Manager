import discord

def crear_embed_base(title: str, color=discord.Color.blue()):
    embed = discord.Embed(title=title, color=color)
    embed.set_footer(text="Ascenso Total Manager | Gestión de Club")
    return embed