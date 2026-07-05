import discord
from db import jugador_queries
from views.modals import ConfigurarPrecioModal


async def mostrar_ficha_jugador(interaction: discord.Interaction, club_id: int, numero: int):
    jugador = jugador_queries.obtener_jugador_con_historico(club_id, numero)

    if not jugador:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"❌ No se encontró ningún jugador con el dorsal #{numero}.",
                                                    ephemeral=True)
        return

    jugador_id = jugador[0]
    # Desempaquetado: (j.id, club_id, nombre, numero, pos, edad, vel, res, anti, sere, trab, pase, ctrl, prof, pot, val, est, vel_b, res_b, anti_b, sere_b, trab_b, pase_b, ctrl_b, prof_b)
    # Índices (0-based):
    # 2:nombre, 5:edad, 6:vel, 7:res, 8:anti, 9:sere, 10:trab, 11:pase, 12:ctrl, 13:prof, 14:pot, 15:valor, 16:estrella
    # 17:vel_b, 18:res_b, 19:anti_b, 20:sere_b, 21:trab_b, 22:pase_b, 23:ctrl_b, 24:prof_b

    nombre, edad = jugador[2], jugador[5]
    vel, res, anti, sere, trab, pase, ctrl, prof = jugador[6:14]
    pot, valor, estrella = jugador[14], jugador[15], jugador[16]

    # Valores base para comparación
    vel_b, res_b, anti_b, sere_b, trab_b, pase_b, ctrl_b, prof_b = jugador[17:25]

    media = round(sum([vel, res, anti, sere, trab, pase, ctrl, prof, pot]) / 9)


    embed = discord.Embed(title=f"⚽ Ficha Técnica: {nombre} (#{numero})", color=discord.Color.blue())
    embed.add_field(name="Información", value=f"Edad: {edad}\nValor: {valor:,.0f} €", inline=False)
    embed.add_field(name="Calificación Global", value=f"⭐ {media}/100", inline=False)



    # Atributos con flechas
    attr_str = (
        f"🏃 Vel: {vel} {obtener_icono_progreso(vel, vel_b)} | 🔋 Res: {res} {obtener_icono_progreso(res, res_b)}\n"
        f"👁️ Anti: {anti} {obtener_icono_progreso(anti, anti_b)} | 🧘 Sere: {sere} {obtener_icono_progreso(sere, sere_b)}\n"
        f"🤝 Trab: {trab} {obtener_icono_progreso(trab, trab_b)} | 🎯 Pase: {pase} {obtener_icono_progreso(pase, pase_b)}\n"
        f"⚽ Ctrl: {ctrl} {obtener_icono_progreso(ctrl, ctrl_b)}"
    )

    embed.add_field(name="Atributos", value=attr_str, inline=False)
    embed.add_field(name="Mentalidad",
                    value=f"📈 Potencial: {pot} | 🧠 Prof: {prof} {obtener_icono_progreso(prof, prof_b)}", inline=False)

    if estrella:
        embed.set_footer(text="⭐ Jugador Estrella")

    view = FichaJugadorView(club_id, jugador_id, media)

    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


def obtener_icono_progreso(actual, base):
    if actual > base:
        return "⬆️"
    elif actual < base:
        return "⬇️"
    return "➖"

class FichaJugadorView(discord.ui.View):
    def __init__(self, club_id, jugador_id, media):
        super().__init__(timeout=60)
        self.club_id = club_id
        self.jugador_id = jugador_id
        self.media = media

    @discord.ui.button(label="💰 Configurar Precio", style=discord.ButtonStyle.primary, emoji="👕")
    async def configurar_precio(self, interaction: discord.Interaction, _button: discord.ui.Button):
        from db.estadio_queries import tiene_tienda_merchandising
        nivel_tienda = tiene_tienda_merchandising(self.club_id)

        if nivel_tienda < 1:
            await interaction.response.send_message(
                "❌ **Acceso denegado:** Necesitas tener la tienda de merchandising a nivel 1 como mínimo para configurar precios individuales.",
                ephemeral=True
            )
            return

            # Si el nivel es correcto, abrimos el modal
        await interaction.response.send_modal(
            ConfigurarPrecioModal(self.club_id, self.media, jugador_id=self.jugador_id)
        )