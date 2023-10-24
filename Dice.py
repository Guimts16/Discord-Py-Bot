from time import mktime
import discord
from discord.ext import commands
import random
import asyncio
import re
from datetime import datetime
import mysql.connector
import requests


conn = mysql.connector.connect(
    user="root",
    password="3141592",
    host="127.0.0.1",
    database="bot",
    auth_plugin='mysql_native_password'
)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix=['!', 'mts', '.'], intents=intents)

intents.typing = False
intents.presences = False

def ids(ctx):
    ids = [617362818299199498, 1136393486082523257, 1053694078589603940]
    return ctx.author.id in ids

bot.remove_command('help')

@bot.event
async def on_ready():
    print(f'LOGADO EM {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!ajuda"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title='Erro de Comando',
            description=f'O comando `{ctx.message.content}` não foi encontrado. Tente usar `!ajuda`!',
            color=discord.Color.red()
        )
        await ctx.message.reply(embed=embed)
        print(f'Erro durante a execucao do comando: {error}')

@bot.command()
async def ping(ctx):
    latency = bot.latency * 100

    mensagem1 = await ctx.send('Calculando.')

    await asyncio.sleep(0.5)
    await mensagem1.edit(content='Calculando..')
    await asyncio.sleep(0.5)
    await mensagem1.edit(content='Calculando...')
    await asyncio.sleep(0.5)
    await mensagem1.edit(content=f'PING: {latency:.1f}ms')

@bot.command()
async def clima(ctx, cidade=None):
    if cidade is None:
        await ctx.message.reply("Por favor forneça uma cidade!")
        return
    api = "5a8be18bb18b8e07db3e330f1e4c0a96"
    link = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api}&lang=pt_br"

    requisicao = requests.get(link)
    requisicao_dic = requisicao.json()
    temperatura = requisicao_dic['main']['temp'] - 273.15
    resultado = round(temperatura, 0)
    embed = discord.Embed(title=f'{cidade}', description='', color=0x740000)
    embed.add_field(name=f'Temperatura de {cidade}', value=f'- {resultado}ºC', inline=False)
    await ctx.message.reply(embed=embed)

@bot.command()
async def turnos(ctx):
    global conn
    sql = f"""
        SELECT iduser, dado FROM bot.tbturnos
        ORDER BY dado DESC;
        """
    c = conn.cursor() 
    c.execute(sql)
    r = c.fetchall()
    if len(r) > 0:
        await ctx.message.reply("> Segue a ordem abaixo:")
        for tupla in r:
            await ctx.send(f'> - Nome: <@{tupla[0]}>, Dado: {tupla[1]}')
            

    else:
        await ctx.message.reply("Nenhum turno adicionado ainda! Use ``!ord`` para adicionar novos turnos")


@bot.command()
async def ord(ctx):
    global conn
    dadin = random.randint(1, 21)
    author = ctx.author.id
    sql = f"insert into bot.tbturnos (iduser, dado) values ({author}, {dadin})"
    c = conn.cursor() 
    c.execute(sql)
    conn.commit()
    await ctx.send(f'Okay! Seu número da sorte foi... {dadin}')
    return
        

@bot.command()
async def turndel(ctx):
    sql = "delete from bot.tbturnos"
    c = conn.cursor() 
    c.execute(sql)
    conn.commit()
    await ctx.message.reply("Turnos resetados!")

@bot.group()
async def profile(ctx, de=None):
    if de is None:
        global conn
        sql = f"SELECT id, id_discord FROM bot.tbuser WHERE id_discord = {ctx.author.id}"
        c = conn.cursor() 
        c.execute(sql)
        r = c.fetchall()

        embed = discord.Embed(title='Perfil', description=f'{ctx.author.mention}', color=0x740000)
        if len(r) > 0:
                
            for palavra in r:
                sql = f"""
                    select
                    u.id_discord, 
                    m.moedas
                    from bot.tbuser u
                    join bot.tbmoeda m on m.id_usuario = u.id
                    where u.id_discord = {ctx.author.id}"""
                c = conn.cursor() 
                c.execute(sql)
                h = c.fetchall()
                embed.add_field(name='Login: Online', value=f'- ID: {palavra[1]}', inline=False)
                embed.add_field(name=f'Moedas: ', value=f'- {h[0][1]}', inline=False)

                sql = f"select u.id from bot.tbuser u where u.id_discord = '{ctx.author.id}'"
                c = conn.cursor()
                c.execute(sql)
                rato = c.fetchall()
                c.close()
                ba = rato[0][0]
                sql = f"""
                select 
                (select u.id from bot.tbuser u where u.id_discord = '{ctx.author.id}') as id_user,
                (select a.avisos from bot.tbwarn a where a.id_dc = '{ba}') as warn,
                (select a.motivos from bot.tbwarn a where a.id_dc = '{ba}') as motivo
                """
                c = conn.cursor()
                c.execute(sql)
                he = c.fetchall()
                c.close()            
                embed.add_field(name=f'Avisos:', value=f'- {he[0][1]}\n- Motivo recente: {he[0][2]}', inline=False)

        else:

            embed.add_field(name='Login: Offline', value=f'Caso queria logar use ``!login @{ctx.author.name}``', inline=False)

        if len(ctx.author.roles) == 1:
            embed.add_field(name=f'Cargos:', value='- Nenhum cargo', inline=False)
        else:
            roles = [role.name for role in ctx.author.roles[1:]] 
            roles_text = ', '.join(roles)
            embed.add_field(name=f'Cargos:\n- {roles_text}', value=f'', inline=False)
        
        criado = ctx.author.created_at.strftime("%d de %B de %Y")

        embed.add_field(name=f'No discord desde:', value=f'- {criado}', inline=False)

        embed.add_field(name='❛ ━━━━━━･❪ ❁ ❫ ･━━━━━━ ❜', value=f'', inline=False)

        await ctx.send(embed=embed)
        return
    else:
        deid = de.replace('<', '').replace('@', '').replace('>', '')
        sql = f"SELECT id, id_discord FROM bot.tbuser WHERE id_discord = {deid}"
        c = conn.cursor() 
        c.execute(sql)
        r = c.fetchall()

        embed = discord.Embed(title='Perfil', description=f'{de}', color=0x740000)
        if len(r) > 0:
                
            for palavra in r:
                sql = f"""
                    select
                    u.id_discord, 
                    m.moedas
                    from bot.tbuser u
                    join bot.tbmoeda m on m.id_usuario = u.id
                    where u.id_discord = {deid}"""
                c = conn.cursor() 
                c.execute(sql)
                h = c.fetchall()
                embed.add_field(name='Login: Online', value=f'- ID: {palavra[1]}', inline=False)
                embed.add_field(name=f'Moedas: ', value=f'- {h[0][1]}', inline=False)

                sql = f"select u.id from bot.tbuser u where u.id_discord = '{deid}'"
                c = conn.cursor()
                c.execute(sql)
                rato = c.fetchall()
                c.close()
                ba = rato[0][0]
                sql = f"""
                select 
                (select u.id from bot.tbuser u where u.id_discord = '{deid}') as id_user,
                (select a.avisos from bot.tbwarn a where a.id_dc = '{ba}') as warn,
                (select a.motivos from bot.tbwarn a where a.id_dc = '{ba}') as motivo
                """
                c = conn.cursor()
                c.execute(sql)
                he = c.fetchall()
                c.close()            
                embed.add_field(name=f'Avisos:', value=f'- {he[0][1]}\n- Motivo recente: {he[0][2]}', inline=False)

        else:

            embed.add_field(name='Login: Offline', value=f'Caso queria logar use ``!login @{de.name}``', inline=False)

        if len(ctx.author.roles) == 1:
            embed.add_field(name=f'Cargos:', value='- Nenhum cargo', inline=False)
        else:
            roles = [role.name for role in ctx.author.roles[1:]] 
            roles_text = ', '.join(roles)
            embed.add_field(name=f'Cargos:\n- {roles_text}', value=f'', inline=False)
        
        criado = ctx.author.created_at.strftime("%d de %B de %Y")

        embed.add_field(name=f'No discord desde:', value=f'- {criado}', inline=False)

        embed.add_field(name='❛ ━━━━━━･❪ ❁ ❫ ･━━━━━━ ❜', value=f'', inline=False)

        await ctx.send(embed=embed)
        return


@bot.command()
async def login(ctx, user=None):
    if user is None:
        embed = discord.Embed(title='LOGIN', description='**ERRO**', color=0x740000)
        embed.add_field(name='Por favor forneça um usuario do discord para que possa ser adicionado', value='', inline=False)
        await ctx.message.reply(embed=embed)

    global conn
    userid = user.replace('<', '').replace('@', '').replace('>', '')
    sql_check = f"SELECT id, id_discord from bot.tbuser WHERE id_discord = {userid}"
    c = conn.cursor() 
    c.execute(sql_check)
    r = c.fetchall()

    if r:
        embed = discord.Embed(title='LOGIN', description='**ERRO**', color=0x740000)
        embed.add_field(name='Usuario já logado em nossa loja!', value=f'ID do usuario: {userid}', inline=False)
        await ctx.message.reply(embed=embed)
    else:

        sql_insert = f"INSERT INTO bot.tbuser (id_discord) VALUES ({userid})"
        c = conn.cursor() 
        c.execute(sql_insert)
        conn.commit()

        sql_select = f"SELECT id, id_discord from bot.tbuser WHERE id_discord = {userid}"
        c = conn.cursor() 
        c.execute(sql_select)
        r = c.fetchall()
        id = r[0][0]

        sql_moeda = f"INSERT INTO bot.tbmoeda (id_usuario, moedas, cooldown) VALUES ({id}, 0, 1)"
        c = conn.cursor() 
        c.execute(sql_moeda)
        conn.commit()
        
        sql_warn = f"insert into bot.tbwarn (id_dc, avisos, motivos) values ({id}, 0, 'Nenhum aviso!')"
        c = conn.cursor() 
        c.execute(sql_warn)
        conn.commit()

        sql_inv = f"insert into bot.tbuserinv (id_user, id_item, quantidade) values ({id}, 7, 2)"
        c = conn.cursor() 
        c.execute(sql_inv)
        conn.commit()

        embed = discord.Embed(title='LOGIN', description='', color=0x740000)
        embed.add_field(name='Usuario logado com sucesso! Já pode começar usando o ``!daily``', value=f'ID do usuario: {userid}', inline=False)
        await ctx.message.reply(embed=embed)

@bot.command()
async def help(ctx):
    await ctx.message.reply("Peço desculpas, o comando ``!help`` e ``ajuda`` estão em manutenção. Caso haja alguma dúvida, consulte meu criador: <@617362818299199498>")

#    author = ctx.message.author
#    embed = discord.Embed(title='Ajuda', description='Aqui está a lista de comandos disponíveis:', color=0x740000)
#    embed.add_field(name='!r <XdY>, ou !roll', value='O famoso rola um d20, rola um dado de 6 a 100 lados.', inline=False)
#    embed.add_field(name='!escolhe (opção1) (opção2)', value='Tá em dúvida? Que tal uma ajudinha do bot!', inline=False)
#    embed.add_field(name='!ppt <pedra,pepel ou tesoura>', value='Pedra, papel e tesoura; Envie ppt (pedra, papel ou tesoura). O bot escolhera um aleatório para ele', inline=False)
#    embed.add_field(name='!moeda', value='Quer brincar de cara ou coroa?', inline=False)
#    embed.add_field(name='!embed <send> ou <info>', value='Pra ficar fofo', inline=False)
#    embed.add_field(name='!calc (+, -, *, **, /)', value='1 + 1 = x?', inline=False)
#    embed.add_field(name='!contagem (iniciar)(cancelar)', value='Está com padrão de segundos, então 120 = 2m, etc. "!contagem iniciar 10"', inline=False)
#    embed.add_field(name='!tempo', value='Parecido com !contagem, porém funciona da seguinte forma: Você ira enviar "!tempo <comando> <1s,1m,1h,1d>" e ele irá executar o comando depois do tempo determiado.', inline=False)
#    embed.add_field(name='!forca', value='Um joguinho da forca para descontrair ia ser legal, não?', inline=False)
#    embed.add_field(name='!cantada', value='Uma cantada pra mandar pro crush? Ou esteja se sentindo carente ksks', inline=False)
#    embed.add_field(name='!anagrama', value='Um joguinho de anagrama, vai.', inline=False)
#    embed.add_field(name='!ship (nome) (nome)', value='Um joguinho pra ver suas chances com a(o) crushzinho :3', inline=False)
#    embed.add_field(name='!tapa', value='Quer dar um tapa naquela pessoa irritante?', inline=False)
#    embed.add_field(name='!abraço', value='Retribua com um abraço para aquela pessoa especial!', inline=False)
#    embed.add_field(name='!beijo', value='Hmm, beijinho bom..', inline=False)
#    embed.add_field(name='!shop', value='Disponivel apenas para os meus RPGs', inline=False)
#    embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
#    await author.send(embed=embed)


@bot.command()
async def entrar(ctx):
    # Verifica se o autor do comando está em uma chamada de voz
    if ctx.author.voice is None:
        await ctx.send("Você não está em uma chamada de voz!")
        return

    canal = ctx.author.voice.channel

    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(canal)
    else:
        await canal.connect()

    await ctx.send(f"Conectado em {canal.name}")

@bot.group()
async def shop(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(title='Ajuda', description='Aqui está a lista de comandos disponíveis:', color=0x740000)
        embed.add_field(name='!shop buy <id do item> <quantidade>', value='Fazer suas compras', inline=False)
        embed.add_field(name='!shop ver', value='Para ver os itens diponiveis', inline=False)
        embed.add_field(name='!daily', value='Pegue suas recompensas diarias para não ficar zerado!', inline=False)
        embed.add_field(name='!inv <ver> ou <de @user>', value='Olhe seu inventario!', inline=False)
        embed.add_field(name='!login <@user>', value='Para fazer login de jogadores que ainda não estão na loja!')
        embed.set_footer(text='Para mais informações, manda mensagem para o Guimts. Por enquanto alguns comandos ainda estão em desenvolvimento!')
        await ctx.message.reply(embed=embed)
        return

@shop.command()
@commands.check(ids)
async def off(ctx):
    shop.remove_command('buy')
    await ctx.message.reply(f'A ``Loja`` foi bloqueada. Reinicie o bot para desbloquear!')

@shop.command() 
async def usar(ctx, item=None, qtd=None): 
    if item or qtd is None:
        embed = discord.Embed(title='USO', description='', color=0x740000)
        embed.add_field(name=f'Forneça um item e uma quantidade por favor!', value=f'Nesse formato, por exemplo: ``!shop usar Poçãoc 1``', inline=False)
        embed.set_footer(text='Para mais informações, manda mensagem para o Guimts.') 
        await ctx.message.reply(embed=embed)
        return
    global conn  
    sql = f"SELECT id FROM bot.tbuser WHERE id_discord = {ctx.author.id}"
     
    c = conn.cursor()  
    c.execute(sql) 
    ar = c.fetchall()
    id = ar[0][0]

    sql = f"""
        SELECT
        i.nome,
        i.id
        from bot.tbitens i
        where i.nome = '{item}'
        """
    
    c = conn.cursor()  
    c.execute(sql) 
    a = c.fetchall()
    nome = a[0][0]
    id_item = a[0][1]

    if nome:
        sql = f"select id, id_user, id_item, quantidade from bot.tbuserinv where id_item = {id_item} and id_user = {id}"

        c = conn.cursor() 
        c.execute(sql)
        r = c.fetchall()
        quanti = r[0][3]
        idd = r[0][2]
        if quanti:

            if quanti > 0:
                sql = f"""update bot.tbuserinv set quantidade = {int(quanti) - int(qtd)} WHERE id_user = '{id}' and id_item = {idd}"""
                c = conn.cursor() 
                c.execute(sql)
                conn.commit()
                total = int(quanti) - int(qtd)
                embed = discord.Embed(title='USO', description='', color=0x740000)
                embed.add_field(name=f'Você usou {qtd} de {item}!', value=f'- Agora tem: {total}', inline=False)
                embed.set_footer(text='Para mais informações, manda mensagem para o Guimts.') 
        else: 
            
            embed = discord.Embed(title='USO', description='', color=0x740000)
            embed.add_field(name=f'Parece que você não tem esse item. Use ``!inv ver`` para verficar!', value='', inline=False)
            embed.set_footer(text='Para mais informações, manda mensagem para o Guimts.') 
    await ctx.message.reply(embed=embed)

@shop.command()
async def vender(ctx, item, qtd):

    #itens da loja
    sql = f"""
        select
        a.id,
        a.preco,
        a.nome,
        a.estoque,
        a.ativo
        from bot.tbitens a
        where nome = '{item}'"""
    c = conn.cursor() 
    c.execute(sql)
    r = c.fetchall()
    name = r[0][2]
    preco = r[0][1]
    sql = f"SELECT id FROM bot.tbuser WHERE id_discord = {ctx.author.id}" 
    c = conn.cursor()  
    c.execute(sql) 
    ar = c.fetchall()
    id = ar[0][0]

    sql = f"select quantidade from bot.tbuserinv where id_user = {id} and id_item = {r[0][0]} "
    c = conn.cursor() 
    c.execute(sql)
    a = c.fetchall()
    quantidade = a[0][0]
    
    if quantidade > 0:
        sql = f"select id, id_user, id_item, quantidade from bot.tbuserinv where id_item = {r[0][0]} and id_user = {id}"

        c = conn.cursor() 
        c.execute(sql)
        r = c.fetchall()
        quanti = r[0][3]
        idd = r[0][2]
        if idd:
            sql = f"""update bot.tbuserinv set quantidade = {int(quanti) - int(qtd)} WHERE id_user = '{id}' and id_item = {idd}"""
            c = conn.cursor() 
            c.execute(sql)
            conn.commit()
            
            sql = f"select moedas from bot.tbmoeda where id_usuario = {id}"
            c = conn.cursor() 
            c.execute(sql)
            f = c.fetchall()
            total = f[0][0] + preco
            sql = f"update bot.tbmoeda set moedas = {total} where id_usuario = {id}"
            c = conn.cursor() 
            c.execute(sql)
            conn.commit()
            embed = discord.Embed(title='VENDAS', description='VENDIDO', color=0x740000)
            embed.add_field(name=f'Vendido!! Você vendeu {name} e recebeu {preco}!', value=f'Suas moedas agora: {total}', inline=False)
            embed.set_footer(text='Para mais informações, manda mensagem para o Guimts.')
        else:
            embed = discord.Embed(title='VENDAS', description='', color=0x740000)
            embed.add_field(name=f'Parece que você não tem esse item. Use ``!inv ver`` para verficar!', value='', inline=False)
            embed.set_footer(text='Para mais informações, manda mensagem para o Guimts.')    
    else:
        embed = discord.Embed(title='VENDAS', description='', color=0x740000)
        embed.add_field(name=f'Parece que você não tem esse item. Use ``!inv ver`` para verficar!', value='', inline=False)
        embed.set_footer(text='Para mais informações, manda mensagem para o Guimts.') 
    await ctx.message.reply(embed=embed)

@shop.command()
async def roleta(ctx):
    global conn
    user = ctx.author.id
    sql  = f"""
        select
        u.id,
        if(UNIX_TIMESTAMP(current_date) - m.cooldown < 604800, 1, 0),
        m.cooldown
        from bot.tbuser u
        join bot.cooldown m on m.id_usuario = u.id
        where u.id_discord = {user}
    """
    c = conn.cursor() 
    c.execute(sql)
    a = c.fetchall()
    id = a[0][0]
    resgatado = a[0][1]
    if resgatado == 1:
        embed = discord.Embed(title='Já deu por hoje...', description='Semana que vem tem mais', color=0x740000)
        embed.add_field(name=f'Você já resgatou presente!! Sinto muito...', value='', inline=False)
        embed.set_footer(text='Para mais informações, manda mensagem para o Guimts.')
        await ctx.message.reply(embed=embed)
        return

    sql = f"""
        update 
        bot.cooldown     
        set cooldown = '{(mktime(datetime.now().timetuple()))}'
        where id_usuario = {id}
    """

    c = conn.cursor()
    c.execute(sql)
    conn.commit()

    sorte = random.randint(1, 4)
    (sorte)
    if sorte == 1:
        item = random.randint(1, 35)
        (item)
        sql = f"SELECT id, nome, preco FROM bot.tbitens WHERE id = '{item}'"
        c = conn.cursor() 
        c.execute(sql)
        r = c.fetchall()
        id = r[0][0]
        nome = r[0][1]
        preco = r[0][2]

        sql = f"select id, id_discord from bot.tbuser where id_discord = {ctx.author.id}"

        c = conn.cursor() 
        c.execute(sql)
        s = c.fetchall()

        id = s[0][0]

        sql = f"select moedas from bot.tbmoeda where id_usuario = {id}"


        c = conn.cursor() 
        c.execute(sql)
        a = c.fetchall()
        moeda_a = a[0][0]

        sql =  f"""
            update 
            bot.tbmoeda     
            set moedas = {moeda_a + preco}
            where id_usuario = {id}
        """

        c = conn.cursor() 
        c.execute(sql)
        conn.commit()
        embed = discord.Embed(title='ROLETA', description='Item!', color=0x740000)
        embed.add_field(name=f'Parabéns! Você recebeu a quantidade de moedas do item ``{nome}``, fique a vontade para compra-lo ou comprar outra coisa!', value=f'Valor do item: {preco}\nSuas moedas: {preco + moeda_a}', inline=False)
        await ctx.message.reply(embed=embed)
        
    if sorte == 2: 
        moedas = random.randint(50, 501)
        sql = f"select id, id_discord from bot.tbuser where id_discord = {ctx.author.id}"

        c = conn.cursor() 
        c.execute(sql)
        s = c.fetchall()

        id = s[0][0]

        sql = f"select moedas from bot.tbmoeda where id_usuario = {id}"


        c = conn.cursor() 
        c.execute(sql)
        a = c.fetchall()
        moeda_a = a[0][0]

        sql =  f"""
            update 
            bot.tbmoeda     
            set moedas = {moeda_a + moedas}
            where id_usuario = {id}
        """

        c = conn.cursor() 
        c.execute(sql)
        conn.commit()

        embed = discord.Embed(title='ROLETA', description='Moedas!', color=0x740000)
        embed.add_field(name=f'Parabéns! Você recebeu {moedas} moedas!', value=f'Agora possui um total de {moeda_a + moedas}', inline=False)
        await ctx.message.reply(embed=embed)

    if sorte == 3:
        embed = discord.Embed(title='ROLETA', description='Que azar!!', color=0x740000)
        embed.add_field(name='Você infelizmente não recebeu nada... Tente novamente na proxima semana!', value='', inline=False)
        await ctx.message.reply(embed=embed)

@shop.command()
async def rolreset(ctx):
    sql = """
        update 
        bot.cooldown    
        set cooldown = 1
        """
    c = conn.cursor() 
    c.execute(sql)
    conn.commit()
    await ctx.message.reply("Roleta GERAL resetada!")

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
            
            embed.add_field(name=str(tupla[4])+" - "f"{tupla[0]} - Estoque: {tupla[2]}", value=f"{tupla[3]} - Preço: {tupla[1]} moedas de prata!", inline=False)

    else:
        embed.add_field(name='**NENHUM ITEM DISPONIVEL**', value='', inline=False)
    embed.set_footer(text='Use !buy e o número do item desejado!')
    await ctx.message.reply(embed=embed)

@shop.command()
@commands.check(ids)
async def clear(ctx):
    sql = f"delete from bot.tbitens where estoque = 0 and ativo = 1"
    c = conn.cursor() 
    c.execute(sql)
    conn.commit()
    await ctx.message.reply('Todos os itens sem estoque foram retirados!')

@shop.command()
@commands.check(ids)
async def repor(ctx, qtd=None):
    if qtd is None:
        embed = discord.Embed(title='Reposição', description='')
        embed.add_field(name=f'Forneça uma quantidade para repor do estoque por favor!', value=f'Nesse formato, por exemplo: ``!shop repor 1``', inline=False)
        embed.set_footer(text='Para mais informações, manda mensagem para o Guimts.')
        await ctx.message.reply(embed=embed)
        return 
    sql = f"update bot.tbitens set estoque = {qtd} where estoque = 0 and ativo = 1"
    c = conn.cursor() 
    c.execute(sql)
    conn.commit()

    await ctx.message.reply('Todos os itens sem estoque foram repostos')



@shop.command()
@commands.check(ids)
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
async def tr(ctx, transf, user2): 
    user1_id = ctx.author.id 
    user2id = user2.replace('<', '').replace('@', '').replace('>', '')
    global conn  
  
    if int(transf) <= 0: 
        embed = discord.Embed(title='TRANSFERENCIA', description='Não foi possivel efetuar a trasnferencia', color=0x740000)
        embed.add_field(name=f'Impossivel tranferir um valor menor que 0.', value=f'Pensa né, lerdão...', inline=False)
        embed.set_footer(text='Para mais informações, manda mensagem para o Guimts.')
        await ctx.message.reply(embed=embed)
        return 
    
    sql = f""" 
        select  
        m.moedas,
        m.id
        from bot.tbuser u 
        join bot.tbmoeda m on m.id_usuario = u.id 
        where u.id_discord = '{user1_id}' 
    """ 
  
    c = conn.cursor()  
    c.execute(sql) 
    r = c.fetchall()   
    moedas_user1 = r[0][0]
    id_1 = r[0][1]

    if moedas_user1 < int(transf): 
        embed = discord.Embed(title='TRANSFERENCIA', description='Não foi possivel efetuar a trasnferencia', color=0x740000)
        embed.add_field(name=f'A quantidade que deseja dar é maior que a que você tem.', value=f'Suas moedas: {moedas_user1}\n- Pedido: {transf} moedas', inline=False)
        embed.set_footer(text='Para mais informações, manda mensagem para o Guimts.')
        await ctx.message.reply(embed=embed)
        return 
    
    sql = f"select id, id_discord from bot.tbuser where id_discord = {user2id}"

    c = conn.cursor() 
    c.execute(sql)
    s = c.fetchall()
    id = s[0][0]

    sql = f"select moedas from bot.tbmoeda where id_usuario = {id}"

    c = conn.cursor() 
    c.execute(sql)
    a = c.fetchall()
    moeda_a = a[0][0]

    sql =  f"""
        update 
        bot.tbmoeda     
        set moedas = {moeda_a + int(transf)}
        where id_usuario = {id}
    """

    c = conn.cursor() 
    c.execute(sql)
    conn.commit()
    

    sql = f""" 
        update bot.tbmoeda 
        set moedas =  {moedas_user1 - int(transf)} 
        where id_usuario = {id_1} 
    """ 
  
    c = conn.cursor() 
    c.execute(sql) 
    conn.commit() 
    c.close() 
  
    embed = discord.Embed(title='TRANSFERENCIA', description='Feito!', color=0x740000)
    embed.add_field(name=f'Você enviou {transf} moedas para o jogador!', value=f'Suas moedas: {moedas_user1 - int(transf)}\n Jogador: {moeda_a + int(transf)}', inline=False)
    embed.set_footer(text='Para mais informações, manda mensagem para o Guimts.')
    await ctx.message.reply(embed=embed)

#SHOP DE COMPRAS
@shop.command()
async def buy(ctx, item, qtd):
    user_id = ctx.author.id
        
    global conn 
    if int(qtd) <= 0:
        await ctx.message.reply('Não é possível comprar um valor menor que 0 itens!')
        return

    sql = f"""
        select
        i.estoque
        from bot.tbitens i
        where i.id = {item}
    """

    c = conn.cursor() 
    c.execute(sql)
    r = c.fetchall()
    c.close()

    if r[0][0] < int(qtd):
        embed = discord.Embed(title='COMPRAS', description='Não foi possivel efetuar a compra', color=0x740000)
        embed.add_field(name=f'A quantidade pedida é maior que a quantidade que há no estoque.', value=f'Estoque: {r[0][0]} - Pedido: {qtd} ', inline=False)
        embed.set_footer(text='Para mais informações, manda mensagem para o Guimts.')
        await ctx.message.reply(embed=embed)
        return

    sql = f"""
        select 
        u.id_discord,
        m.moedas,
        (select i.preco from bot.tbitens i where i.id = {item})as preco,
        (select i.nome from bot.tbitens i where i.id = {item}) as nome_item,
        (select i.estoque from bot.tbitens i where i.id = {item}) as qtd_item,
        ui.quantidade,
        u.id
        from bot.tbuser u
        join bot.tbmoeda m on m.id_usuario = u.id
        left join bot.tbuserinv ui on ui.id_user = u.id
        where u.id_discord = {user_id}
        """
    c = conn.cursor()
    c.execute(sql)
    r = c.fetchall()
    c.close()
    
    total = int(r[0][2])*int(qtd)


    moedas_atuais = r[0][1]
    estoque = r[0][4]
    qtd_user_inv = r[0][5]
    id_user_db = r[0][6]

    #se o valor for igual ou maior ao total...
    if int(r[0][1]) >= total:
        sql = f"""
            select
            count(*)
            from bot.tbuserinv i
            where i.id_user = {id_user_db} and i.id_item = {item}
        """
        c = conn.cursor()
        c.execute(sql)
        ct = c.fetchall()
        c.close()

        #se o jogador tiver o item ele acrescenta
        if ct[0][0] > 0:
            sql = f"""
                update bot.tbuserinv
                set quantidade = {qtd_user_inv + int(qtd)} 
                where id_user = {id_user_db} and id_item = {item}
            """
        #se não ele adiciona um novo
        else:

            sql = f"""
                insert into bot.tbuserinv (id_user, id_item, quantidade)
                values ({id_user_db}, {item}, {qtd})
            """ 

        c = conn.cursor()
        c.execute(sql)
        conn.commit()
        c.close()
        #muda estoque conforme a quantidade comprada
        sql = f"""
            update bot.tbitens 
            set estoque = {estoque - int(qtd)}
            where id = {item}
        """
        c = conn.cursor()
        c.execute(sql)
        conn.commit()
        c.close()
        #muda as moedas do jogador
        sql = f"""
            update bot.tbmoeda
            set moedas = {moedas_atuais} - {total}
            where id_usuario = {id_user_db}
        """
        c = conn.cursor()
        c.execute(sql)
        conn.commit()
        c.close()
        embed = discord.Embed(title='COMPRAS', description='Compra feita com sucesso! ', color=0x740000)
        embed.add_field(name=f'Você adquiriu {qtd} de {r[0][3]}.', value='', inline=False)
        embed.set_footer(text='Para mais informações, manda mensagem para o Guimts.')
        await ctx.message.reply(embed=embed)
    else:
        embed = discord.Embed(title='COMPRAS', description='Compra RECUSADA', color=0x740000)
        embed.add_field(name=f'Você não possui dinheiro suficiente pra isso...', value=f'Suas moedas: {r[0][1]}', inline=False)
        embed.set_footer(text='Para mais informações, manda mensagem para o Guimts.')
        await ctx.message.reply(embed=embed)



@shop.command()
@commands.check(ids)
async def add(ctx, nome=None, preco=None, estoque=None, desc=None, value=None):
    if nome is None or preco is None or estoque is None or desc is None or value is None:    
        await ctx.message.reply('Forneça o item, o preço, a quantidade, descrição e se o item está ativo!')
        return

    global conn
    sql = f"insert into bot.tbitens(nome, preco, estoque, descricao, ativo) values('{str(nome)}',{int(preco)}, {int(estoque)}, '{str(desc)}', {int(value)})"

    c = conn.cursor() 
    c.execute(sql)
    conn.commit()
    
    await ctx.message.reply(f'Item ``{nome}`` adicionado')

    
@bot.command()
async def myid(ctx):
    user_id = ctx.author.id
    await ctx.send(f"Seu ID de usuário é: {user_id}")
    
@shop.command()
@commands.check(ids)
async def coin(ctx, moedas, users):

    usar = users.replace('<', '').replace('@', '').replace('>','')
    global conn

    sql = f"select id, id_discord from bot.tbuser where id_discord = {usar}"

    c = conn.cursor() 
    c.execute(sql)
    s = c.fetchall()

    id = s[0][0]

    sql = f"select moedas from bot.tbmoeda where id_usuario = {id}"


    c = conn.cursor() 
    c.execute(sql)
    a = c.fetchall()
    moeda_a = a[0][0]

    sql =  f"""
        update 
        bot.tbmoeda     
        set moedas = {moedas}
        where id_usuario = {id}
    """

    c = conn.cursor() 
    c.execute(sql)
    conn.commit()


    moedas_antes = {moeda_a} - {moedas}

    embed = discord.Embed(title='MOEDAS', description='Alteração de moedas', color=0x740000)
    embed.add_field(name=f'As moedas do usuario foram atualizadas de {moedas_antes} para {moedas}', value='', inline=False)
    embed.set_footer(text='')
    await ctx.message.reply(embed=embed)


@bot.group()
async def inv(ctx, de=None):
    if de is None:
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
                
                embed.add_field(name=''+f" - Item: {palavra[1]}\n", value=''+f" - Quantidade: {palavra[2]}", inline=False)

        else:

            embed.add_field(name='**NENHUM ITEM DISPONIVEL**', value='', inline=False)
        embed.add_field(name='❛ ━━━━━━･❪ ❁ ❫ ･━━━━━━ ❜'"", value=f'- Moedas: {palavra[3]}'+f"", inline=False)
        await ctx.send(embed=embed)
        return
    else:
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
            where u.id_discord = {de.replace('<', '').replace('@', '').replace('>', '')}
        """ 
        c = conn.cursor() 
        c.execute(sql)
        s = c.fetchall()
        embed = discord.Embed(title='INVENTARIO', description=f'ITENS DE {de}', color=0x71368A)
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
        if(UNIX_TIMESTAMP(current_date) - m.cooldown < 79200, 1, 0),
        m.cooldown
        from bot.tbuser u
        join bot.tbmoeda m on m.id_usuario = u.id
        where u.id_discord = {user_id}
    """
    
    c = conn.cursor()
    c.execute(sql)
    r = c.fetchall()

    resgatado = r[0][2]
    if resgatado == 1:
        embed = discord.Embed(title='Daily JÁ RESGATADO', description='Aguarde 24 horas para pegar novamente!', color=0x740000)
        embed.add_field(name=f'Você já resgatou seu daily de hoje. Volte amanhã!', value='', inline=False)
        embed.set_footer(text='Para mais informações, manda mensagem para o Guimts.')
        await ctx.message.reply(embed=embed)
        return

    moedas = r[0][0]
    daily = random.randrange(10, 101)
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

    embed = discord.Embed(title='Daily RESGATADO', description='Aguarde 24 horas para pegar novamente!', color=0x740000)
    embed.add_field(name=f'Você tinha {moedas}, e ganhou {daily}, agora tem {moedasDaily}', value='', inline=False)
    embed.set_footer(text='Para mais informações, manda mensagem para o Guimts.')
    await ctx.message.reply(embed=embed)

@bot.command()
@commands.check(ids)
async def resetdaily(ctx):

    global conn
    sql = """update 
        bot.tbmoeda     
        set cooldown = 1
        where id_usuario
        """
    
    c = conn.cursor() 
    c.execute(sql)
    conn.commit()

    await ctx.message.reply('Daily resetado!')

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
async def calc(ctx, expression):
    try:
        result = eval(expression)
        await ctx.send(f"{expression} = {result}")
    except Exception as erro:
        (f"Erro ao calcular: {erro}")

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
@commands.check(ids)
async def banana(ctx, channel_name=None):
    if channel_name is None:
        await ctx.message.reply("Por favor, forneça o nome do novo canal!")
        return
    category = ctx.channel.category

    await ctx.channel.delete()

    await category.create_text_channel(channel_name)

@bot.command()
async def tst(ctx, amor):
    userid = ctx.author.id

    mor = amor.replace('<', '').replace('@', '').replace('>', '')
    await ctx.send(f"<@{mor}>\n Seu ID: {userid}")

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
@commands.has_permissions(ban_members=True)
async def punish(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.message.reply('Use algum subcomando! ``ban``, ``kick``, ``warn``, etc.')
        
@punish.command()
async def ban(ctx, member: discord.Member=None, reason=None):
    if ctx.author.guild_permissions.administrator:
        if member is None:
            embed = discord.Embed(title='Ajuda', description='**Punish**', color=0x740000)
            embed.add_field(name=f'Mencione um jogador válido.', value='!punish ban @jogador', inline=False)
            embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
            await ctx.message.reply(embed=embed)
            return
        else:
            await member.ban(reason=reason)
            embed = discord.Embed(title='Ban', description='**Punish**', color=0x740000)
            embed.add_field(name=f'O jogador foi banido(a)! Ninguém mandou fazer coisa errada!!', value='', inline=False)
            embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
            await ctx.message.reply(embed=embed)
    else:
        embed = discord.Embed(title='Ajuda', description='**Punish**', color=0x740000)
        embed.add_field(name='Opa, parece que algo deu errado. Você não tem permissão de executar esse comando!', value='', inline=False)
        embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
        await ctx.message.reply(embed=embed)
@punish.command()
async def mute(ctx, jogador: discord.Member):

    if ctx.author.guild_permissions.administrator:

        for cargo in jogador.roles[1:]:  
            await jogador.remove_roles(cargo)
        
        cargo_mute = discord.utils.get(ctx.guild.roles, name="mute")
        if cargo_mute is not None:
            await jogador.add_roles(cargo_mute)
            embed = discord.Embed(title='Mute', description='**Punish**', color=0x740000)
            embed.add_field(name=f'o jogador foi mutado(a)! Ninguém mandou fazer coisa errada!!', value='', inline=False)
            embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
            await ctx.message.reply(embed=embed)
        else:
            embed = discord.Embed(title='Ajuda', description='**Punish**', color=0x740000)
            embed.add_field(name='Opa, parece que algo deu errado, verifique se o cargo "mute" existe!', value='', inline=False)
            embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
            await ctx.message.reply(embed=embed)
    else:
            embed = discord.Embed(title='Ajuda', description='**Punish**', color=0x740000)
            embed.add_field(name='Opa, parece que algo deu errado. Você não tem permissão de executar esse comando!', value='', inline=False)
            embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
            await ctx.message.reply(embed=embed)

@bot.command()
async def unmute(ctx, jogador: discord.Member):
    if ctx.author.guild_permissions.administrator:
        cargo_mute = discord.utils.get(ctx.guild.roles, name="mute")

        if cargo_mute is not None:
            await jogador.remove_roles(cargo_mute)
            embed = discord.Embed(title='Unmute', description='**Punish**', color=0x740000)
            embed.add_field(name=f'O jogador foi desmutado(a) ou já estava!', value='', inline=False)
            embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
            await ctx.message.reply(embed=embed)
        else:
            embed = discord.Embed(title='Ajuda', description='**Punish**', color=0x740000)
            embed.add_field(name='Opa, parece que algo deu errado, verifique se o cargo "mute" existe!', value='', inline=False)
            embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
            await ctx.message.reply(embed=embed)
    else:
            embed = discord.Embed(title='Ajuda', description='**Punish**', color=0x740000)
            embed.add_field(name='Opa, parece que algo deu errado. Você não tem permissão de executar esse comando!', value='', inline=False)
            embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
            await ctx.message.reply(embed=embed)


@punish.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member=None, reason=None):
    if ctx.author.guild_permissions.administrator:

        if member is None:
            embed = discord.Embed(title='Ajuda', description='**Punish**', color=0x740000)
            embed.add_field(name=f'Mencione um jogador válido!', value='!punish kick @jogador', inline=False)
            embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
            await ctx.message.reply(embed=embed)
        else:
            await member.kick(reason=reason)
            embed = discord.Embed(title='Kick', description='**Punish**', color=0x740000)
            embed.add_field(name=f'O jogador foi expulso(a)! Ninguém mandou fazer coisa errada!!', value='', inline=False)
            embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
            await ctx.message.reply(embed=embed)
    else:
        embed = discord.Embed(title='Ajuda', description='**Punish**', color=0x740000)
        embed.add_field(name=f'Você não possui permissão para executar este comando.', value='', inline=False)
        embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')

@punish.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, member_id: int):
    try:
        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            if ban_entry.user.id == member_id:
                await ctx.guild.unban(ban_entry.user)
                embed = discord.Embed(title='Unban', description='**Punish**', color=0x740000)
                embed.add_field(name=f'Usuário desbanido.\nID: {member_id}', value='', inline=False)
                embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
                await ctx.message.reply(embed=embed)
                return
        
        if member_id not in banned_users:
            embed = discord.Embed(title='Membro não encontrado!', description='', color=0x740000)
            embed.add_field(name='Quer saber quem está?', value='Use ``!banlist``', inline=False)
            await ctx.send(embed=embed)

    except discord.Forbidden:
        embed = discord.Embed(title='Unban', description='**Punish**', color=0x740000)
        embed.add_field(name='Você não tem permissão para executar este comando.', value='', inline=False)
        await ctx.send(embed=embed)

@bot.command()
async def banlist(ctx):
    if ctx.author.guild_permissions.administrator:
        try:
            bans = await ctx.guild.bans()
            
            if bans:
                lista_banidos = [f'{ban.user.name} ID:({ban.user.id})' for ban in bans]
                await ctx.send(f'Membros banidos neste servidor:\n{", ".join(lista_banidos)}')
            else:
                embed = discord.Embed(title='Lista', description='**Punish**', color=0x740000)
                embed.add_field(name='Não há nenhum membro banido. Que ótimo!', value='Espero que nem precise...', inline=False)
                await ctx.message.reply(embed=embed)
        except Exception as e:
            await ctx.send(f"Ocorreu um erro ao listar os membros banidos: {e}")
    else:
        await ctx.send('Você não tem permissão para usar este comando.')

async def on_message(self, message):
        if message.content.startswith("!punish avisar"):
            mensagem = message.content[len("!punish avisar"):]
            if mensagem.startswith("\"") and mensagem.endswith("\""):
                mensagem = mensagem[1:-1]
            else:
                mensagem = None
            if mensagem is not None:
                self.comando(mensagem)
@punish.command()
async def avisar(ctx, membero, motivo):
    global conn 

    sql = f"""
        select
        count(*)
        from bot.tbuser u
        where u.id_discord = {membero.replace('<', '').replace('@', '').replace('>', '')}
        """
        
    c = conn.cursor()
    c.execute(sql)
    r = c.fetchall()
    id_discord = membero.replace('<', '').replace('@', '').replace('>', '')

    if int(r[0][0]) == 0:
        sql = f"""
            insert into bot.tbuser (id_discord)
            values ('{id_discord}')"""
        c = conn.cursor()
        c.execute(sql)
        conn.commit()
        c.close()

        sql = f"insert into bot.tbwarn(id_dc, avisos) values((select u.id from bot.tbuser u where u.id_discord = '{id_discord}'), 1);"
        c = conn.cursor()
        c.execute(sql)
        conn.commit()
        c.close()
    else:

        sql = f"select u.id from bot.tbuser u where u.id_discord = '{id_discord}'"
        c = conn.cursor()
        c.execute(sql)
        rato = c.fetchall()
        c.close()
        ba = rato[0][0]
        sql = f"""
        select 
        (select u.id from bot.tbuser u where u.id_discord = '{id_discord}') as id_user,
        (select a.id from bot.tbwarn a where a.id_dc = '{ba}') as id_warn,
        (select a.avisos from bot.tbwarn a where a.id_dc = '{ba}') as warn,
        (select a.motivos from bot.tbwarn a where a.id_dc = '{ba}') as motivo
        """
        c = conn.cursor()
        c.execute(sql)
        batata = c.fetchall()
        c.close()

        slk = batata[0][1]
        avisos = batata[0][2]

        sql = f"""update 
        bot.tbwarn
        set avisos = {avisos + 1}
        where id = {slk}
        """
        c = conn.cursor()
        c.execute(sql)
        conn.commit()
        c.close()
        if not motivo:
            sql = f"UPDATE bot.tbwarn SET motivos = 'Motivo não informado' WHERE id = {slk}"
            c = conn.cursor()
            c.execute(sql)
            conn.commit()
            c.close()
        else: 
            sql = f"UPDATE bot.tbwarn SET motivos = '{motivo}' WHERE id = {slk}"
            c = conn.cursor()
            c.execute(sql)
            conn.commit()
            c.close()
        total = avisos + 1
    

    embed = discord.Embed(title='AVISOS', description='', color=0x740000)
    embed.add_field(name=f"Usuario foi avisado!", value=f" - Avisos: {total}\n - Motivo: {motivo}", inline=False)

    if total >= 5:
        embed.add_field(name=f"5 AVISOS", value=f"``!punish mute @jogador``", inline=False)

    if total >= 7:
        embed.add_field(name=f"7 AVISOS", value=f"``!punish kick @jogador``", inline=False)
    
    if total >= 10:
        embed.add_field(name=f"**10 AVISOS**", value=f"``!punish ban @jogar``", inline=False)


    await ctx.send(embed=embed)    
    
@punish.command()
async def perdoar(ctx, membro):
    global conn

    id_discord = membro.replace('<', '').replace('@', '').replace('>', '')

    sql = f"select u.id from bot.tbuser u where u.id_discord = '{id_discord}'"
    c = conn.cursor()
    c.execute(sql)
    rato = c.fetchall()
    c.close()

    ba = rato[0][0]

    sql = f"""
    select 
    (select u.id from bot.tbuser u where u.id_discord = '{id_discord}') as id_user,
    (select a.id from bot.tbwarn a where a.id_dc = '{ba}') as id_warn,
    (select a.avisos from bot.tbwarn a where a.id_dc = '{ba}') as warn,
    (select a.motivos from bot.tbwarn a where a.id_dc = '{ba}') as MOTIVOS
    """
    
    c = conn.cursor()
    c.execute(sql)
    batata = c.fetchall()
    c.close()

    slk = batata[0][1]
    avisos = batata[0][2]
    motivos = batata[0][3]
    sql = f"""update 
    bot.tbwarn
    set avisos = 0
    where id = {slk}
    """
    c = conn.cursor()
    c.execute(sql)
    conn.commit()
    c.close()

    sql = f"UPDATE bot.tbwarn SET motivos = 'Nenhum' WHERE id = {slk}"
    c = conn.cursor()
    c.execute(sql)
    conn.commit()
    c.close()

    total = 0
    
    embed = discord.Embed(title='PERDÃO', description='', color=0x740000)
    embed.add_field(name=f"Usuario foi perdoado!", value=f" - Avisos: {total}\n - Motivo recente: Nenhum", inline=False)

    await ctx.send(embed=embed)    

@punish.command()
async def avisos(ctx, member):
    global conn 
    sql = f"""
        select
        count(*)
        from bot.tbuser u
        where u.id_discord = {member.replace('<', '').replace('@', '').replace('>', '')}
        """
    
    disc = member.replace('<', '').replace('@', '').replace('>', '')
    c = conn.cursor()
    c.execute(sql)
    r = c.fetchall()
    
    embed = discord.Embed(title='AVISOS', description=f'', color=0x740000)        
    if int(r[0][0]) == 1:

        sql = f"select u.id from bot.tbuser u where u.id_discord = '{disc}'"
        c = conn.cursor()
        c.execute(sql)
        rato = c.fetchall()
        c.close()
        ba = rato[0][0]

        sql = f"""
        select 
        (select u.id from bot.tbuser u where u.id_discord = '{disc}') as id_user,
        (select a.id from bot.tbwarn a where a.id_dc = '{ba}') as id_warn,
        (select a.avisos from bot.tbwarn a where a.id_dc = '{ba}') as warn,
        (select a.motivos from bot.tbwarn a where a.id_dc = '{ba}') as avisos
        """
        c = conn.cursor()
        c.execute(sql)
        batata = c.fetchall()
        c.close()
        aviso = batata[0][2]
        motivo_rec = batata[0][3]
        total = aviso + 1 
        embed.add_field(name=f"Este jogador tem:", value=f" - Avisos: {aviso} \n- Motivo recente: {motivo_rec}", inline=False)

        if total >= 5:
            embed.add_field(name=f"5 AVISOS", value=f"``!punish mute @jogador``", inline=False)

        if total >= 7:
            embed.add_field(name=f"7 AVISOS", value=f"``!punish kick @jogador``", inline=False)
        
        if total >= 10:
            embed.add_field(name=f"**10 AVISOS**", value=f"``!punish ban @jogar``", inline=False)
            embed.add_field(name="•——◤✧◥——•", value="", inline=False)
    else:
        embed.add_field(name='**Nada encontrado**', value='', inline=False)
    await ctx.send(embed=embed)
    return




@bot.command()
async def teste(ctx, wubba, member: discord.Member=None ):
    await ctx.message.reply(f'Você mencionou {member}')
    await ctx.send(f"{wubba.replace('<', 'gay', 1)}")

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

@bot.command()
async def ajuda(ctx):
    await ctx.message.reply("Peço desculpas, o comando ``!help`` e ``ajuda`` estão em manutenção. Caso haja alguma dúvida, consulte meu criador: <@617362818299199498>")
#    author = ctx.message.author
#    embed = discord.Embed(title='Ajuda', description='Aqui está a lista de comandos disponíveis:', color=0x740000)
#    embed.add_field(name='!r <XdY>, ou !roll', value='O famoso rola um d20, rola um dado de 6 a 100 lados.', inline=False)
#    embed.add_field(name='!escolhe (opção1) (opção2)', value='Tá em dúvida? Que tal uma ajudinha do bot!', inline=False)
#    embed.add_field(name='!ppt <pedra,pepel ou tesoura>', value='Pedra, papel e tesoura; Envie ppt (pedra, papel ou tesoura). O bot escolhera um aleatório para ele', inline=False)
#    embed.add_field(name='!moeda', value='Quer brincar de cara ou coroa?', inline=False)
#    embed.add_field(name='!calc (+, -, *, **, /)', value='1 + 1 = x?', inline=False)
#    embed.add_field(name='!contagem (iniciar)(cancelar)', value='Está com padrão de segundos, então 120 = 2m, etc. "!contagem iniciar 10"', inline=False)
#    embed.add_field(name='!tempo', value='Parecido com !contagem, porém funciona da seguinte forma: Você ira enviar "!tempo <comando> <1s,1m,1h,1d>" e ele irá executar o comando depois do tempo determiado.', inline=False)
#    embed.add_field(name='!forca', value='Um joguinho da forca para descontrair ia ser legal, não?', inline=False)
#    embed.add_field(name='!cantada', value='Uma cantada pra mandar pro crush? Ou esteja se sentindo carente ksks', inline=False)
#    embed.add_field(name='!anagrama', value='Um joguinho de anagrama, vai.', inline=False)
#    embed.add_field(name='!ship (nome) (nome)', value='Um joguinho pra ver suas chances com a(o) crushzinho :3', inline=False)
#    embed.add_field(name='!tapa', value='Quer dar um tapa naquela pessoa irritante?', inline=False)
#    embed.add_field(name='!abraço', value='Retribua com um abraço para aquela pessoa especial!', inline=False)
#    embed.add_field(name='!beijo', value='Hmm, beijinho bom..', inline=False)
#    embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
#    await author.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def adm(ctx):
    author = ctx.message.author
    embed = discord.Embed(title='Ajuda', description='Aqui está a lista de comandos de administradores disponíveis:', color=0x740000)
    embed.add_field(name='!clear (quantidade)', value='Deleta aquele monte de conversa do chat.', inline=False)
    embed.add_field(name='!punish ban (@player)', value='Banido!', inline=False)
    embed.add_field(name='!punish kick (@player)', value='Expulso!', inline=False)
    embed.add_field(name='!punish unban (ID Player)', value='Desbane um jogador!', inline=False)
    embed.add_field(name='!unmute (ID player)', value='Desumuta um jogador!', inline=False)
    embed.add_field(name='!punish mute (@player)', value='Silencia o jogador, porém deve ter o cargo "mute" no servidor!', inline=False)
    embed.add_field(name='!banlist', value='Exibe a lista de usuarios banidos no servidor!', inline=False)
    embed.add_field(name='!punish warn (@player)', value='Avisa um jogador quando faz algo errado!', inline=False)
    embed.add_field(name='!punish warns', value='Exibe os jogadores em estado de aviso!', inline=False)
    embed.add_field(name='!dado (set, unset ou show)', value='Adiciona um número viciado ao dado, retira ou vê qual está setado!', inline=False)
    embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
    await author.send(embed=embed)


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
async def roll(ctx, dice: str):
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



@bot.command()
async def r(ctx, dice: str):
    try:
        dice_list = dice.split('#')
        result_texts = []


        for dice_entry in dice_list:
            dice, *positive = re.split(r'\+', dice_entry)
            dice, *negative = re.split(r'\-', dice)
            rolls, limit = map(int, dice.split('d'))



            if rolls < 1 or rolls > 60:
                embed = discord.Embed(title='Algo deu errado. :game_die:', description='', color=0x740000)
                embed.add_field(name='Número inválido de dados. Use entre 1 e 60 dados.', value='', inline=False)
                embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
                await ctx.message.reply(embed=embed)
                return

            if limit < 1 or limit > 1000:
                embed = discord.Embed(title='Algo deu errado. :game_die:', description='', color=0x740000)
                embed.add_field(name='Eita, acho que deu um exagero de dados aí ein. Use até 1d1000', value='', inline=False)
                embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
                await ctx.message.reply(embed=embed)
                return

            results = [random.randint(1, limit) for _ in range(rolls)]
            modifier_total = sum(int(modifier) for modifier in positive) - sum(int(modifier) for modifier in negative)

            if ctx.author.id in user_settings:
                fixed_value = user_settings[ctx.author.id]
                results = [fixed_value] * rolls

            total = sum(results) + modifier_total
            result_text = ', '.join(str(result) for result in results)
            result_texts.append(f'{result_text}\n TOTAL: {total} <:20:1137750453359214653>\nAdicionado: {modifier_total}')

        response = "\n\n".join(result_texts)
        embed = discord.Embed(title=':game_die: ʕ •ᴥ•ʔ :game_die:', description='', color=0x740000)
        embed.add_field(name='Resultados dos dados:', value=response, inline=False)
        await ctx.message.reply(embed=embed)

    except Exception:
        embed = discord.Embed(title='Algo deu errado. :game_die:', description='Use esse formato:', color=0x740000)
        embed.add_field(name='!r (Quantidade de dados e Dado desejado [+/- Modificadores] ou 1d20#1d20)', value='1d20 Por exemplo!', inline=False)
        embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
        await ctx.message.reply(embed=embed)
        ('Erro')

@bot.command()
async def rolar(ctx, dice: str):
    try:
        dice_list = dice.split('#')
        result_texts = []


        for dice_entry in dice_list:
            dice, *positive = re.split(r'\+', dice_entry)
            dice, *negative = re.split(r'\-', dice)
            rolls, limit = map(int, dice.split('x'))



            if rolls < 1 or rolls > 20:
                embed = discord.Embed(title='Algo deu errado. :game_die:', description='', color=0x740000)
                embed.add_field(name='Número inválido de dados. Use entre 1 e 20 dados.', value='', inline=False)
                embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
                await ctx.message.reply(embed=embed)
                return

            if limit < 1 or limit > 1000:
                embed = discord.Embed(title='Algo deu errado. :game_die:', description='', color=0x740000)
                embed.add_field(name='Eita, acho que deu um exagero de dados aí ein. Use até 1d1000', value='', inline=False)
                embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
                await ctx.message.reply(embed=embed)
                return

            results = [random.randint(1, limit) for _ in range(rolls)]
            modifier_total = sum(int(modifier) for modifier in positive) - sum(int(modifier) for modifier in negative)

            if ctx.author.id in user_settings:
                fixed_value = user_settings[ctx.author.id]
                results = [fixed_value] * rolls

            total = sum(results) + modifier_total
            result_text = f' ⟵ {dice}\n'.join(str(result) for result in results)
            result_texts.append(f' {result_text} ⟵ {dice} \n TOTAL: {total} <:20:1137750453359214653>\nAdicionado: {modifier_total}')
            
        response = "\n\n".join(result_texts)
        embed = discord.Embed(title=':game_die: ʕ •ᴥ•ʔ :game_die:', description='', color=0x740000)
        embed.add_field(name=f'Resultados do(s) teu(s) {rolls} dado(s)!', value=response, inline=False)
        await ctx.message.reply(embed=embed)

    except Exception:
        embed = discord.Embed(title='Algo deu errado. :game_die:', description='Use esse formato:', color=0x740000)
        embed.add_field(name='!r (Quantidade de dados e Dado desejado [+/- Modificadores] ou 1d20#1d20)', value='1d20 Por exemplo!', inline=False)
        embed.set_footer(text='Para mais informações, manda mensagem para o Gui aí.')
        await ctx.message.reply(embed=embed)
        ('Erro')


@bot.group()
async def embed(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(title=f'Precisa de ajuda?', description=f'Comandos do Embed:', color=0x740000)
        embed.add_field(name=f'!embed info', value=f'Aprensetará as informações pra você', inline=False)
        embed.add_field(name=f'!embed send', value=f'Assim que você enviará suas mensagens', inline=False)
        await ctx.message.reply(embed=embed)

@embed.command()
async def send(canal: discord.TextChannel, *, argumento):
    partes = re.findall(r'"([^"]*)"', argumento) 

    palavra = partes[0].strip() if partes else ""
    desc = partes[1].strip() if len(partes) > 1 else ""
    resto = partes[2].strip() if len(partes) > 2 else ""
    val = partes[3].strip() if len(partes) > 3 else ""
    foot = partes[4].strip() if len(partes) > 4 else ""

    embed = discord.Embed(title=f'{palavra}', description=f'{desc}', color=0x740000)
    embed.add_field(name=f'{resto}', value=f'{val}', inline=False)
    embed.set_footer(text=f'{foot}')
    await canal.send(embed=embed)

@embed.command()
async def info(ctx):
    embed = discord.Embed(title=f'Precisa de ajuda?', description=f'Como funciona?', color=0x740000)
    embed.add_field(name=f'!embed send', value=f"Simples! Use ``!embed 'Canal(#canal)', 'Titulo', 'Descrição', 'Corpo', 'Descrição', 'Rodapé'``. Detalhe, não é obrigatorio preencher todos os campos! (COLOQUE ÁSPAS ENTRE AS PALAVRAS, MENOS NO CANAL DESTINO)", inline=False)
    await ctx.message.reply(embed=embed)

#peguei do chatgpt dane-se
@bot.command()
async def emoji(ctx, emoji_name):
    if ctx.guild.me.guild_permissions.manage_emojis:
        emoji = discord.utils.get(ctx.guild.emojis, name=emoji_name)
        if emoji:
            await ctx.send(f"O ID do emoji {emoji_name} é {emoji.id}")
        else:
            await ctx.send(f"Emoji {emoji_name} não encontrado neste servidor.")
    else:
        await ctx.send("O bot não tem permissão para gerenciar emojis.")
    
@bot.command()
@commands.check(ids)
async def remover(ctx, comando):
    bot.remove_command(f'{comando}')
    await ctx.message.reply(f'``!{comando}`` foi removido!')




    


bot.run('MTA5NjkzODU4NjU5NjcxMjYzOQ.G5GE_Y.INjo5BbjUAqDZo0Gt5b36ENsP7g_KxZEUZxGtg')
