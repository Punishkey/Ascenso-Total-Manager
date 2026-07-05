import discord
from config import NOMBRE_MONEDA
from db.merch_queries import actualizar_precio_producto_catering

class SelectProducto(discord.ui.Select):
    def __init__(self, club_id):
        self.club_id = club_id
        options = [
            discord.SelectOption(label="Bebida", value="bebida", emoji="🥤"),
            discord.SelectOption(label="Patatas", value="patatas", emoji="🍟"),
            discord.SelectOption(label="Bocadillo", value="bocadillo", emoji="🥪"),
        ]
        super().__init__(placeholder="Selecciona producto a modificar", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ModalPrecioCatering(self.club_id, self.values[0]))

class ModalPrecioCatering(discord.ui.Modal, title="Configurar Precio"):
    def __init__(self, club_id, producto):
        super().__init__()
        self.club_id = club_id
        self.producto = producto
        self.precio = discord.ui.TextInput(label=f"Precio para {producto}", placeholder="Ej: 2", required=True)
        self.add_item(self.precio)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            precio = float(self.precio.value)
            actualizar_precio_producto_catering(self.club_id, self.producto, precio)
            await interaction.response.send_message(f"✅ {self.producto.capitalize()} fijado a {precio} {NOMBRE_MONEDA}.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Introduce un número válido.", ephemeral=True)

class CateringView(discord.ui.View):
    def __init__(self, club_id):
        super().__init__(timeout=60)
        self.add_item(SelectProducto(club_id))