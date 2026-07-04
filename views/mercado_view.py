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
            # Diccionario de mapeo de posiciones

            mapeo_posiciones = {
                "1": "POR",
                "2": "DFC",
                "3": "MCD",
                "4": "MC",
                "5": "EXT",
                "6": "DC"
            }

            fichaje = self.jugadores[self.current_page]
            fichaje_id, nombre, pos, precio, club, media = fichaje

            # Convertimos el ID de posición a texto, o dejamos el número si no existe en el diccionario
            nombre_posicion = mapeo_posiciones.get(str(pos), str(pos))

            # Formateo seguro
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
            print(f"❌ ERROR CRÍTICO en get_embed: {e}")
            return discord.Embed(title="Error", description=f"Error en datos: {e}", color=discord.Color.red())

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary, row=0)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Comprar", style=discord.ButtonStyle.green, row=1)
    async def comprar(self, interaction: discord.Interaction, _button: discord.ui.Button):
        from db.club_queries import obtener_club_id_por_usuario

        comprador_club_id = obtener_club_id_por_usuario(interaction.user.id)
        # Validación extra: si no tiene club
        if not comprador_club_id:
            await interaction.response.send_message("❌ No tienes un club registrado.", ephemeral=True)
            return

        fichaje_id = self.jugadores[self.current_page][0]
        exito, mensaje = ejecutar_compra(fichaje_id, comprador_club_id)

        if exito:
            # Recargamos mercado
            self.jugadores = obtener_jugadores_en_mercado()
            self.current_page = 0

            # Si el mercado se quedó vacío, editamos para avisar
            if not self.jugadores:
                await interaction.response.edit_message(content="🛒 El mercado se ha quedado vacío.", embed=None,
                                                        view=None)
            else:
                await interaction.response.edit_message(content="✅ ¡Jugador fichado!", embed=self.get_embed(),
                                                        view=self)
        else:
            await interaction.response.send_message(f"❌ {mensaje}", ephemeral=True)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary, row=0)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.jugadores) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Mis Ventas", style=discord.ButtonStyle.secondary, row=1)
    async def mis_ventas(self, interaction: discord.Interaction, button: discord.ui.Button):
        from db.club_queries import obtener_club_id_por_usuario
        club_id = obtener_club_id_por_usuario(interaction.user.id)

        ventas = obtener_jugadores_en_venta_del_club(club_id)
        if not ventas:
            await interaction.response.send_message("❌ No tienes ningún jugador en venta.", ephemeral=True)
            return

        await interaction.response.send_message("Selecciona qué jugador quieres retirar:",
                                                view=RetirarVentaView(club_id), ephemeral=True)

    @discord.ui.button(label="Volver al Estadio", style=discord.ButtonStyle.secondary, row=2)
    async def volver_estadio(self, interaction: discord.Interaction, button: discord.ui.Button):
        from views.estadio_view import EstadioView

        # Obtenemos el club_id necesario para EstadioView
        from db.club_queries import obtener_club_id_por_usuario
        club_id = obtener_club_id_por_usuario(interaction.user.id)

        # Creamos la vista del estadio
        view = EstadioView(club_id, interaction.user.id)

        # Volvemos a mostrar el embed inicial del estadio
        await interaction.response.edit_message(
            content=None,
            embed=view.actualizar_embed_inicial(),
            view=view
        )