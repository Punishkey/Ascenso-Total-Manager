import discord


class ManualSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Fundar Equipo", description="Empieza tu carrera desde cero", emoji="🏗️",
                                 value="fundar"),
        ]
        super().__init__(placeholder="Elige una opción...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "fundar":
            await interaction.response.send_message("Redirigiendo al proceso de fundación...", ephemeral=True)


class ManualView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(ManualSelect())


async def enviar_manual_tutorial(interaction: discord.Interaction):
    embeds = []

    # Caja 1: (Morado)
    e1 = discord.Embed(
        title="⚽ Introducción / Descripción general",
        color=discord.Color.blue()
    )
    e1.description = (
        "**Ascenso Total Mánager** es un bot de Discord que te convierte en el mánager de tu propio club de fútbol. "
        "Construye tu equipo desde cero, gestiona jugadores generados aleatoriamente, toma decisiones estratégicas "
        "y compite contra otros mánagers en un mundo persistente.\n\n"
        "Sin dependencias de licencias reales ni APIs externas, **Ascenso Total Mánager** ofrece total libertad creativa "
        "y una experiencia 100% original. Funda tu club, asciende divisiones y demuestra que tienes lo necesario "
        "para llegar a la cima. 🏆\n\n"
        "¡El fútbol es pasión, estrategia y **ascenso total**! 🚀"
    )
    embeds.append(e1)

    # Caja 2: (Amarillo/Dorado)
    e2 = discord.Embed(
        title="🛠️ Cómo Empezar (Tutorial Básico)",
        color=discord.Color.gold()
    )
    e2.description = (
        "Lee todo este tutorial y, abajo en el desplegable, selecciona **Fundar Equipo** y dale un nombre a tu club. 📝\n\n"
        "Una vez hecho esto, sucederá lo siguiente:\n"
        "• Se generarán **16 jugadores** de forma aleatoria con sus estadísticas propias. ⚽\n"
        "• Recibirás **1,000 Keycoins** para empezar a gestionar tus finanzas. 💰\n"
        "• Tendrás acceso al comando **/estadio**, donde se centraliza toda la operativa del juego. 🏟️"
    )
    embeds.append(e2)

    # Caja 3: (Rojo)
    e3 = discord.Embed(
        title="⚙️ Mecánicas Principales",
        color=discord.Color.green()
    )
    e3.add_field(name="Gestión de Club y Jugadores",
                 value="Crea y personaliza tu club. Gestiona una plantilla de jugadores con atributos realistas generados proceduralmente.",
                 inline=False)
    e3.add_field(name="Mercado de Fichajes", value="Compra, vende y negocia jugadores con otros mánagers.",
                 inline=False)
    e3.add_field(name="Partidos y Simulaciones",
                 value="Vive emocionantes encuentros con resultados basados en las estadísticas de tus jugadores, tácticas y forma actual.",
                 inline=False)
    e3.add_field(name="Progresión",
                 value="Sube de división, mejora instalaciones, desbloquea mejores jugadores y aumenta la reputación de tu club.",
                 inline=False)
    e3.add_field(name="Economía",
                 value="Administra tu presupuesto, ingresos por partidos, patrocinios y gastos en fichajes y entrenamiento.",
                 inline=False)
    embeds.append(e3)

    # Caja 4: (Verde)
    e4 = discord.Embed(
        title="🌟 Características Únicas",
        color=discord.Color.purple()
    )
    e4.add_field(name="Totalmente Independiente",
                 value="Sin marcas reales ni licencias, lo que permite una experiencia libre y sin problemas legales.",
                 inline=False)
    e4.add_field(name="Desarrollado desde Cero",
                 value="Creado con Python y discord.py, con arquitectura modular (Cogs) que facilita actualizaciones y nuevas funciones.",
                 inline=False)
    e4.add_field(name="Simulación Profunda",
                 value="Jugadores con atributos variados, sistema propio de generación y progresión.", inline=False)
    e4.add_field(name="Multi-jugador en Discord",
                 value="Compite en tiempo real con amigos o miembros de tu comunidad en un entorno social y competitivo.",
                 inline=False)
    e4.add_field(name="Persistencia Total",
                 value="Tu club y plantillas permanecen seguras incluso después de reinicios del bot.", inline=False)
    embeds.append(e4)

    # Caja 5: (Azul)
    e5 = discord.Embed(
        title="🚀 Futuro y Llamado a la Acción",
        color=discord.Color.orange()
    )
    e5.description = (
        "**Ascenso Total Mánager** está en desarrollo activo y tiene mucho potencial. Próximas actualizaciones incluirán "
        "más tácticas avanzadas, ligas automáticas, sistema de juveniles, mejoras de estadio y mucho más.\n\n"
        "**¿Quieres formar parte del ascenso?**\n"
        "• Prueba el bot en el servidor. 🎮\n"
        "• Únete a la comunidad y comparte tu progreso. 🤝"
    )
    embeds.append(e5)

    await interaction.response.send_message(embeds=embeds, view=ManualView(), ephemeral=True)