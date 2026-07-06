import discord

from config import NOMBRE_MONEDA
from db.club_queries import (get_connection, check_y_aplicar_mejora_servicio,
                             obtener_tiempo_restante_construccion)
from db.merch_queries import obtener_ventas_tienda, obtener_ventas_catering
from views.modals import ConfirmarMejoraServicioModal


class MenuServicios(discord.ui.Select):
    def __init__(self, club_id, user_id):
        self.club_id = club_id
        self.user_id = user_id
        options = [
            discord.SelectOption(label="Estadísticas de Catering", value="stats_catering", emoji="🍟"),
            discord.SelectOption(label="Estadísticas de Tienda", value="stats_tienda", emoji="👕"),
            discord.SelectOption(label="Gestionar Precios Catering", value="config_catering", emoji="💰"),
            discord.SelectOption(label="Gestionar Precios Tienda", value="config_tienda", emoji="🛠️"),
        ]
        super().__init__(placeholder="Selecciona una acción...", options=options)

    async def callback(self, interaction: discord.Interaction):
        # Nota: Aquí deberías añadir la lógica para config_catering/tienda
        if self.values[0] == "stats_catering":
            datos = obtener_ventas_catering(self.club_id)
            texto = "\n".join([f"🥤 {p}: {pre} {NOMBRE_MONEDA} | Ventas: {v}" for p, pre, v in datos])
            embed = discord.Embed(title="🍟 Estadísticas Catering", description=texto or "Sin datos",
                                  color=discord.Color.gold())
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif self.values[0] == "stats_tienda":
            datos = obtener_ventas_tienda(self.club_id)
            texto = "\n".join([f"👕 {nom}: {pre} {NOMBRE_MONEDA} | Ventas: {v}" for nom, pre, v in datos])
            embed = discord.Embed(title="👕 Estadísticas Tienda", description=texto or "Sin datos",
                                  color=discord.Color.blue())
            await interaction.response.send_message(embed=embed, ephemeral=True)


class ServiciosView(discord.ui.View):
    def __init__(self, club_id, user_id):
        super().__init__(timeout=60)
        self.club_id = club_id
        self.user_id = user_id
        self.add_item(MenuServicios(club_id, user_id))
        self.actualizar_estado_botones()

    def actualizar_estado_botones(self):
        check_y_aplicar_mejora_servicio(self.club_id, 'nivel_catering')
        check_y_aplicar_mejora_servicio(self.club_id, 'nivel_tienda')

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT nivel_catering, nivel_tienda FROM estadio_servicios WHERE club_id = ?', (self.club_id,))
        niveles = cursor.fetchone()
        conn.close()

        cat, tienda = niveles if niveles else (1, 0)

        tiempo_cat = obtener_tiempo_restante_construccion(self.club_id, 'catering')
        tiempo_tienda = obtener_tiempo_restante_construccion(self.club_id, 'tienda')

        # Control catering
        if tiempo_cat and tiempo_cat != "FINALIZADO":
            self.mejorar_catering.disabled = True
            self.mejorar_catering.label = f"Catering ({tiempo_cat})"
        else:
            self.mejorar_catering.disabled = (cat >= 10)
            self.mejorar_catering.label = "Mejorar Catering"

        # Control tienda
        if tiempo_tienda and tiempo_tienda != "FINALIZADO":
            self.mejorar_tienda.disabled = True
            self.mejorar_tienda.label = f"Tienda ({tiempo_tienda})"
        else:
            self.mejorar_tienda.disabled = (tienda >= 10)
            self.mejorar_tienda.label = "Mejorar Tienda"

        self.embed = discord.Embed(title="🌭 Servicios del Estadio", color=discord.Color.gold())
        self.embed.add_field(name="Catering", value=f"Nivel: **{cat}**", inline=True)
        self.embed.add_field(name="Tienda", value=f"Nivel: **{tienda}**", inline=True)
        self.embed.description = "Mejora tus servicios para aumentar los ingresos. Las obras tardan 6h + 1h por nivel."

    async def _refresh_view(self, interaction: discord.Interaction):
        self.actualizar_estado_botones()
        try:
            # Usamos edit_message de la interacción para refrescar sin errores Forbidden
            await interaction.response.edit_message(embed=self.embed, view=self)
        except Exception as e:
            print(f"⚠️ Error al refrescar: {e}")

    @discord.ui.button(label="Mejorar Catering", style=discord.ButtonStyle.primary, emoji="🌭")
    async def mejorar_catering(self, interaction: discord.Interaction, _button: discord.ui.Button):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT nivel_catering FROM estadio_servicios WHERE club_id = ?', (self.club_id,))
        nivel = cursor.fetchone()[0]
        conn.close()

        modal = ConfirmarMejoraServicioModal(self.club_id, 'nivel_catering', nivel)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Mejorar Tienda", style=discord.ButtonStyle.primary, emoji="👕")
    async def mejorar_tienda(self, interaction: discord.Interaction, _button: discord.ui.Button):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT nivel_tienda FROM estadio_servicios WHERE club_id = ?', (self.club_id,))
        nivel = cursor.fetchone()[0]
        conn.close()

        modal = ConfirmarMejoraServicioModal(self.club_id, 'nivel_tienda', nivel)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Volver al Estadio", style=discord.ButtonStyle.secondary, emoji="🏟️", row=2)
    async def volver_estadio(self, interaction: discord.Interaction, _button: discord.ui.Button):
        from views.estadio_view import EstadioView

        # Instanciamos la vista principal del estadio
        view = EstadioView(self.club_id, self.user_id)
        embed = view.actualizar_embed_inicial(self.club_id, self.user_id)

        # Editamos el mensaje actual para volver al menú principal
        await interaction.response.edit_message(embed=embed, view=view)