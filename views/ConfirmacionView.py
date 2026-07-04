from datetime import timedelta, datetime
import discord
import views.estadio_view
from config import TIEMPO_MEJORA_ESTADIO, NOMBRE_MONEDA
from db.database import get_connection


class ConfirmacionMejoraView(discord.ui.View):
    def __init__(self, club_id, coste):
        super().__init__(timeout=60)
        self.club_id = club_id
        self.coste = coste

    @discord.ui.button(label="Aceptar", style=discord.ButtonStyle.green)
    async def aceptar(self, interaction: discord.Interaction, _button: discord.ui.Button):
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar si tiene presupuesto (seguridad extra)
        cursor.execute('SELECT presupuesto FROM clubes WHERE id = ?', (self.club_id,))
        presupuesto = cursor.fetchone()[0]

        if presupuesto < self.coste:
            await interaction.response.send_message(f"❌ No tienes suficientes {NOMBRE_MONEDA} para pagar la mejora.",
                                                    ephemeral=True)
            conn.close()
            return

        # Restar dinero e iniciar la obra en una sola transacción
        fecha_fin = (datetime.now() + timedelta(hours=TIEMPO_MEJORA_ESTADIO)).isoformat()

        try:
            # Restamos el dinero
            cursor.execute('UPDATE clubes SET presupuesto = presupuesto - ? WHERE id = ?', (self.coste, self.club_id))
            # Iniciamos la construcción
            cursor.execute('UPDATE estadios SET fecha_finalizacion = ? WHERE club_id = ?', (fecha_fin, self.club_id))
            conn.commit()

            # Respuesta visual
            view = views.estadio_view.EstadioView(self.club_id, interaction.user.id)
            embed = view.actualizar_embed_inicial(self.club_id, interaction.user.id)

            await interaction.response.edit_message(
                content=f"🏗️ **¡Obras iniciadas!** Se han descontado {self.coste} {NOMBRE_MONEDA}. Tu estadio estará listo en {TIEMPO_MEJORA_ESTADIO} horas.",
                embed=embed,
                view=view
            )
        except Exception as e:
            conn.rollback()
            await interaction.response.send_message("❌ Error al procesar el pago.", ephemeral=True)
        finally:
            conn.close()

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.red)
    async def cancelar(self, interaction: discord.Interaction, _button: discord.ui.Button):
        # Crear la vista
        view = views.estadio_view.EstadioView(self.club_id, interaction.user.id)

        embed = view.actualizar_embed_inicial(self.club_id, interaction.user.id)

        await interaction.response.edit_message(
            content="Has cancelado la subida de nivel del estadio.",
            embed=embed,
            view=view
        )