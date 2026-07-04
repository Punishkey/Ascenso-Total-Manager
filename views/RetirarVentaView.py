import discord

from config import NOMBRE_MONEDA
from db.mercado_queries import obtener_jugadores_en_venta_del_club, retirar_jugador_mercado


class RetirarVentaView(discord.ui.View):
    def __init__(self, club_id):
        super().__init__()
        self.club_id = club_id
        self.add_item(RetirarSelect(club_id))

class RetirarSelect(discord.ui.Select):
    def __init__(self, club_id):
        self.club_id = club_id
        # Obtenemos sus jugadores
        ventas = obtener_jugadores_en_venta_del_club(club_id)
        options = [
            discord.SelectOption(label=f"{nombre} - {precio} {NOMBRE_MONEDA}", value=str(fichaje_id))
            for fichaje_id, nombre, precio in ventas
        ]
        super().__init__(placeholder="Selecciona un jugador para retirar...", options=options)

    async def callback(self, interaction: discord.Interaction):
        fichaje_id = int(self.values[0])
        retirar_jugador_mercado(fichaje_id)
        await interaction.response.edit_message(content="✅ Jugador retirado del mercado con éxito.", view=None)