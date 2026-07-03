import discord
from db.mercado_queries import obtener_jugadores_en_mercado, ejecutar_compra


class MercadoView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.jugadores = obtener_jugadores_en_mercado()
        self.current_page = 0

    def get_embed(self):
        if not self.jugadores:
            return discord.Embed(title="🛒 Mercado", description="Vacío.", color=discord.Color.red())

        # fichaje_id, nombre, pos, precio, club, media
        fichaje = self.jugadores[self.current_page]
        fichaje_id, nombre, pos, precio, club, media = fichaje

        embed = discord.Embed(title=f"🛒 Mercado de Fichajes", color=discord.Color.gold())
        embed.add_field(name="Jugador", value=f"**{nombre}** ({pos})", inline=False)
        embed.add_field(name="Media", value=f"⭐ {media:.1f}", inline=True)
        embed.add_field(name="Precio", value=f"💰 {precio:,} monedas", inline=True)
        embed.add_field(name="Club Vendedor", value=f"🏟️ {club}", inline=False)
        return embed

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Comprar", style=discord.ButtonStyle.green)
    async def comprar(self, interaction: discord.Interaction, button: discord.ui.Button):
        from db.club_queries import obtener_club_id_por_usuario

        comprador_club_id = obtener_club_id_por_usuario(interaction.user.id)
        fichaje_id = self.jugadores[self.current_page][0]

        exito, mensaje = ejecutar_compra(fichaje_id, comprador_club_id)

        if exito:
            self.jugadores = obtener_jugadores_en_mercado()
            self.current_page = 0
            await interaction.response.edit_message(content="✅ ¡Jugador fichado!", embed=self.get_embed(), view=self)
        else:
            await interaction.response.send_message(f"❌ {mensaje}", ephemeral=True)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.jugadores) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)