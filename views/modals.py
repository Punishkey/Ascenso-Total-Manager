import discord

from config import NOMBRE_MONEDA
from db.estadio_queries import renombrar_estadio_db
from db.merch_queries import actualizar_precio_camiseta


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

            await interaction.response.edit_message(
                content=None,
                embed=embed,
                view=view
            )
        else:
            await interaction.response.send_message("❌ Error al renombrar el estadio.", ephemeral=True)


class ConfigurarPrecioModal(discord.ui.Modal, title="Ajustar Precio de Camiseta"):
    def __init__(self, jugador_id, media):
        super().__init__()
        self.jugador_id = jugador_id

        # Fórmula de precio sugerido: 40 + (Media - 60) * 2.82
        # Limitado entre 40 y 150 Keycoins
        precio_sugerido = int(40 + (max(0, media - 60) * 2.82))
        self.precio_rec = min(150, max(40, precio_sugerido))

        # Definimos el campo de texto
        self.precio = discord.ui.TextInput(
            label=f"Precio recomendado: {self.precio_rec} {NOMBRE_MONEDA}",
            style=discord.TextStyle.short,
            placeholder=str(self.precio_rec),
            default=str(self.precio_rec),
            required=True,
        )
        self.add_item(self.precio)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            nuevo_precio = float(self.precio.value)

            # Validación de rangos permitidos (40 a 150)
            if nuevo_precio < 40 or nuevo_precio > 150:
                await interaction.response.send_message(
                    "❌ El precio debe estar entre **40 y 150 {NOMBRE_MONEDA}**.",
                    ephemeral=True
                )
                return

            # Guardar en base de datos
            actualizar_precio_camiseta(self.jugador_id, nuevo_precio)
            await interaction.response.send_message(
                f"✅ Precio de camiseta actualizado a **{int(nuevo_precio)} {NOMBRE_MONEDA}**.",
                ephemeral=True
            )

        except ValueError:
            await interaction.response.send_message(
                "❌ Por favor, introduce un número válido.",
                ephemeral=True
            )