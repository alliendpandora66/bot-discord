from discord.ext import commands
import discord
import os
import json

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

# Cargar información de cuentas y dinero desde el archivo JSON
def cargar_datos():
    try:
        with open('dinero.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return {}

# Guardar información de cuentas y dinero en el archivo JSON
def guardar_datos(data):
    with open('dinero.json', 'w') as f:
        json.dump(data, f, indent=4)

# Inicializar cuentas al arrancar el bot
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command(name='hola', help='Saluda al bot.')
async def say_hello(ctx):
    await ctx.send('¡Hola!')

@bot.command(name='como_te_llamas', help='Preguntarle su nombre.')
async def ask_name(ctx):
    await ctx.send('Soy Canada-Bot, el bot oficial de Canada.')

@bot.command(name='economia', help='Puedes usar este comando para ver la economía.')
async def economy(ctx):
    await ctx.send('La economía es excelente.')

@bot.command(name='reglas', help='Puedes ir al canal de reglas.')
async def rules(ctx):
    await ctx.send('Entra al canal de Discord o Minecraft para ver las reglas.')

@bot.command(name='rango', help='Muestra los roles del usuario que ejecutó el comando.')
async def show_roles(ctx):
    user = ctx.author
    roles = [role.name for role in user.roles]
    roles_message = ', '.join(roles) if roles else 'Sin roles.'
    await ctx.send(f'Roles de {user.name}: {roles_message}')

@bot.command(name='crear', help='Crea una cuenta si no tienes una.')
async def crear_cuenta(ctx):
    user_id = str(ctx.author.id)
    data = cargar_datos()

    if user_id not in data:
        data[user_id] = {'saldo': 0}
        guardar_datos(data)
        await ctx.send('¡Cuenta creada con éxito!')
    else:
        await ctx.send('Ya tienes una cuenta.')

@bot.event
async def on_member_join(member):
    # Asignar el rol al miembro al unirse
    role_name = '👤 𝕸𝖎𝖊𝖒𝖇𝖗𝖔 👤'
    role = discord.utils.get(member.guild.roles, name=role_name)

    if role in member.roles:
        user_id = str(member.id)
        data = cargar_datos()
        if user_id not in data:
            data[user_id] = {'saldo': 0}
            guardar_datos(data)

@bot.command(name='cuenta', help='Ver el saldo de tu cuenta.')
async def ver_saldo(ctx):
    user_id = str(ctx.author.id)
    data = cargar_datos()

    if user_id in data:
        saldo = data[user_id]['saldo']
        await ctx.send(f'Saldo de {ctx.author.name}: ${saldo}')
    else:
        await ctx.send('Aún no tienes una cuenta registrada. Usa `$crear` para crear una.')

@bot.command(name='pago', help='Hacer un pago a otra cuenta. Uso: $pago <mención_usuario> <monto>')
async def hacer_pago(ctx, miembro: discord.Member, monto: int):
    if monto <= 0:
        await ctx.send('El monto debe ser mayor que cero.')
        return

    emisor_id = str(ctx.author.id)
    receptor_id = str(miembro.id)

    data = cargar_datos()

    if emisor_id not in data:
        await ctx.send('No tienes una cuenta registrada. Usa `$crear` para crear una.')
        return

    if receptor_id not in data:
        await ctx.send('La cuenta receptora no está registrada.')
        return

    saldo_emisor = data[emisor_id]['saldo']

    if saldo_emisor < monto:
        await ctx.send('No tienes suficiente dinero en tu cuenta para realizar este pago.')
        return

    # Realizar la transferencia
    data[emisor_id]['saldo'] -= monto
    data[receptor_id]['saldo'] += monto

    guardar_datos(data)

    await ctx.send(f'¡Pago de ${monto} a {miembro.name} realizado con éxito!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Comando no encontrado. ¡Escribe `$help` para ver la lista de comandos!')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Faltan argumentos. Asegúrate de proporcionar todos los argumentos necesarios.')
    else:
        print(f'Error: {error}')

@bot.command(name='help', help='Muestra la lista de comandos o información detallada sobre un comando específico.')
async def show_help(ctx, command_name: str = None):
    if command_name:
        command = bot.get_command(command_name)
        if command:
            await ctx.send(f'Ayuda para `{command.name}`: {command.help}')
        else:
            await ctx.send('Comando no encontrado.')
    else:
        help_message = 'Lista de comandos:\n'
        for command in bot.commands:
            help_message += f'`{bot.command_prefix}{command.name}`: {command.help}\n'
        await ctx.send(help_message)

my_secret = os.environ['TOKEN']
bot.run(my_secret)
