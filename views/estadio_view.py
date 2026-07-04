import discord
from config import CAPACIDAD_POR_NIVEL, COSTE_MEJORA_ESTADIO
from db.club_queries import obtener_info_estadio, obtener_tiempo_restante_construccion, check_y_aplicar_mejora
from db.estadio_queries import obtener_info_club_y_estadio
from views.plantilla_view import PlantillaPaginator
from views.ConfirmacionView import ConfirmacionMejoraView
from db.transaction_queries import obtener_estadisticas_club


class EstadioSelect(discord.ui.Select):
    def __init__(self, club_id):
        self.club_id = club_id
        options = [
            discord.SelectOption(label="Mejorar Estadio", value="upgrade", emoji="🏗️"),
            discord.SelectOption(label="Renombrar Estadio", value="rename", emoji="✍️"),
            discord.SelectOption(label="Ver Plantilla", value="plantilla", emoji="📋"),
            discord.SelectOption(label="Entrenar Jugadores", value="entrenar", emoji="🏋️"),
            discord.SelectOption(label="Ir al Mercado", value="mercado", emoji="🛒"),
        ]

        super().__init__(placeholder="Selecciona una acción...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "upgrade":
            info = obtener_info_estadio(self.club_id)
            nivel_actual, capacidad_actual = info[1], info[2]
            coste = nivel_actual * COSTE_MEJORA_ESTADIO

            tiempo = obtener_tiempo_restante_construccion(self.club_id)
            if tiempo and tiempo != "FINALIZADO":
                await interaction.response.send_message("❌ Ya hay una obra en curso.", ephemeral=True)
                return

            embed = discord.Embed(title="🏗️ Confirmar Mejora de Estadio", color=discord.Color.orange())
            embed.add_field(name="Estado Actual", value=f"Nivel {nivel_actual} | {capacidad_actual} asientos",
                            inline=False)
            embed.add_field(name="Tras la Mejora",
                            value=f"Nivel {nivel_actual + 1} | {capacidad_actual + CAPACIDAD_POR_NIVEL} asientos", inline=False)
            embed.add_field(name="💰 Coste", value=f"{coste} Keycoins", inline=False)

            await interaction.response.edit_message(embed=embed, view=ConfirmacionMejoraView(self.club_id, coste))

        elif self.values[0] == "plantilla":
            view = PlantillaPaginator(self.club_id, interaction.user.id)
            await interaction.response.edit_message(content="Aquí tienes tu plantilla:", embed=view.get_embed(),
                                                    view=view)
        elif self.values[0] == "rename":
            from views.modals import RenombrarEstadioModal
            await interaction.response.send_modal(RenombrarEstadioModal(self.club_id))

        elif self.values[0] == "mercado":
            from views.mercado_view import MercadoView

            view = MercadoView(interaction.user.id)

            if not view.jugadores:
                await interaction.response.send_message("🛒 El mercado está vacío.", ephemeral=True)
            else:
                await interaction.response.edit_message(content="🛒 **Mercado de Fichajes**",
                                                        embed=view.get_embed(),
                                                        view=view)

        elif self.values[0] == "entrenar":
            from views.entrenamiento_view import EntrenamientoView
            embed = discord.Embed(
                title="🏋️ Sala de Entrenamiento",
                description="Selecciona el tipo de entrenamiento y al jugador que quieres mejorar.",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(
                content=None,
                embed=embed,
                view=EntrenamientoView(self.club_id, interaction.user.id)
            )


class EstadioView(discord.ui.View):
    def __init__(self, club_id, user_id):
        super().__init__(timeout=None)
        self.club_id = club_id
        self.user_id = user_id
        self.add_item(EstadioSelect(club_id))


    def actualizar_embed_inicial(self, club_id, user_id):
        # Recargamos info fresca de BD
        info = obtener_info_club_y_estadio(user_id)
        stats = obtener_estadisticas_club(club_id)
        nombre_club, presupuesto, nombre_estadio, nivel, capacidad = info
        tiempo_restante = obtener_tiempo_restante_construccion(club_id)
        check_y_aplicar_mejora(club_id)
        info = obtener_info_club_y_estadio(user_id)


        embed = discord.Embed(title=f"🏟️ Información de {nombre_club}", color=discord.Color.blue())
        embed.add_field(name="💰 Presupuesto", value=f"{presupuesto} Keycoins", inline=False)
        embed.add_field(name="📍 Nombre del Estadio", value=nombre_estadio, inline=True)
        embed.add_field(name="⭐ Nivel", value=str(nivel), inline=True)
        embed.add_field(name="👥 Capacidad", value=f"{capacidad} asientos", inline=True)
        if tiempo_restante:
            if tiempo_restante == "FINALIZADO":
                embed.add_field(name="✅ Estado", value="Construcción finalizada. ¡Disfruta tus mejoras!", inline=False)
            else:
                embed.add_field(name="🏗️ En Construcción", value=f"Tiempo restante: **{tiempo_restante}**",
                                inline=False)

        historial_str = (
            f"✅ Victorias: {stats.get('victorias', 0)}\n"
            f"🤝 Empates: {stats.get('empates', 0)}\n"
            f"❌ Derrotas: {stats.get('derrotas', 0)}\n"
            f"📊 Total: {stats.get('total', 0)}"
        )
        embed.add_field(name="🏆 Historial de Partidos", value=historial_str, inline=False)
        return embed