import discord
from discord import ui
from datetime import datetime, timedelta
from db.estadio_queries import obtener_datos_spa, tiene_spa, aplicar_recuperacion_spa
from db.club_queries import obtener_presupuesto, restar_dinero
from db.database import get_connection
from config import NOMBRE_MONEDA


class InstalacionesView(ui.View):
    def __init__(self, club_id, user_id):
        super().__init__(timeout=None)
        self.club_id = club_id
        self.user_id = user_id

    def get_embed(self):
        datos = obtener_datos_spa(self.club_id)

        # Validación de seguridad:
        if datos is None:
            return discord.Embed(title="Error", description="No se encontraron datos del SPA para este club.",
                                 color=discord.Color.red())
        nivel = datos.get('nivel', 0)
        nivel_estadio = datos.get('nivel_estadio', 1)
        fecha_fin_str = datos.get('fecha_fin')

        embed = discord.Embed(title="🏗️ Panel de Instalaciones", color=discord.Color.blue())

        status = "❌ Bloqueado"
        if nivel > 0:
            status = f"✅ SPA Nivel {nivel}"

        if fecha_fin_str:
            fecha_fin = datetime.fromisoformat(fecha_fin_str)
            if datetime.now() < fecha_fin:
                status = f"🚧 En construcción\nFinaliza: {fecha_fin.strftime('%H:%M:%S')}"

        embed.add_field(name="🧖 SPA de Recuperación", value=f"Estado: {status}\nNivel actual: {nivel}/{nivel_estadio}",
                        inline=False)
        return embed

    @ui.button(label="Construir/Mejorar SPA", style=discord.ButtonStyle.primary, emoji="🛠️")
    async def mejorar_spa(self, interaction: discord.Interaction, _button: ui.Button):
        datos = obtener_datos_spa(self.club_id)
        nivel_actual = datos['nivel']
        nivel_estadio = datos['nivel_estadio']

        if nivel_actual >= nivel_estadio:
            await interaction.response.send_message("❌ El SPA no puede superar el nivel de tu estadio.", ephemeral=True)
            return

        coste = 20000 + (nivel_actual * 10000)
        presupuesto = obtener_presupuesto(self.club_id)

        if presupuesto < coste:
            await interaction.response.send_message(f"❌ Necesitas {coste} {NOMBRE_MONEDA} para esta mejora.",
                                                    ephemeral=True)
            return

        horas_construccion = 2 + nivel_estadio
        fecha_fin = (datetime.now() + timedelta(hours=horas_construccion)).isoformat()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE estadio_instalaciones SET spa_nivel = ?, fecha_ultima_construccion = ? WHERE club_id = ?",
            (nivel_actual + 1, fecha_fin, self.club_id))
        conn.commit()
        conn.close()

        restar_dinero(self.club_id, coste)

        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @ui.button(label="Usar SPA", style=discord.ButtonStyle.secondary, emoji="🧖")
    async def usar_spa(self, interaction: discord.Interaction, _button: ui.Button):
        if not tiene_spa(self.club_id):
            await interaction.response.send_message("❌ Debes construir el SPA primero.", ephemeral=True)
            return

        view = SeleccionarJugadorSpaView(self.club_id, self.user_id)
        await interaction.response.send_message("Selecciona al jugador que quieres recuperar:", view=view,
                                                ephemeral=True)

    @ui.button(label="Volver al Estadio", style=discord.ButtonStyle.danger, emoji="🏟️")
    async def volver(self, interaction: discord.Interaction, _button: ui.Button):
        from views.estadio_view import EstadioView
        view = EstadioView(self.club_id, self.user_id)
        embed = view.actualizar_embed_inicial(self.club_id, self.user_id)
        await interaction.response.edit_message(embed=embed, view=view)


class SeleccionarJugadorSpaView(ui.View):
    def __init__(self, club_id, user_id):
        super().__init__(timeout=60)
        self.club_id = club_id
        self.user_id = user_id
        self.add_item(JugadorSelect(club_id))


class JugadorSelect(ui.Select):
    def __init__(self, club_id):
        self.club_id = club_id
        conn = get_connection()
        cursor = conn.cursor()
        # Filtro: Solo jugadores Sano o Tocado, NO lesionados
        cursor.execute("SELECT id, nombre, energia, estado FROM jugadores WHERE club_id = ? AND estado != 'Lesionado' AND energia < 100", (club_id,))
        jugadores = cursor.fetchall()
        conn.close()

        options = [
            discord.SelectOption(label=f"{j[1]} - {j[3]} ({j[2]}%)", value=str(j[0]))
            for j in jugadores
        ]

        super().__init__(placeholder="Elige un jugador para el SPA...", options=options if options else [
            discord.SelectOption(label="No hay jugadores disponibles", value="none")])

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            return await interaction.response.send_message("No hay jugadores que necesiten energía.", ephemeral=True)

        jugador_id = int(self.values[0])
        resultado = aplicar_recuperacion_spa(self.club_id, jugador_id)

        await interaction.response.send_message(resultado, ephemeral=True)
        return None