import discord
from db.mercado_queries import obtener_jugadores_en_mercado, ejecutar_compra, obtener_jugadores_en_venta_del_club
from views.RetirarVentaView import RetirarVentaView


class MercadoView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.jugadores = obtener_jugadores_en_mercado()
        self.current_page = 0

    def get_embed(self):
        if not self.jugadores:
            return discord.Embed(title="🛒 Mercado", description="Vacío.", color=discord.Color.red())

        try:
            mapeo_posiciones = {
                "1": "POR", "2": "DFC", "3": "MCD", "4": "MC", "5": "EXT", "6": "DC"
            }

            fichaje = self.jugadores[self.current_page]
            fichaje_id, nombre, pos, precio, club, media = fichaje

            nombre_posicion = mapeo_posiciones.get(str(pos), str(pos))

            nombre_display = nombre if nombre else "Jugador Desconocido"
            media_display = f"{media:.1f}" if media is not None else "0.0"

            embed = discord.Embed(title=f"🛒 Mercado de Fichajes", color=discord.Color.gold())
            embed.add_field(name="Jugador", value=f"**{nombre_display}** ({nombre_posicion})", inline=False)
            embed.add_field(name="Media", value=f"⭐ {media_display}", inline=True)
            embed.add_field(name="Precio", value=f"💰 {precio:,} monedas", inline=True)
            embed.add_field(name="Club Vendedor", value=f"🏟️ {club}", inline=False)
            embed.set_footer(text=f"Página {self.current_page + 1} de {len(self.jugadores)}")
            return embed

        except Exception as e:
            return discord.Embed(title="Error", description=f"Error en datos: {e}", color=discord.Color.red())

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary, row=0)
    async def prev(self, interaction: discord.Interaction, _button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Comprar", style=discord.ButtonStyle.green, row=1)
    async def comprar(self, interaction: discord.Interaction, _button: discord.ui.Button):
        from db.club_queries import obtener_club_id_por_usuario
        comprador_club_id = obtener_club_id_por_usuario(interaction.user.id)

        if not comprador_club_id:
            await interaction.response.send_message("❌ No tienes un club registrado.", ephemeral=True)
            return

        fichaje_id = self.jugadores[self.current_page][0]
        exito, mensaje = ejecutar_compra(fichaje_id, comprador_club_id)

        if exito:
            self.jugadores = obtener_jugadores_en_mercado()
            self.current_page = 0
            if not self.jugadores:
                await interaction.response.edit_message(content="🛒 El mercado se ha quedado vacío.", embed=None,
                                                        view=None)
            else:
                await interaction.response.edit_message(content="✅ ¡Jugador fichado!", embed=self.get_embed(),
                                                        view=self)
        else:
            await interaction.response.send_message(f"❌ {mensaje}", ephemeral=True)

    @discord.ui.button(label="Vender", style=discord.ButtonStyle.blurple, row=1)
    async def vender(self, interaction: discord.Interaction, _button: discord.ui.Button):
        await interaction.response.send_modal(VenderJugadorModal())

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary, row=0)
    async def next(self, interaction: discord.Interaction, _button: discord.ui.Button):
        if self.current_page < len(self.jugadores) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Mis Ventas", style=discord.ButtonStyle.secondary, row=1)
    async def mis_ventas(self, interaction: discord.Interaction, _button: discord.ui.Button):
        from db.club_queries import obtener_club_id_por_usuario
        club_id = obtener_club_id_por_usuario(interaction.user.id)
        ventas = obtener_jugadores_en_venta_del_club(club_id)
        if not ventas:
            await interaction.response.send_message("❌ No tienes ningún jugador en venta.", ephemeral=True)
            return
        await interaction.response.send_message("Selecciona qué jugador quieres retirar:",
                                                view=RetirarVentaView(club_id), ephemeral=True)

    @discord.ui.button(label="Volver al Estadio", style=discord.ButtonStyle.secondary, row=2)
    async def volver_estadio(self, interaction: discord.Interaction, _button: discord.ui.Button):
        from views.estadio_view import EstadioView
        from db.club_queries import obtener_club_id_por_usuario

        club_id = obtener_club_id_por_usuario(interaction.user.id)
        view = EstadioView(club_id, interaction.user.id)
        await interaction.response.edit_message(
            content=None,
            embed=view.actualizar_embed_inicial(club_id, interaction.user.id),
            view=view
        )


class VenderJugadorModal(discord.ui.Modal, title="Vender Jugador"):
    dorsal = discord.ui.TextInput(label="Dorsal del jugador", placeholder="Ej: 7", min_length=1, max_length=2)
    precio = discord.ui.TextInput(label="Precio de venta", placeholder="Ej: 500000", min_length=1, max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        from db import club_queries, jugador_queries
        from db.mercado_queries import publicar_jugador

        club_id = club_queries.obtener_club_id_por_usuario(interaction.user.id)
        try:
            dorsal_val = int(self.dorsal.value)
            precio_val = int(self.precio.value)
        except ValueError:
            await interaction.response.send_message("❌ El dorsal y el precio deben ser números.", ephemeral=True)
            return

        jugador = jugador_queries.obtener_jugador_por_numero(club_id, dorsal_val)
        if not jugador:
            await interaction.response.send_message("❌ No tienes ningún jugador con ese dorsal.", ephemeral=True)
            return

        if publicar_jugador(jugador[0], club_id, precio_val):
            await interaction.response.send_message(f"✅ ¡{jugador[1]} puesto en el mercado!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Este jugador ya está en venta o hubo un error.", ephemeral=True)