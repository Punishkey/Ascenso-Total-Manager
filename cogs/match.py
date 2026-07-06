import asyncio
import discord
import random
from discord import app_commands
from discord.ext import commands
from config import EVENTOS_NARRATIVA, NOMBRE_MONEDA, BASE_POR_PARTIDO, BONUS_RESULTADO
from db.club_queries import obtener_nombre_club, obtener_rival_ia, obtener_club_id_por_usuario
from db.database import get_connection
from db.jugador_queries import obtener_media_titular, obtener_jugador_aleatorio, obtener_id_jugador_aleatorio
from db.transaction_queries import registrar_resultado_partido
from views.estadio_view import VolverEstadioView
from db.merch_queries import (puede_vender, registrar_venta_catering, registrar_venta_camiseta,
                              obtener_precio_camiseta, obtener_precios_catering, calcular_penalizacion_precio)
from db.estadio_queries import obtener_configuracion_partido, actualizar_popularidad_partido


def registrar_evento_db(partido_id, jugador, equipo, tipo, minuto):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO eventos_partido
                          (partido_id, jugador_nombre, equipo_nombre, tipo_evento, minuto)
                      VALUES (?, ?, ?, ?, ?)''', (partido_id, jugador, equipo, tipo, minuto))
    conn.commit()
    conn.close()


def procesar_fin_partido(club_a_id, club_b_id, goles_favor, goles_contra):
    victoria = goles_favor > goles_contra
    base = BASE_POR_PARTIDO
    premio = BONUS_RESULTADO if victoria else 0
    total_ingresos_a = base + premio
    premio_rival = BONUS_RESULTADO if goles_contra > goles_favor else 0
    total_ingresos_b = base + premio_rival

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE clubes SET presupuesto = presupuesto + ? WHERE id = ?", (total_ingresos_a, club_a_id))
    cursor.execute("UPDATE clubes SET presupuesto = presupuesto + ? WHERE id = ?", (total_ingresos_b, club_b_id))
    conn.commit()
    conn.close()
    return {"partido": base, "victoria": premio}


async def simular_partido(interaction, club_a_id, nombre_a, club_b_id, nombre_b, es_local_a=True):
    # Cálculo de media ajustada con estados
    def obtener_media_ajustada(club_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT estado FROM jugadores WHERE club_id = ?", (club_id,))
        estados = cursor.fetchall()
        conn.close()
        media = obtener_media_titular(club_id)
        for (estado,) in estados:
            if estado == 'Tocado': media *= 0.95
        return media

    media_a = obtener_media_ajustada(club_a_id) + (2.0 if es_local_a else 0)
    media_b = obtener_media_ajustada(club_b_id) + (2.0 if not es_local_a else 0)

    partido_id_actual = registrar_resultado_partido(club_a_id, club_b_id, 0, 0)

    historial_jugadores = {}
    estado_tarjetas = {}
    tarjetas_jugadores = []
    posesion_a = 0
    posesion_b = 0
    ingresos_catering_a = 0
    ingresos_tienda_a = 0

    embed = discord.Embed(title=f"⚽ {nombre_a} vs {nombre_b}", color=discord.Color.green())
    embed.add_field(name=nombre_a, value=f"Media: {media_a:.1f}\nGoles: 0", inline=True)
    embed.add_field(name=nombre_b, value=f"Media: {media_b:.1f}\nGoles: 0", inline=True)
    msg = await interaction.followup.send(embed=embed)

    goles_a = 0
    goles_b = 0
    precios_base_catering = {"bebida": 2.0, "patatas": 3.0, "bocadillo": 5.0}

    # --- Guardar estado inicial ---
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nombre, velocidad, resistencia, anticipacion, serenidad, trabajo_equipo, precision_pases, control_balon, profesionalidad FROM jugadores WHERE club_id IN (?, ?)",
        (club_a_id, club_b_id))
    estado_inicial = {fila[0]: {"nombre": fila[1], "attr": list(fila[2:])} for fila in cursor.fetchall()}
    conn.close()


    for minuto in [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90]:
        await asyncio.sleep(3)
        factor_tiempo = (minuto / 90) + 0.5
        tipo_evento = random.choices(list(EVENTOS_NARRATIVA.keys()), weights=[0.03, 0.12, 0.15, 0.10, 0.60])[0]
        factor_evento = 2.0 if tipo_evento == "gol" else (1.2 if tipo_evento == "tarjeta" else 1.0)
        probabilidad_venta = 0.4 * factor_tiempo * factor_evento

        # Lógica de lesión durante el juego (Mejora integrada)
        jugador_res = obtener_jugador_aleatorio(club_a_id if random.random() < 0.5 else club_b_id)

        if isinstance(jugador_res, dict):
            nombre_jugador = jugador_res.get('nombre')
            estado_jugador = jugador_res.get('estado', 'Sano')
        else:
            nombre_jugador = jugador_res
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT estado FROM jugadores WHERE nombre = ? AND club_id = ?",
                           (nombre_jugador, club_a_id if random.random() < 0.5 else club_b_id))
            row = cursor.fetchone()
            estado_jugador = row[0] if row else 'Sano'
            conn.close()

        if estado_jugador == 'Tocado' and random.random() < 0.15:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE jugadores SET estado = 'Lesionado' WHERE nombre = ?", (nombre_jugador,))
            conn.commit()
            conn.close()

        prob_a = media_a / (media_a + media_b)
        protagonista_a = random.random() < prob_a
        club_id = club_a_id if protagonista_a else club_b_id
        club_nombre = nombre_a if protagonista_a else nombre_b

        es_local_actual = True if (club_id == club_a_id and es_local_a) or (
                club_id == club_b_id and not es_local_a) else False

        if es_local_actual:
            if puede_vender(club_id, 'catering'):
                precios_actuales = dict(obtener_precios_catering(club_id))
                prod = random.choice(list(precios_base_catering.keys()))
                precio_actual_prod = precios_actuales.get(prod, precios_base_catering[prod])
                penalizacion = calcular_penalizacion_precio(precio_actual_prod, precios_base_catering[prod])
                if random.random() < (probabilidad_venta * penalizacion):
                    cantidad = 1 if factor_evento < 1.5 else 2
                    registrar_venta_catering(club_id, prod, cantidad=cantidad)
                    if club_id == club_a_id: ingresos_catering_a += (precio_actual_prod * cantidad)

            if puede_vender(club_id, 'tienda'):
                j_id = obtener_id_jugador_aleatorio(club_id)
                if j_id:
                    precio_cam = obtener_precio_camiseta(j_id)
                    penalizacion_t = calcular_penalizacion_precio(precio_cam, 50.0)
                    if random.random() < (probabilidad_venta * 0.5 * penalizacion_t):
                        registrar_venta_camiseta(j_id, cantidad=1)
                        if club_id == club_a_id: ingresos_tienda_a += precio_cam

        if protagonista_a:
            posesion_a += 1
        else:
            posesion_b += 1

        jugador_nombre = nombre_jugador if nombre_jugador else "Jugador"
        if jugador_nombre not in historial_jugadores: historial_jugadores[jugador_nombre] = {"equipo": club_nombre,
                                                                                             "total": 0}
        historial_jugadores[jugador_nombre]["total"] += 1

        if tipo_evento == "tarjeta":
            if jugador_nombre not in estado_tarjetas: estado_tarjetas[jugador_nombre] = {"amarillas": 0,
                                                                                         "expulsado": False}
            if not estado_tarjetas[jugador_nombre]["expulsado"]:
                if random.random() < 0.2:
                    estado_tarjetas[jugador_nombre]["expulsado"] = True
                    tipo_tarjeta = "Roja"
                    icono = "🟥"
                else:
                    estado_tarjetas[jugador_nombre]["amarillas"] += 1
                    if estado_tarjetas[jugador_nombre]["amarillas"] >= 2:
                        estado_tarjetas[jugador_nombre]["expulsado"] = True
                        tipo_tarjeta = "Roja (doble amarilla)"
                        icono = "🟥"
                    else:
                        tipo_tarjeta = "Amarilla"
                        icono = "🟨"
                registrar_evento_db(partido_id_actual, jugador_nombre, club_nombre, tipo_tarjeta, minuto)
                texto = f"{icono} **{tipo_tarjeta}**: El árbitro amonesta a {jugador_nombre} del equipo {club_nombre}."
                tarjetas_jugadores.append(f"{icono} {tipo_tarjeta} | Min. {minuto}: {jugador_nombre} ({club_nombre})")
                if estado_tarjetas[jugador_nombre]["expulsado"]:
                    if protagonista_a:
                        media_a -= 5
                    else:
                        media_b -= 5
        elif tipo_evento == "gol":
            if random.random() < (prob_a if protagonista_a else 1 - prob_a):
                frase = random.choice(EVENTOS_NARRATIVA[tipo_evento])
                texto = frase.format(jugador=jugador_nombre, equipo=club_nombre)
                registrar_evento_db(partido_id_actual, jugador_nombre, club_nombre, "gol", minuto)
                if protagonista_a:
                    goles_a += 1
                else:
                    goles_b += 1
            else:
                texto = f"¡Gran ocasión de {jugador_nombre} del equipo {club_nombre}, pero el portero lo evita!"
        else:
            frase = random.choice(EVENTOS_NARRATIVA[tipo_evento])
            texto = frase.format(jugador=jugador_nombre, equipo=club_nombre)

        embed.description = f"**Minuto {minuto}'**: {texto}"
        embed.set_field_at(0, name=nombre_a, value=f"Media: {media_a:.1f}\nGoles: {goles_a}", inline=True)
        embed.set_field_at(1, name=nombre_b, value=f"Media: {media_b:.1f}\nGoles: {goles_b}", inline=True)
        await msg.edit(embed=embed)

    # --- Cálculo Entradas ---
    ingresos_tickets = 0
    asistencia = 0
    if es_local_a:
        capacidad, precio_entrada, popularidad, nivel = obtener_configuracion_partido(club_a_id)
        aforo_base = max(10, int(capacidad * 0.01))
        factor_elasticidad = 0.7 if precio_entrada >= (nivel * 1) else 1.0
        factor_rival = 1.2 if obtener_media_titular(club_b_id) > media_a else 0.8

        # Asistencia calculada con un suelo mínimo
        asistencia = int(aforo_base + (capacidad * (popularidad / 100) * factor_rival * factor_elasticidad))
        ingresos_tickets = asistencia * precio_entrada

    # --- Popularidad ---
    cambio_a = actualizar_popularidad_partido(club_a_id, goles_a > goles_b)
    cambio_b = actualizar_popularidad_partido(club_b_id, goles_b > goles_a)

    def obtener_mensaje_popularidad(cambio):
        if cambio > 0: return "¡La afición está eufórica y la popularidad sube!"
        return "La afición está decepcionada por el resultado..."

    resultados = procesar_fin_partido(club_a_id, club_b_id, goles_a, goles_b)
    total_ingresos_final = resultados['partido'] + resultados[
        'victoria'] + ingresos_catering_a + ingresos_tienda_a + ingresos_tickets

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT jugador_nombre, minuto FROM eventos_partido WHERE partido_id = ? AND tipo_evento = 'gol'",
                   (partido_id_actual,))
    goleadores = cursor.fetchall()
    conn.close()
    texto_goles = "\n".join([f"⚽ Min. {m}: {j}" for j, m in goleadores]) if goleadores else "Sin goles"

    # --- Resumen Final ---
    total_eventos = posesion_a + posesion_b
    porcentaje_a = int((posesion_a / total_eventos) * 100) if total_eventos > 0 else 50
    porcentaje_b = 100 - porcentaje_a
    barra_posesion = ("█" * int(porcentaje_a / 10)) + ("░" * (10 - int(porcentaje_a / 10)))
    jugador_estrella = max(historial_jugadores, key=lambda x: historial_jugadores[x]["total"])
    datos_estrella = historial_jugadores[jugador_estrella]

    # --- Comparar evolución ---
    nombres_attr = ["Vel", "Res", "Anti", "Sere", "Trab", "Pase", "Ctrl", "Prof"]
    evolucion_texto = []

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, velocidad, resistencia, anticipacion, serenidad, trabajo_equipo, precision_pases, control_balon, profesionalidad FROM jugadores WHERE club_id IN (?, ?)",
        (club_a_id, club_b_id))
    for fila in cursor.fetchall():
        j_id, *attr_nuevos = fila
        if j_id in estado_inicial:
            cambios_jugador = []
            for i in range(len(attr_nuevos)):
                dif = attr_nuevos[i] - estado_inicial[j_id]["attr"][i]
                if dif != 0:
                    signo = "+" if dif > 0 else ""
                    cambios_jugador.append(f"{nombres_attr[i]} {signo}{dif}")

            if cambios_jugador:
                evolucion_texto.append(f"**{estado_inicial[j_id]['nombre']}**: {', '.join(cambios_jugador)}")
    conn.close()


    resumen_embed = discord.Embed(title="📊 Resumen del Partido", color=discord.Color.green())
    resumen_embed.add_field(name="Resultado Final", value=f"**{nombre_a} {goles_a} - {goles_b} {nombre_b}**",
                            inline=False)
    resumen_embed.add_field(name="Evolución de Popularidad",
                            value=f"{nombre_a}: {obtener_mensaje_popularidad(cambio_a)}\n{nombre_b}: {obtener_mensaje_popularidad(cambio_b)}",
                            inline=False)
    resumen_embed.add_field(name="Ingresos del Partido", value=(
        f"⚽ Partido jugado: +{resultados['partido']} {NOMBRE_MONEDA}\n"
        f"🏆 Victoria: +{resultados['victoria']} {NOMBRE_MONEDA}\n"
        f"🎟️ Entradas ({asistencia} personas): +{ingresos_tickets:.0f} {NOMBRE_MONEDA}\n"
        f"🌭 Catering: +{ingresos_catering_a:.0f} {NOMBRE_MONEDA}\n"
        f"👕 Tienda: +{ingresos_tienda_a:.0f} {NOMBRE_MONEDA}\n"
        f"--------------------------\n"
        f"💰 **Total: +{total_ingresos_final:.0f} {NOMBRE_MONEDA}**"
    ), inline=False)
    resumen_embed.add_field(name="Goleadores", value=texto_goles, inline=False)
    resumen_embed.add_field(name="Posesión del balón",
                            value=f"{nombre_a}: {porcentaje_a}% | {nombre_b}: {porcentaje_b}%\n`{barra_posesion}`",
                            inline=False)
    resumen_embed.add_field(name="Jugador Destacado",
                            value=f"⭐ {jugador_estrella} ({datos_estrella['equipo']}) con {datos_estrella['total']} intervenciones",
                            inline=False)
    resumen_embed.add_field(name="Tarjetas Mostradas",
                            value="\n".join(tarjetas_jugadores) if tarjetas_jugadores else "Partido limpio.",
                            inline=False)

    if evolucion_texto:
        contenido = "\n".join(evolucion_texto[:5])
        resumen_embed.add_field(name="📈 Evolución de Atributos", value=contenido, inline=False)
    else:
        resumen_embed.add_field(name="📈 Evolución de Atributos", value="Sin cambios significativos.", inline=False)

    view_final = VolverEstadioView(club_a_id, interaction.user.id)
    await interaction.followup.send(embed=resumen_embed, view=view_final)


class MatchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.jugadores_en_partido = set()

    @app_commands.command(name="partido", description="Juega un partido amistoso contra un club de la IA")
    async def partido(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id in self.jugadores_en_partido:
            await interaction.response.send_message("❌ ¡Ya tienes un partido en curso!", ephemeral=True)
            return
        club_usuario_id = obtener_club_id_por_usuario(interaction.user.id)
        if not club_usuario_id:
            await interaction.response.send_message("❌ Primero debes crear un club.", ephemeral=True)
            return
        rival_data = obtener_rival_ia(club_usuario_id)
        if not rival_data:
            await interaction.response.send_message("❌ No hay otros clubes disponibles.", ephemeral=True)
            return
        rival_id, rival_nombre = rival_data
        club_usuario_nombre = obtener_nombre_club(club_usuario_id)
        self.jugadores_en_partido.add(user_id)
        await interaction.response.defer()
        try:
            await simular_partido(interaction, club_usuario_id, club_usuario_nombre, rival_id, rival_nombre)
        finally:
            self.jugadores_en_partido.remove(user_id)


async def setup(bot):
    await bot.add_cog(MatchCog(bot))