import discord
from db.club_queries import (get_connection, mejorar_servicio_db,
                             check_y_aplicar_mejora_servicio,
                             obtener_tiempo_restante_construccion)

class ServiciosView(discord.ui.View):
    def __init__(self, club_id, user_id):
        super().__init__(timeout=60)
        self.club_id = club_id
        self.user_id = user_id
        self.actualizar_estado_botones()

    def actualizar_estado_botones(self):
        # 1. Aplicar lógica de BD primero
        check_y_aplicar_mejora_servicio(self.club_id, 'nivel_catering')
        check_y_aplicar_mejora_servicio(self.club_id, 'nivel_tienda')

        # 2. Obtener niveles y tiempos
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT nivel_catering, nivel_tienda FROM estadio_servicios WHERE club_id = ?', (self.club_id,))
        niveles = cursor.fetchone()
        conn.close()
        cat, tienda = niveles if niveles else (1, 1)

        tiempo_cat = obtener_tiempo_restante_construccion(self.club_id, 'catering')
        tiempo_tienda = obtener_tiempo_restante_construccion(self.club_id, 'tienda')

        # 3. Configurar botones
        # Catering
        if tiempo_cat and tiempo_cat != "FINALIZADO":
            self.mejorar_catering.disabled = True
            self.mejorar_catering.label = "Construyendo..."
        else:
            self.mejorar_catering.disabled = (cat >= 10)
            self.mejorar_catering.label = "Mejorar Catering"

        # Tienda
        if tiempo_tienda and tiempo_tienda != "FINALIZADO":
            self.mejorar_tienda.disabled = True
            self.mejorar_tienda.label = "Construyendo..."
        else:
            self.mejorar_tienda.disabled = (tienda >= 10)
            self.mejorar_tienda.label = "Mejorar Tienda"

        # 4. Crear el Embed aquí para evitar tenerlo como atributo flotante
        self.embed = discord.Embed(title="🌭 Servicios del Estadio", color=discord.Color.gold())
        self.embed.add_field(name="Catering", value=f"Nivel: **{cat}**", inline=True)
        self.embed.add_field(name="Tienda", value=f"Nivel: **{tienda}**", inline=True)
        self.embed.description = "Mejora tus servicios para aumentar los ingresos. Las obras tardan 6h + 1h por nivel."

    @discord.ui.button(label="Mejorar Catering", style=discord.ButtonStyle.primary, emoji="🌭")
    async def mejorar_catering(self, interaction: discord.Interaction, _button: discord.ui.Button):
        print("DEBUG: Botón Catering pulsado")  # <--- AÑADE ESTO
        exito, mensaje = mejorar_servicio_db(self.club_id, 'nivel_catering')
        print(f"DEBUG: Resultado BD: {exito}, {mensaje}")  # <--- AÑADE ESTO
        if exito:
            self.actualizar_estado_botones()
            await interaction.response.edit_message(embed=self.embed, view=self)
            print("DEBUG: Mensaje editado correctamente")  # <--- AÑADE ESTO
        else:
            await interaction.response.send_message(f"❌ {mensaje}", ephemeral=True)

    @discord.ui.button(label="Mejorar Tienda", style=discord.ButtonStyle.primary, emoji="👕")
    async def mejorar_tienda(self, interaction: discord.Interaction, _button: discord.ui.Button):
        exito, mensaje = mejorar_servicio_db(self.club_id, 'nivel_tienda')
        if exito:
            self.actualizar_estado_botones()
            await interaction.response.edit_message(embed=self.embed, view=self)
        else:
            await interaction.response.send_message(f"❌ {mensaje}", ephemeral=True)