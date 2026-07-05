import discord
from config import NOMBRE_MONEDA, COSTE_MEJORA_SERVICIOS
from db.estadio_queries import renombrar_estadio_db
from db.merch_queries import actualizar_precio_tienda_club, actualizar_precio_individual
from db.club_queries import mejorar_servicio_db


class RenombrarEstadioModal(discord.ui.Modal, title="Renombrar Estadio"):
    nuevo_nombre = discord.ui.TextInput(
        label="Nuevo nombre del estadio",
        style=discord.TextStyle.short,
        placeholder="Ej: Nuevo Santiago Bernabéu",
        required=True,
        min_length=3,
        max_length=50,
    )

    def __init__(self, club_id):
        super().__init__()
        self.club_id = club_id

    async def on_submit(self, interaction: discord.Interaction):
        exito = renombrar_estadio_db(self.club_id, self.nuevo_nombre.value)
        if exito:
            from views.estadio_view import EstadioView
            view = EstadioView(self.club_id, interaction.user.id)
            embed = view.actualizar_embed_inicial(self.club_id, interaction.user.id)
            await interaction.response.edit_message(content=None, embed=embed, view=view)
        else:
            await interaction.response.send_message("❌ Error al renombrar el estadio.", ephemeral=True)


class ConfigurarPrecioModal(discord.ui.Modal, title="Ajustar Precio de Camiseta"):
    def __init__(self, club_id, media, jugador_id=None):
        super().__init__()
        self.club_id = club_id
        self.jugador_id = jugador_id

        precio_sugerido = int(40 + (max(0, media - 60) * 2.82))
        self.precio_rec = min(150, max(40, precio_sugerido))

        self.precio = discord.ui.TextInput(
            label=f"Precio sugerido: {self.precio_rec} {NOMBRE_MONEDA}",
            style=discord.TextStyle.short,
            placeholder=str(self.precio_rec),
            default=str(self.precio_rec),
            required=True,
        )
        self.add_item(self.precio)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            nuevo_precio = float(self.precio.value)
            if nuevo_precio < 40 or nuevo_precio > 150:
                await interaction.response.send_message(f"❌ El precio debe estar entre 40 y 150 {NOMBRE_MONEDA}.",
                                                        ephemeral=True)
                return

            if self.jugador_id:
                actualizar_precio_individual(self.jugador_id, nuevo_precio)
                await interaction.response.send_message(
                    f"✅ Precio actualizado a **{int(nuevo_precio)} {NOMBRE_MONEDA}** para el jugador.", ephemeral=True)
            else:
                actualizar_precio_tienda_club(self.club_id, nuevo_precio)
                await interaction.response.send_message(
                    f"✅ Precio actualizado a **{int(nuevo_precio)} {NOMBRE_MONEDA}** para todo el club.",
                    ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Por favor, introduce un número válido.", ephemeral=True)


class ConfirmarMejoraServicioModal(discord.ui.Modal):
    def __init__(self, club_id, tipo_servicio, nivel_actual, view_callback):
        nombre_servicio = "Catering" if "catering" in tipo_servicio else "Tienda"
        super().__init__(title=f"Confirmar mejora de {nombre_servicio}")

        self.club_id = club_id
        self.tipo_servicio = tipo_servicio
        self.view_callback = view_callback

        # Cálculo del coste: Nivel actual * Coste base definido en config
        self.coste_total = (nivel_actual + 1) * COSTE_MEJORA_SERVICIOS

        self.info = discord.ui.TextInput(
            label="Detalles de la inversión",
            style=discord.TextStyle.paragraph,
            default=f"Nivel actual: {nivel_actual}\nNivel a alcanzar: {nivel_actual + 1}\n\nCoste: {self.coste_total} {NOMBRE_MONEDA}"
        )
        self.add_item(self.info)

    async def on_submit(self, interaction: discord.Interaction):
        exito, mensaje = mejorar_servicio_db(self.club_id, self.tipo_servicio)

        if exito:
            await interaction.response.send_message("🏗️ Obras iniciadas correctamente.", ephemeral=True)
            await self.view_callback()
        else:
            await interaction.response.send_message(f"❌ {mensaje}", ephemeral=True)