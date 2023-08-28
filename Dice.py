from time import mktime
import discord
from discord.ext import commands
import random
import asyncio
import re
from datetime import datetime
import mysql.connector 

conn = mysql.connector.connect(
    user="root",
    password="3141592",
    host="127.0.0.1",
    database="bot",
    auth_plugin='mysql_native_password'
)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)
canal_destino = None
active_countdowns = {} 
bot_ativo = True
intents.typing = False
intents.presences = False


bot.remove_command('help')

@bot.event
async def on_ready():
    print(f'LOGADO EM {bot.user}')
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name="a"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.lower()
    if content != content.lower():
        embed = discord.Embed(
            title='Opa! Algo deu errado..',
            description=f'Deu algum probleminha ai! Tente usar !ajuda {message.author.mention}.',
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)

    await bot.process_commands(message)
msg = ['oi', 'olá', 'ola', 'hi', 'hello']
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    conteudo = message.content.lower()
    for palavra in msg:
        if palavra in conteudo:
            await message.author.send(f"Aoba, tudo bem?")
            return

    await bot.process_commands(message)

@bot.command(name='help', with_app_command=True)
async def help(ctx):
    embed = discord.Embed(title='Ajuda', description='Aqui está a lista de comandos disponíveis:', color=0x740000)
    embed.add_field(name='!r <XdY>, ou !roll', value='O famoso rola um d20, rola um dado de 6 a 100 lados.', inline=False)
    embed.add_field(name='!escolhe (opção1) (opção2)', value='Tá em dúvida? Que tal uma ajudinha do bot!', inline=False)
    embed.add_field(name='!ppt <pedra,pepel ou tesoura>', value='Pedra, papel e tesoura; Envie ppt (pedra, papel ou tesoura). O bot escolhera um aleatório para ele', inline=False)
    embed.add_field(name='!moeda', value='Quer brincar de cara ou coroa?', inline=False)
    embed.add_field(name='!calc (+, -, *, **, /)', value='1 + 1 = x?', inline=False)
    embed.add_field(name='!contagem (iniciar)(cancelar)', value='Está com padrão de segundos, então 120 = 2m, etc. "!contagem iniciar 10"', inline=False)
    embed.add_field(name='!tempo', value='Parecido com !contagem, porém funciona da seguinte forma: Você ira enviar "!tempo <comando> <1s,1m,1h,1d>" e ele irá executar o comando depois do tempo determiado.', inline=False)
    embed.add_field(name='!forca', value='Um joguinho da forca para descontrair ia ser legal, não?', inline=False)
    embed.add_field(name='!cantada', value='Uma cantada pra mandar pro crush? Ou esteja se sentindo carente ksks', inline=False)
    embed.add_field(name='!anagrama', value='Um joguinho de anagrama, vai.', inline=False)
    embed.add_field(name='!ship (nome) (nome)', value='Um joguinho pra ver suas chances com a(o) crushzinho :3', inline=False)
    embed.add_field(name='!tapa', value='Quer dar um tapa naquela pessoa irritante?', inline=False)
    embed.add_field(name='!abraço', value='Retribua com um abraço para aquela pessoa especial!', inline=False)
    embed.add_field(name='!beijo', value='Hmm, beijinho bom..', inline=False)
    embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
    await ctx.message.reply(embed=embed)



@bot.group()
async def shop(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(title='Ajuda', description='Aqui está a lista de comandos disponíveis:', color=0x740000)
        embed.add_field(name='!shop buy', value='Fazer suas compras', inline=False)
        embed.add_field(name='!shop ver', value='Para ver os itens diponiveis', inline=False)
        embed.add_field(name='!daily', value='Pegue suas recompensas diarias para não ficar zerado!', inline=False)
        embed.add_field(name='!inv', value='Olhe seu inventario!', inline=False)
        embed.set_footer(text='Para mais informações, manda mensagem para o Guimts. Por enquanto alguns comandos ainda estão em desenvolvimento!')
        await ctx.message.reply(embed=embed)
        return

@shop.command()
async def ver(ctx):
    global conn
    sql = """
        select
        i.nome, 
        i.preco, 
        i.estoque, 
        i.descricao,
        i.id
        from bot.tbitens i
        where i.ativo = 1
    """ 
    c = conn.cursor() 
    c.execute(sql)
    r = c.fetchall()

    embed = discord.Embed(title='LOJINHA', description='ITENS DISPONÍVEIS', color=0x740000)
    if len(r) > 0:
            
        for tupla in r:
            
            embed.add_field(name=str(tupla[4])+" - "+tupla[0]+f" - Estoque: {tupla[2]}", value=tupla[3]+f" - Preço: {tupla[1]} moedas de prata!", inline=False)

    else:
        embed.add_field(name='**NENHUM ITEM DISPONIVEL**', value='', inline=False)
    embed.set_footer(text='Use !buy e o número do item desejado!')
    await ctx.send(embed=embed)

@shop.command()
@commands.has_permissions(administrator=True) 

async def delete(ctx, item=None):
    if item is None:
        await ctx.message.reply('Forneça um item para deletar!')
        return
    
    global conn
    sql = f"delete from bot.tbitens where nome = '{item}'"
    c = conn.cursor() 
    c.execute(sql)
    conn.commit()
    await ctx.message.reply(f'``{item}`` deletado com sucesso!')




@shop.command()
async def buy(ctx, item, qtd):
    user_id = ctx.author.id
#
#

@shop.command()
@commands.has_permissions(administrator=True) 
async def add(ctx, nome=None, preco=None, estoque=None, desc=None):
    if nome is None or preco is None or estoque is None or desc is None:    
        await ctx.message.reply('Forneça o item, o preço, a quantidade e a descrição!')
        return

    global conn
    sql = f"insert into bot.tbitens(nome, preco, estoque, descricao) values('{str(nome)}',{int(preco)}, {int(estoque)}, '{str(desc)}')"

    c = conn.cursor() 
    c.execute(sql)
    conn.commit()
    
    await ctx.message.reply('Item adicionado')

@bot.command()
async def myid(ctx):
    user_id = ctx.author.id
    await ctx.send(f"Seu ID de usuário é: {user_id}")
    
@shop.command()
@commands.has_permissions(administrator=True) 

async def coinset(ctx, moedas, users):
    sql =  f"""
        update 
        bot.tbmoeda     
        set moedas = {moedas},
        where id_usuario = '{users}'
    """
    c = conn.cursor() 
    c.execute(sql)
    conn.commit()

    await ctx.message.reply(f"Moedas de {users} foram atualizadas para {moedas}")

@bot.command()
async def inv(ctx):
    user_id = ctx.author.id

    global conn
    sql = f"""
        select
        u.id_discord, 
        i.nome,
        ui.quantidade,
        m.moedas,
        d.descricao
        from bot.tbuser u
        join bot.tbuserinv ui on ui.id_user = u.id
        left join bot.tbitens i on i.id = ui.id_item
        left join bot.tbitens d on i.id = d.descricao
        join bot.tbmoeda m on m.id_usuario = u.id
        where u.id_discord = {user_id}
    """ 

    c = conn.cursor() 
    c.execute(sql)
    s = c.fetchall()
    embed = discord.Embed(title='INVENTARIO', description=f'ITENS DE {ctx.author.mention}', color=0x71368A)
    if len(s) > 0:
            
        for palavra in s:
            
            embed.add_field(name=''+f" - Item: {palavra[1]}", value=''+f" - Quantidade: {palavra[2]}", inline=False)

    else:

        embed.add_field(name='**NENHUM ITEM DISPONIVEL**', value='', inline=False)
    embed.add_field(name='❛ ━━━━━━･❪ ❁ ❫ ･━━━━━━ ❜'"", value=f'- Moedas: {palavra[3]}'+f"", inline=False)
    await ctx.send(embed=embed)
    return

@bot.command()
async def daily(ctx):
    global conn
    user_id = ctx.author.id
    
    sql  = f"""
        select
        m.moedas,
        u.id,
        if(UNIX_TIMESTAMP(current_date) - m.cooldown < 86400, 1, 0),
        m.cooldown
        from bot.tbuser u
        join bot.tbmoeda m on m.id_usuario = u.id
        where u.id_discord = {user_id}
    """
    
    c = conn.cursor()
    c.execute(sql)
    r = c.fetchall()


    if r[0][2] == 1:
        await ctx.message.reply(f"Você já resgatou seu daily\nUltimo resgate: {datetime.utcfromtimestamp(float(r[0][3])).strftime('%Y-%m-%d %H:%M:%S')}")
        return

    moedas = r[0][0]
    daily = random.randrange(5,51)
    moedasDaily = moedas + daily



    sql = f"""
        update 
        bot.tbmoeda     
        set moedas = {moedasDaily},
        cooldown = '{(mktime(datetime.now().timetuple()))}'
        where id_usuario = {r[0][1]}
    """


    c = conn.cursor()
    c.execute(sql)
    conn.commit()
    
  
    await ctx.message.reply(f"Você tinha {moedas}, e ganhou {daily}, agora tem {moedasDaily}!")
    


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title='Erro de Comando',
            description=f'O comando `{ctx.message.content}` não foi encontrado. Tente usar `!ajuda`!',
            color=discord.Color.red()
        )
        await ctx.message.reply(embed=embed)
    else:
        print(f'Erro durante a execucao do comando: {error}')


ship_results = {}
    
@bot.command()
async def ship(ctx, arg1=None, arg2=None):
    if arg1 is None or arg2 is None:
        await ctx.message.reply("Por favor, dê-me dois nomes para continuarmos! :3")
        return

    key = f"{arg1.lower()}_{arg2.lower()}"

    if key in ship_results:
        percentage, message = ship_results[key]
    else:
        percentage = random.randint(0, 100)
        ship_results[key] = (percentage, None)

    await ctx.message.reply('❤️ **Huuum, vamos ver...** ❤️')
    await asyncio.sleep(1)
    await ctx.send(f'**{arg1}** deve ter uma chance de cerca de **{percentage}%** com **{arg2}** 👀')

    love = ['Ame a si mesmo!']
    love2 = ['Você já tem um não, agora busque o sim!']
    love3 = ['Se você quer, não custa tentar ein!']

    if percentage <= 50:
        await ctx.send(random.choice(love))
    elif percentage <= 80:
        await ctx.send(random.choice(love2))
    else:
        await ctx.send(random.choice(love3))

    if message is not None:
        await ctx.send(message)

gifs_beijos = [
    "https://media.tenor.com/217aKgnf16sAAAAM/kiss.gif",
    "https://media.tenor.com/fiafXWajQFoAAAAC/kiss-anime.gif",
    "https://media.tenor.com/BbU3DflfH_UAAAAM/kiss.gif",
    "https://media.tenor.com/QjMZ6Dx33_QAAAAC/kuss-kussi.gif",
    "https://i.pinimg.com/originals/2d/c1/d4/2dc1d4306778b0b7b6ca67d1d3e219f5.gif",
    "https://i.pinimg.com/originals/4d/67/84/4d6784bcad9589f99efd63f9474f841b.gif"
]

@bot.command()
async def calc(ctx, *, expression):
    try:
        result = eval(expression)
        await ctx.send(f"{expression} = {result}")
    except Exception as e:
        print(f"Erro ao calcular: {e}")

@bot.command()
async def beijo(ctx, member: discord.Member=None):
    if member is None:
        await ctx.message.reply("> Por favor forneça um nome.")
        return
        
    if member == ctx.author:
        await ctx.message.reply("Você não pode se beijar!")
    else:
        gif_url = random.choice(gifs_beijos)
        embed = discord.Embed(title="Beijinho :3", description=f"❤{ctx.author.mention} deu um beijo em {member.mention}!❤", color=0xFFC0CB)
        embed.set_image(url=gif_url)
        await ctx.send(embed=embed)

gifs_tapa = [
    "https://gifdb.com/images/high/patrick-star-glove-slap-37o9zy7fx6kucnjg.gif",
    "https://i.pinimg.com/originals/d1/49/69/d14969a21a96ec46f61770c50fccf24f.gif",
    "https://i.pinimg.com/originals/40/fa/32/40fa327344c9a71783b1cd77afa19ac9.gif",
    "https://cdn.quotesgram.com/img/97/60/1011194420-Sad-Pikachu-Clone-Pikachu-Dont-Want-To-Fight-Anymore-In-Pokemon-The-First-Movie-Gif.gif"

]

@bot.command()
async def tapa(ctx, member: discord.Member=None):
    if member is None:
        await ctx.message.reply("> Por favor forneça um nome.")
        return
        
    if member == ctx.author:
        await ctx.message.reply("Não se bata, você não merece isso!")
    else:
        gif_url = random.choice(gifs_tapa)
        embed = discord.Embed(title="Tapa!", description=f"{ctx.author.mention} deu um tapa em {member.mention}! >:(", color=0xFFC0CB)
        embed.set_image(url=gif_url)
        await ctx.send(embed=embed)

gifs_hug = [
    "https://gifdb.com/images/high/peach-and-goma-hug-m2o3js9u468ergqx.gif",
    "https://i.pinimg.com/originals/11/bb/43/11bb43404d06d1adabd683953fd8e294.gif",
    "https://usagif.com/wp-content/uploads/hugs-2.gif",

]

@bot.command()
async def abraço(ctx, member: discord.Member=None):                    
    if member is None:
        await ctx.message.reply("> Por favor forneça um nome.")
        return
        
    if member == ctx.author:
        await ctx.send("Você não pode se abraçar!")
    else:
        gif_url = random.choice(gifs_hug)
        embed = discord.Embed(title="Abraço ❤", description=f"❤{ctx.author.mention} deu um abraço em {member.mention}!❤", color=0xFFC0CB)
        embed.set_image(url=gif_url)
        await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def banana(ctx, channel_name=None):
    if channel_name is None:
        await ctx.message.reply("Por favor, forneça o nome do novo canal!")
        return
    category = ctx.channel.category

    await ctx.channel.delete()

    new_channel = await category.create_text_channel(channel_name)

casais = {}
    

@bot.command()
async def casar(ctx, pessoa: discord.Member):

    if ctx.author in casais:
        await ctx.send(f"Você já está casado com {pessoa}!!! Tá maluco?? Use ``!divorciar`` caso não queira mais...")

    elif pessoa in casais.values():
        await ctx.send("A pessoa que você deseja casar já está casada! Safadinho")
    else:
        casais[ctx.author] = pessoa
        await ctx.message.reply(f"Hmmm casalzinho novo! :3\n{ctx.author.mention} e {pessoa.mention} estão casados agora!")

@bot.command()
async def divorciar(ctx):

    if ctx.author in casais:
        ex_parceiro = casais.pop(ctx.author)
        await ctx.send(f"{ctx.author.mention} e {ex_parceiro.mention} estão divorciados agora...")
    else:
        await ctx.send("Você não está casado!")

@bot.command()
@commands.has_permissions(administrator=True) 
async def alterar(ctx, arg1=None, arg2=None, novo_percentual=None):
    if arg1 is None or arg2 is None or novo_percentual is None:
        await ctx.message.reply("Por favor, forneça os argumentos necessários para a alteração!")
        return

    key = f"{arg1.lower()}_{arg2.lower()}"

    if key in ship_results:
        resultado_anterior = ship_results[key]
        ship_results[key] = (novo_percentual, resultado_anterior[1])
        resultado_mudado = await ctx.send(f"O resultado para **{arg1}** e **{arg2}** foi alterado para **{novo_percentual}%**")
        await asyncio.sleep(2)
        await ctx.message.delete()
        await resultado_mudado.delete()
    else:
        await ctx.send("Não há resultado anterior para esses nomes.")
        

@bot.group()
async def contagem(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Você deve fornecer um subcomando válido, como 'iniciar' ou 'cancelar'.")

@contagem.command()
async def iniciar(ctx, tempo: int):
    if tempo <= 0:
        await ctx.send("O tempo deve ser um valor positivo em segundos.")
        return
    
    countdown_id = ctx.message.author.id 
    if countdown_id in active_countdowns:
        await ctx.send("Você já tem uma contagem em andamento.")
        return

    active_countdowns[countdown_id] = True
    for i in range(tempo, 0, -1):
        if countdown_id not in active_countdowns:
            
            return

        await ctx.send(f"{i}...")
        await asyncio.sleep(1)
    
    del active_countdowns[countdown_id]
    await ctx.send("Contagem concluída!")

@contagem.command()
async def cancelar(ctx):
    countdown_id = ctx.message.author.id
    if countdown_id in active_countdowns:
        del active_countdowns[countdown_id]
        await ctx.send("Contagem cancelada.")
    else:
        await ctx.send("Não há nenhuma contagem em andamento.")

@bot.command()
async def off(ctx):
    global bot_ativo
    if isinstance(ctx.channel, discord.channel.DMChannel) or ctx.author.guild_permissions.administrator:
        bot_ativo = False
        await ctx.message.reply('Bot desativado.')
    else:
        await ctx.message.reply('Você não tem permissão para ativar o bot.')


@bot.command()
async def on(ctx):
    global bot_ativo
    if isinstance(ctx.channel, discord.channel.DMChannel) or ctx.author.guild_permissions.administrator:
        bot_ativo = True
        await ctx.message.reply('Bot reativado.')
    else:
        await ctx.message.reply('Você não tem permissão para ativar o bot.')

@bot.event
async def on_message(message):
    if message.content.startswith('!on'):
        await bot.process_commands(message)
    elif bot_ativo:
        await bot.process_commands(message)
    else:
        if message.content.startswith('!'):
            await message.channel.send('Não estou disponível.')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member=None, *, reason=None):
    if member is None:
        await ctx.message.reply("Por favor, mencione um membro válido para banir.")
        return

    await member.ban(reason=reason)
    await ctx.message.reply(f'{member.mention} foi banido.')

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member=None, *, reason=None):
    if member is None:
        await ctx.message.reply("Por favor, mencione um membro válido para expulsar.")
        return

    await member.kick(reason=reason)
    await ctx.message.reply(f'{member.mention} foi expulso.')

@bot.command()
@commands.has_permissions(administrator=True) 
async def unban(ctx, member_id: int):
    try:
        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            if ban_entry.user.id == member_id:
                await ctx.guild.unban(ban_entry.user)
                await ctx.send(f'Usuario {member_id} agora está desbanido!')
                return

        await ctx.send('Usario não encontrado na lista')

    except discord.Forbidden:
        await ctx.send('Você não tem permissão para isso!')

@bot.command()
async def escolher(ctx, *alternativas):
    if len(alternativas) < 2:
        await ctx.message.reply("Por favor, escolhe pelo menos duas alternativas!")
    else:
        escolha = random.choice(alternativas)
        await ctx.message.reply(f"Escolho: {escolha}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def clear(ctx, quantidade: int=None):
    if quantidade is None:
        await ctx.message.reply("Por favor, diga um número para deletar.")
        return
    if quantidade > 0:

        messages = await ctx.channel.history(limit=quantidade+1).flatten()
        
        for message in messages:
            await message.delete()
        
        delete_msg = await ctx.send(f'Deletado {len(messages)-1} mensagens.')
        
        await asyncio.sleep(3)
        await delete_msg.delete()

        await asyncio.sleep(3)
        await ctx.message.delete()

@bot.command()
async def moeda(ctx):


    resultado = random.choice(['Cara', 'Coroa'])
    await ctx.message.reply(f":coin: {resultado}!")
    

def converter_tempo_para_minutos(tempo_str):
    match = re.match(r'(\d+)\s*([smhd])', tempo_str)
    if match:
        quantidade = int(match.group(1))
        unidade = match.group(2)
        if unidade == 's':
            return quantidade / 60  
        elif unidade == 'm':
            return quantidade
        elif unidade == 'h':
            return quantidade * 60  
        elif unidade == 'd':
            return quantidade * 60 * 24  
    return None
    

def converter_segundos_para_horas_minutos_segundos(segundos):
    horas = segundos // 3600
    segundos %= 3600
    minutos = segundos // 60
    segundos %= 60
    return horas, minutos, segundos

scheduled_commands = {}

@bot.command()
async def tempo(ctx, tempo_str: str, *, comando: str):
    minutos = converter_tempo_para_minutos(tempo_str)
    if minutos is None:
        await ctx.send(f"Tempo inválido. Use formatos como '1s' (1 segundo), '1m' (1 minuto) ou '1d' (1 dia).")
        return

    scheduled_commands[ctx.author.id] = (comando, ctx.channel.id, minutos * 60)
    
    await ctx.message.reply(f'Comando agendado por {minutos} minutos. Use "!time show" para ver os comandos ativos.')

    await asyncio.sleep(minutos * 60)

    if ctx.author.id in scheduled_commands:
        del scheduled_commands[ctx.author.id]
        
        cmd, *args = comando.split(" ")
        if cmd:
            new_ctx = await bot.get_context(ctx.message)
            new_ctx.message.content = f"{bot.command_prefix}{cmd} {' '.join(args)}"
            await bot.invoke(new_ctx)
        else:
            await ctx.send(f"O comando '{comando}' não está registrado.")

@bot.group(invoke_without_command=True)
async def time(ctx):
    await ctx.send("Comando inválido. Use !time show ou !time cancelar <comando>.")

@time.command()
async def show(ctx):
    if ctx.author.id in scheduled_commands:
        cmd, _, tempo_em_segundos = scheduled_commands[ctx.author.id]
        horas, minutos, segundos = converter_segundos_para_horas_minutos_segundos(tempo_em_segundos)
        await ctx.send(f"Comando agendado: {cmd}\nTempo restante: {horas}h {minutos}m {segundos}s")
    else:
        await ctx.send("Nenhum comando agendado.")

@time.command()
async def cancelar(ctx, *, cmd_name: str):
    if ctx.author.id in scheduled_commands:
        cmd, _, _ = scheduled_commands[ctx.author.id]
        if cmd_name == cmd:
            del scheduled_commands[ctx.author.id]
            await ctx.send(f"Comando '{cmd_name}' cancelado.")
        else:
            await ctx.send(f"Comando '{cmd_name}' não coincide com o comando agendado.")
    else:
        await ctx.send("Nenhum comando agendado.")


@bot.command()
async def ajuda(ctx):
    embed = discord.Embed(title='Ajuda', description='Aqui está a lista de comandos disponíveis:', color=0x740000)
    embed.add_field(name='!r <XdY>, ou !roll', value='O famoso rola um d20, rola um dado de 6 a 100 lados.', inline=False)
    embed.add_field(name='!escolhe (opção1) (opção2)', value='Tá em dúvida? Que tal uma ajudinha do bot!', inline=False)
    embed.add_field(name='!ppt <pedra,pepel ou tesoura>', value='Pedra, papel e tesoura; Envie ppt (pedra, papel ou tesoura). O bot escolhera um aleatório para ele', inline=False)
    embed.add_field(name='!moeda', value='Quer brincar de cara ou coroa?', inline=False)
    embed.add_field(name='!calc (+, -, *, **, /)', value='1 + 1 = x?', inline=False)
    embed.add_field(name='!contagem (iniciar)(cancelar)', value='Está com padrão de segundos, então 120 = 2m, etc. "!contagem iniciar 10"', inline=False)
    embed.add_field(name='!tempo', value='Parecido com !contagem, porém funciona da seguinte forma: Você ira enviar "!tempo <comando> <1s,1m,1h,1d>" e ele irá executar o comando depois do tempo determiado.', inline=False)
    embed.add_field(name='!forca', value='Um joguinho da forca para descontrair ia ser legal, não?', inline=False)
    embed.add_field(name='!cantada', value='Uma cantada pra mandar pro crush? Ou esteja se sentindo carente ksks', inline=False)
    embed.add_field(name='!anagrama', value='Um joguinho de anagrama, vai.', inline=False)
    embed.add_field(name='!ship (nome) (nome)', value='Um joguinho pra ver suas chances com a(o) crushzinho :3', inline=False)
    embed.add_field(name='!tapa', value='Quer dar um tapa naquela pessoa irritante?', inline=False)
    embed.add_field(name='!abraço', value='Retribua com um abraço para aquela pessoa especial!', inline=False)
    embed.add_field(name='!beijo', value='Hmm, beijinho bom..', inline=False)
    embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def adm(ctx):
    embed = discord.Embed(title='Ajuda', description='Aqui está a lista de comandos de administradores disponíveis:', color=0x740000)
    embed.add_field(name='!clear (quantidade)', value='Deleta aquele monte de conversa do chat.', inline=False)
    embed.add_field(name='!ban (@player)', value='Banido!', inline=False)
    embed.add_field(name='!kick (@player)', value='Expulso!', inline=False)
    embed.add_field(name='!dado (set, unset ou show)', value='Adiciona um número viciado ao dado, retira ou vê qual está setado!', inline=False)
    embed.add_field(name='!off', value='Incapacita o bot de usar qualquer comando', inline=False)
    embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
    await ctx.send(embed=embed)



@bot.command()
async def ppt(ctx, escolha):
    global conn
    user_id = ctx.author.id
    
    sql  = f"""
        select
        m.moedas,
        u.id,
        if(UNIX_TIMESTAMP(current_date) - m.cooldown < 86400, 1, 0),
        m.cooldown
        from bot.tbuser u
        join bot.tbmoeda m on m.id_usuario = u.id
        where u.id_discord = {user_id}
    """
    
    c = conn.cursor()
    c.execute(sql)
    r = c.fetchall()


    if r[0][2] == 1:
        escolha = escolha.lower()
        if escolha not in ['pedra', 'papel', 'tesoura']:
            await ctx.send('Escolha inválida. Use `pedra`, `papel` ou `tesoura`.')
            return

        choices = ['pedra', 'papel', 'tesoura']
        escolha_bot = random.choice(choices)

        if escolha == escolha_bot:
            resultado = "Empate!"
        elif (
            (escolha == "pedra" and escolha_bot == "tesoura") or
            (escolha == "papel" and escolha_bot == "pedra") or
            (escolha == "tesoura" and escolha_bot == "papel")
        ):
            resultado = "Você venceu!"
        else:
            resultado = "Eu venci!"

        await ctx.send(f'Eu escolhi {escolha_bot}. {resultado}')
        return

    moedas = r[0][0]
    daily = random.randrange(1,11)
    moedasDaily = moedas + daily



    sql = f"""
        update 
        bot.tbmoeda     
        set moedas = {moedasDaily},
        cooldown = '{(mktime(datetime.now().timetuple()))}'
        where id_usuario = {r[0][1]}
    """



    c = conn.cursor()
    c.execute(sql)
    conn.commit()


    escolha = escolha.lower()
    if escolha not in ['pedra', 'papel', 'tesoura']:
        await ctx.send('Escolha inválida. Use `pedra`, `papel` ou `tesoura`.')
        return

    choices = ['pedra', 'papel', 'tesoura']
    escolha_bot = random.choice(choices)

    if escolha == escolha_bot:
        resultado = "Empate!"
    elif (
        (escolha == "pedra" and escolha_bot == "tesoura") or
        (escolha == "papel" and escolha_bot == "pedra") or
        (escolha == "tesoura" and escolha_bot == "papel")
    ):
        resultado = "Você venceu!"
    else:
        resultado = "Eu venci!"

    await ctx.send(f'Eu escolhi {escolha_bot}. {resultado}')
    await ctx.message.reply(f"Você recebeu {daily} moedas! Use ``!inv`` para ver o total!")

user_settings = {}

@bot.group()
@commands.has_permissions(ban_members=True)
async def dado(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Invalido! Use '!dado 'set', 'unset' ou 'show'!")

@dado.command()
async def set(ctx, fixed_value: int):
    user_settings[ctx.author.id] = fixed_value
    await ctx.send(f"Valor `{fixed_value}` setado, cuidado!")

@dado.command()
async def unset(ctx):
    if ctx.author.id in user_settings:
        del user_settings[ctx.author.id]
        await ctx.send("Valor retirado")

@dado.command()
async def show(ctx):
    fixed_value = user_settings.get(ctx.author.id)
    if fixed_value is not None:
        await ctx.send(f"O valor setado é: {fixed_value}")
    else:
        await ctx.send("Não houve valor setado ainda.")

@bot.command()
async def r(ctx, dice: str):
    try:
        dice_list = dice.split('#')
        results_list = []

        for dice_entry in dice_list:
            dice, *positive = re.split(r'\+', dice_entry)
            dice, *negative = re.split(r'\-', dice)
            rolls, limit = map(int, dice.split('d'))

            negative_total = sum(int(modifier) for modifier in negative)
            positive_total = sum(int(modifier) for modifier in positive)
            modifier_total = sum(int(modifier) for modifier in positive) - sum(int(modifier) for modifier in negative)

            if limit < 1 or limit > 100:
                await ctx.message.reply('Opa... Você só pode usar os números de 1 a 100!')
                return

            results = [random.randint(1, limit) for _ in range(rolls)]
            negative_total = sum(results) - negative_total
            total = sum(results) + positive_total

            if ctx.author.id in user_settings:
                fixed_value = user_settings[ctx.author.id]
                results = [fixed_value] * rolls

            total = sum(results) + modifier_total
            result_text = ', '.join(str(result) for result in results)
            result_with_total = f"{result_text}\n ❃ **Total:** {total} ❃\n"

            if total == 1:
                result_list = f"{result_text}\n ❃ **Total:** **{total}** ☠️\n"
            elif total == limit:
                result_list = f"{result_text}\n ❃ **Total:** **{total}** 🥳\n"
            else:
                result_list = result_with_total

            results_list.append(result_list)

        await ctx.message.reply('\n'.join(results_list))

    except Exception:
        embed = discord.Embed(title='Algo deu errado. :game_die:', description='Use esse formato:', color=0x740000)
        embed.add_field(name='!r (Quantidade de dados e Dado desejado [+/- Modificadores] ou 1d20#1d20)', value='1d20 Por exemplo!', inline=False)
        embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
        await ctx.message.reply(embed=embed)

palavras = ["abacaxi", "banana", "guitarra", "praia", "senha", "rpg", "cryptomoeda", "serra", "mor", "otto", "edgar",
            "katsuragi", "lucifer", "idril", "shiro", "naato", "servo", "historia", "batata", "banimento", "minecraft",
            "herobrine", "laninieu", "galaxia", "abóbora", "chocolate", "elefante", "dança", "computador", "sol", 
            "cachorro", "livro", "laranja", "camiseta", "avião", "espelho", "futebol", "pizza", "girafa", "vento",
            "cama", "tênis", "sushi"]


def get_random_word():
    return random.choice(palavras)

@bot.group()
async def forca(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("User 'iniciar' ou 'cancelar'.")

@forca.command()
async def iniciar(ctx):
    global jogo_ativo
    jogo_ativo = True

    await ctx.send("> Jogo da Forca iniciado! Tente adivinhar a palavra.")
    await ctx.send("> Você tem 2 minutos para enviar uma letra! Caso queira para use: ``!forca cancelar``")

    palavra = get_random_word().upper()
    letras_corretas = []
    letras_erradas = []
    tentativas = 6

    def montar_forca():
        forca = ""
        for letra in palavra:
            if letra in letras_corretas:
                forca += letra
            else:
                forca += "-"
        return forca

    def verificar_fim_jogo():
        if "-" not in montar_forca():
            return "player"
        elif tentativas == 0:
            jogo_ativo = False 
            return "bot"
        else:
            return None

    while jogo_ativo:
        forca_atual = montar_forca()
        fim_jogo = verificar_fim_jogo()

        if fim_jogo == "player":
            await ctx.send(f"Parabéns! Tu venceu! A palavra era: {palavra}")
            jogo_ativo = False
        elif fim_jogo == "bot":
            await ctx.send(f"Tu perdeu! A palavra era: {palavra}")
            jogo_ativo = False

        await ctx.send(f"Palavra: {forca_atual}")
        await ctx.send(f"Tentativas restantes: {tentativas}")

        def check(message):
            return (
                message.author == ctx.author
                and message.channel == ctx.channel
                and message.content.isalpha()
            )

        try:
            resposta = await bot.wait_for("message", check=check, timeout=120)
            comando = resposta.content.lower()

            if comando == "cancelar":
                await ctx.send("Jogo cancelado.")
                jogo_ativo = False
            else:
                if len(comando) > 1:
                    if comando.upper() == palavra:
                        await ctx.send(f"Parabéns! Tu venceu! A palavra era: {palavra}")
                        jogo_ativo = False
                    else:
                        tentativas -= 1
                        await ctx.send(f"Resposta incorreta.")
                else:
                    letra = comando.upper()

                    if letra in letras_corretas or letra in letras_erradas:
                        await ctx.send("Essa letra já foi. Tenta outra!")
                    elif letra in palavra:
                        letras_corretas.append(letra)
                    else:
                        letras_erradas.append(letra)
                        tentativas -= 1
                        await ctx.send(f"A letra **{letra}** está incorreta. Tenta de novo.")
        except asyncio.TimeoutError:
            await ctx.send(f"O tempo limite para responder acabou, a palavra era {palavra}. Jogo cancelado!")
            jogo_ativo = False

@forca.command()
async def cancelar(ctx):
    global jogo_ativo
    await ctx.message.reply("Jogo cancelado.")
    jogo_ativo = False

@bot.command()
async def cantada(ctx):
    cantadas = ["Você não é o Google, mas tem tudo o que eu procuro.",
                "Poderia criar uma religião com você sendo minha deusa",
                "Acredita em amor à primeira vista ou devo passar por aqui mais uma vez?",
                "Ei, você tem um mapa? Porque me perdi no brilho dos seus olhos.",
                "Você é feito de cobre e telúrio? Porque você é Cu-Te!",
                "Se beleza fosse crime, você pegaria prisão perpétua.",
                "Seu pai é astronauta? Porque você é de outro mundo!",
                "Aposto um beijo que você me dá um fora.",
                "Você é um dicionário? Porque quando te vejo, as palavras desaparecem.",
                "Se você fosse um sanduíche, seria um 'x-princesa'.",
                "Meu amor por você é como a constante matemática 'pi': irracional, infinito e impossível de ser calculado."]  
    escolha = random.choice(cantadas)
    await ctx.message.reply(f"{escolha}")

cartas = 927010543515107429

@bot.command()
async def carta(ctx, remetente: discord.Member, *, mensagem):
    canal = bot.get_channel(cartas)
    
    user = ctx.author
    embed = discord.Embed(
        title=f"Carta Anônima para {remetente.display_name}",
        description=f"{mensagem}",
        color=discord.Color.random()
    )
    embed.set_footer(text=f"Uiui")
    embed.set_image(url="https://media.tenor.com/UdiK4V7MxYYAAAAM/anime-girl.gif")

    
    await canal.send(embed=embed)
    await ctx.message.delete()

@carta.error
async def carta_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        error = await ctx.message.reply("Por favor, forneça o remetente e a mensagem corretamente. Exemplo: `!carta @remetente mensagem`")
        await asyncio.sleep(5)
        await error.delete()
        await ctx.message.delete() 

@bot.command()
async def anagrama(ctx):
    palavras = ['Amor', 'Casa', 'Vida', 'Gato', 'Rato', 'Pato', 'Livro', 'Mesa', 'Cama', 'Flor','Sol', 'Lua', 'Mar', 'otorrinolaringologista',
                'Céu', 'Terra', 'Água', 'Fogo', 'Ar', 'Chuva', 'Neve','Vento', 'Laranja', 'Limão', 'Maçã', 'Banana',
                'Abacaxi', 'Morango', 'Uva', 'Melancia', 'Mamão','Kiwi', 'Cachorro', 'Gato', 'Passarinho', 'Leão', 
                'Tigre', 'Elefante', 'Girafa', 'Zebra', 'Cobra','Tartaruga', 'Borboleta', 'Abelha', 'Formiga',
                'Mosquito', 'Aranha', 'Escorpião', 'Sapo', 'Peixe', 'Baleia','Tubarão', 'Golfinho', 'Crocodilo', 
                'Jacaré', 'Águia', 'Falcão', 'Coruja', 'Pinguim', 'Esquilo', 'Raposa','Elefante', 'Rinoceronte', 
                'Hiena', 'Camaleão', 'Mosca', 'Caracol', 'Barata', 'Veado', 'Cervo', 'Urso','Guaxinim', 'Texugo', 
                'Castor', 'Canguru', 'Coala', 'Panda', 'Girafa', 'Canguru', 'Gorila', 'Chimpanzé','Orangotango', 
                'Lagarto', 'Javali', 'Raposa', 'Doninha', 'Lince', 'Rã', 'Grilo', 'Mariposa', 'Louva-a-deus','Morcego', 
                'Escaravelho', 'Centopeia', 'Tatu', 'Arara', 'Peixe-boi', 'Tamanduá', 'Quati', 'Gazela', 'Mandril','Hipopótamo', 
                'Quimera', 'Xilofone', 'Epistemologia', 'Obfuscado', 'Zoologia', 'Iconoclasta', 'Escatologia','Procrastinação', 
                'Abstruso', 'Anacronismo', 'Elocubração', 'Cacofonia', 'Exacerbado', 'Fosforescência','Quinquagésimo', 'Paradoxo',
                'Axiomático', 'Filantropia', 'Serendipidade', 'Ambivalente', 'Dissonância','Onomatopeia', 'Paradigma', 'Perspicácia',
                'Quotidiano', 'Zeladoria', 'Enigmatizar', 'Imperturbável', 'Ubíquo','Circunloquio', 'Vicissitude', 'Inefável', 'Insondável',
                'Ineffugível', 'Inefugível', 'Plenipotenciário','Polimatia', 'Ineficácia', 'Inexorável', 'Indômito', 'Heliocentrismo', 'Querubim',
                'Cosmogonia', 'Eclético','Peregrinação', 'Eufemismo', 'Antítese', 'Penumbra', 'Recôndito']


    palavra = random.choice(palavras)
    embaralhada = ''.join(random.sample(palavra, len(palavra))).lower()

    def check(message):
        return message.author == ctx.author and message.content.lower() == palavra.lower()

    await ctx.message.reply('> Certo! Então você tem 1 minuto. Pode pedir ajuda para os amigos ein!')
    await ctx.send(f"Desembaralhe a palavra: **{embaralhada}**")

    try:
        msg = await bot.wait_for("message", timeout=60, check=check)
        if msg.content.lower() == palavra.lower():
            await ctx.send(f"Gg, {ctx.author.mention} É isso aí!")
        else:
            await ctx.send(f"Que pena, {ctx.author.mention}. A palavra correta era **{palavra}**.")
    except asyncio.TimeoutError:
        await ctx.send(f"Tempo esgotado! A palavra era: **{palavra}**.")

censura_servidores = {}
censura_ativada = False

palavras_proibidas = [
    "caralho",
    "merda",
    "puta",
    "nigger",
    "macaco",
    "vadia",
    "piranha",
    "bicha",
    "sapatão",
    "matar",
    "machucar",
    "destruir",
    "idiota",
    "imbecil",
    "porra",
    "fdp",
    "arrombado",
    "filho da puta",
    "vsfd",
    "vai se fude",
    "vai se fuder",
    "cacete",
    "fudido",
    "arrombadinho",
    "cuzão",
    "cuzao",
    "cuzinho",
    "crlh",
    "prr",
    "porno",
    "pqp",
    "puta que pariu",
    "hentai",
    "xvideos",
    "pornhub",
    "porn"
    "puta q pariu",
    "p q p",
    "sexo"
]

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  

    servidor_id = message.guild.id  

    censura_ativada = censura_servidores.get(servidor_id, False)

    if censura_ativada:
        
        mensagem = message.content.lower()

        for palavra in palavras_proibidas:
            if palavra in mensagem:

                await message.delete()

                await message.channel.send(f"{message.author.mention} olha a boquinha!!")

    await bot.process_commands(message)

@bot.command()
@commands.has_permissions(administrator=True) 
async def censura(ctx):
    servidor_id = ctx.guild.id  
    if servidor_id in censura_servidores:
        censura_servidores[servidor_id] = not censura_servidores[servidor_id]
    else:
        censura_servidores[servidor_id] = True

    estado = "ativada" if censura_servidores[servidor_id] else "desativada"
    await ctx.send(f"Censura foi {estado} neste servidor.")

bot.run('MTA5NjkzODU4NjU5NjcxMjYzOQ.G8zCE9.TLX0lNAEW-5PZL7lyHmooWBQSzUZo5psRT4Mw8')
