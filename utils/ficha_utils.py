import discord
from db import jugador_queries


async def mostrar_ficha_jugador(interaction: discord.Interaction, club_id: int, numero: int):
    jugador = jugador_queries.obtener_jugador_por_numero(club_id, numero)

    if not jugador:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"❌ No se encontró ningún jugador con el dorsal #{numero}.",
                                                    ephemeral=True)
        return

    (_id, nombre, edad, vel, res, anti, sere, trab, pase, ctrl, prof, pot, valor, estrella) = jugador

    suma_total = vel + res + anti + sere + trab + pase + ctrl + prof + pot
    media = round(suma_total / 9)

    embed = discord.Embed(title=f"⚽ Ficha Técnica: {nombre} (#{numero})", color=discord.Color.blue())
    embed.add_field(name="Información", value=f"Edad: {edad}\nValor: {valor:,.0f} €", inline=False)
    embed.add_field(name="Calificación Global", value=f"⭐ {media}/100", inline=False)
    embed.add_field(name="Atributos",
                    value=f"🏃 Vel: {vel} | 🔋 Res: {res}\n👁️ Anti: {anti} | 🧘 Sere: {sere}\n🤝 Trab: {trab} | 🎯 Pase: {pase}\n⚽ Ctrl: {ctrl}",
                    inline=False)
    embed.add_field(name="Mentalidad", value=f"📈 Potencial: {pot} | 🧠 Prof: {prof}", inline=False)

    if estrella:
        embed.set_footer(text="⭐ Jugador Estrella")

    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True)