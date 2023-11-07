import discord
from discord import app_commands
from discord.ext import commands
from config import *
import datetime
import pymongo
from discord import ui
from discord.ui import Button, View
intents = discord.Intents.all()
intents.message_content = True

client = pymongo.MongoClient(url)
db = client.dm_data


today = datetime.datetime.now()
date_time = today.strftime("%d/%m/%Y  %H.%M.%S")
saat = today.strftime("%H %M %S")
tarih = today.strftime("%d/%m/%Y  %H.%M")

class LeoOnayRed(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Onayla', style=discord.ButtonStyle.green, custom_id='leo_onayla')
    async def but_onay(self, interaction: discord.Interaction, button: discord.ui.Button):
        hex = {"msg_id": interaction.message.id}
        admin = interaction.guild.get_role(admin_rol_id)
        yeni_yetkili = interaction.guild.get_role(yeni_yetkili_rol_id)
        basvuru_kanal = interaction.guild.get_channel(basvuru_durum_kanal_id)
        if admin not in interaction.user.roles: 
            await interaction.response.send_message(f"Butona bassmak için <@&{admin_rol_id}>", ephemeral=True)
        elif admin in interaction.user.roles:
            if db.basvuru.count_documents(hex) == 1:
                member2 = db.basvuru.find(hex)
                for i in member2:
                    info = int(i['uye_id'])
                    member = await interaction.guild.fetch_member(info)
                    await member.add_roles(yeni_yetkili)
                    db.basvuru.delete_one(hex)
                    OnayEmbed = discord.Embed(
                    title = f"Başvuru Onaylandı",
                    description = f'<@{info}> kullanıcısının başvurusu onaylandı\nonaylayan yetkili {interaction.user}',
                    colour = discord.Colour.green()
                )
                await interaction.response.edit_message(embed=OnayEmbed, view=None)
                await basvuru_kanal.send(f"<@{info}> ({info}) kullanıcısının başvurusu {interaction.user} tarafından **ONAYLANDI** ✅")
                await member.send(f"Hey başvurun {interaction.user} tarafından onaylandı ekibimize hoş geldin")
            else:
                interaction.response.send_message("Database kaynaklı bir sorun var lütfen üst yetkiliye bildirin")
        else:
            await interaction.response.send_message("Bir hata oluştu lütfen yetkiliye bildirin")

    @discord.ui.button(label='Reddet', style=discord.ButtonStyle.red, custom_id='leo_reddet')
    async def but_red(self, interaction: discord.Interaction, button: discord.ui.Button):
        hex = {"msg_id": interaction.message.id}
        admin = interaction.guild.get_role(admin_rol_id)
        if admin not in interaction.user.roles: 
            await interaction.response.send_message(f"Butona bassmak için <@&{admin_rol_id}>", ephemeral=True)
        elif admin in interaction.user.roles:
            if db.basvuru.count_documents(hex) == 1:
                member2 = db.basvuru.find(hex)
                for i in member2:
                    info = int(i['uye_id'])
                    member = await interaction.guild.fetch_member(info)
                    RedEmbed = discord.Embed(
                    title = f"Başvuru Reddedildi",
                    description = f'<@{info}> kullanıcısının başvurusu reddedildi\nreddeden yetkili {interaction.user}',
                    colour = discord.Colour.red()
                )
                await interaction.response.send_modal(RedModal())
        else:
            await interaction.response.send_message("Bir hata oluştu lütfen yetkiliye bildirin")


class BasvuruModal(ui.Modal, title="Başvuru Sistemi"):
    ad = ui.TextInput(label="Adın ne?", placeholder="Leo...", style=discord.TextStyle.short)
    yas = ui.TextInput(label="Kaç yaşındasın?", placeholder="18", style=discord.TextStyle.short, max_length=2)
    onay = ui.TextInput(label="kuralları kabul ettiğini onaylıyor musun?", placeholder="onaylıyorum/onaylamıyorum", style=discord.TextStyle.short, max_length=13)

    async def on_submit(self, interaction: discord.Interaction):
        today2 = datetime.datetime.now()
        tarih2 = today2.strftime("%d/%m/%Y  %H.%M")
        pp = interaction.user.avatar.with_size(64)
        eembed = discord.Embed(
            title = f"Başarılı",
            description = f'Başvurunu yetkililere ve bir kopyasını da sana gönderdim başvuru sonucunu sana DM yoluyla ileticem eğer mesaj alamıyorsan <#{basvuru_durum_kanal_id}> kanalından takip edebilirsin.',
            colour = discord.Colour.green()
        )
        eembed.set_author(name=f"{bot.user.name}", icon_url=f"{bot.user.avatar}")
        eembed.add_field(name=f'{interaction.user}', value=f'``Ad:`` {self.ad}\n``ID: `` {interaction.user.id}\n``Yaş:`` {self.yas}\n``Onay:`` **{self.onay}**\n``Tarih:`` {tarih2}')
        await interaction.response.edit_message(embed=eembed, view=None)
        log_channel = bot.get_channel(log_kanal_id)
        embed = discord.Embed(
            title = f"{interaction.user}",
            description = f'``Ad:`` {self.ad}\n``Yaş:`` {self.yas}\n``Onay:`` **{self.onay}**\n``Tarih:`` {tarih2}',
            colour = discord.Colour.blue()
        )
        embed.set_thumbnail(url=pp)
        embed.set_footer(text=f"{interaction.user}", icon_url=f"{pp}")
        msg = await log_channel.send(embed=embed, view=LeoOnayRed())
        id1 = interaction.user.id
        id2 = msg.id
        db.basvuru.insert_one(
                    {
                        "uye_id": id1,
                        "msg_id": id2,
                        "tarih": f"{tarih2}",
                    }
                )

class Istek(ui.Modal, title="İstek Öneri Sistemi"):
    konu = ui.TextInput(label="Konu?", style=discord.TextStyle.short)
    oneri = ui.TextInput(label="istek/öneri?", style=discord.TextStyle.long, max_length=500)

    async def on_submit(self, interaction: discord.Interaction):
        today2 = datetime.datetime.now()
        tarih2 = today2.strftime("%d/%m/%Y  %H.%M")
        tarih3 = today2.strftime("%Y%m%d%H%M%S")
        hex = {"uye_id": interaction.user.id}
        hex2 = {"$set": {"t_hesap": tarih3}}
        eembed = discord.Embed(
            title = f"Başarılı",
            description = f'İsteğin/Önerin başarıyla gönderildi önerini görmek için <#{öneri_kanal}> kanalını kontrol edebilirsin.',
            colour = discord.Colour.random()
        )
        if db.oneri.count_documents(hex) == 1:
            member2 = db.oneri.find(hex)
            for i in member2:
                sure_kontrol = int(i['t_hesap'])
                islem = int(tarih3) - sure_kontrol
                if islem > oneri_sure:
                    await interaction.response.edit_message(embed=eembed, view=None)
                    oneri_channel = bot.get_channel(öneri_kanal)
                    pp = interaction.user.avatar.with_size(64)
                    kabul = '✅'
                    red = '❌'
                    embed = discord.Embed(
                        title = f"İstek/Öneri",
                        description = f'``Konu:`` **{self.konu}**\n``İstek/Öneri:`` **{self.oneri}**\n``Kullanıcı ID:`` **{interaction.user.id}**\n``Tarih:`` {tarih2}',
                        colour = discord.Colour.random()
                    )
                    embed.set_author(name=f"{bot.user.name}", icon_url=f"{bot.user.avatar}")
                    embed.set_thumbnail(url=f"{pp}")
                    embed.set_footer(text=f"{interaction.user}", icon_url=f"{pp}")    
                    mesaj = await oneri_channel.send(embed=embed)
                    await mesaj.add_reaction(kabul)
                    await mesaj.add_reaction(red)
                    id1 = interaction.user.id
                    db.oneri.update_one(hex, hex2)

        elif db.oneri.count_documents(hex) == 0:
            await interaction.response.edit_message(embed=eembed, view=None)
            oneri_channel = bot.get_channel(öneri_kanal)
            pp = interaction.user.avatar.with_size(64)
            kabul = '✅'
            red = '❌'
            embed = discord.Embed(
                title = f"İstek/Öneri",
                description = f'``Konu:`` **{self.konu}**\n``İstek/Öneri:`` **{self.oneri}**\n``Kullanıcı ID:`` **{interaction.user.id}**\n``Tarih:`` {tarih2}',
                colour = discord.Colour.random()
            )
            embed.set_author(name=f"{bot.user.name}", icon_url=f"{bot.user.avatar}")
            embed.set_thumbnail(url=f"{pp}")
            embed.set_footer(text=f"{interaction.user}", icon_url=f"{pp}")    
            mesaj = await oneri_channel.send(embed=embed)
            await mesaj.add_reaction(kabul)
            await mesaj.add_reaction(red)
            id1 = interaction.user.id
            db.oneri.insert_one(
                        {
                            "uye_id": id1,
                            "t_hesap": tarih3,
                        }
                    )
        else:
            print("bir hata var")


class RedModal(ui.Modal, title="Başvuru Sistemi"):
    sebep = ui.TextInput(label="Reddetme sebebi", placeholder="Trol/Başka sebepler vs.", style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction):
        hex = {"msg_id": interaction.message.id}
        basvuru_kanal = interaction.guild.get_channel(basvuru_durum_kanal_id)
        today2 = datetime.datetime.now()
        tarih3 = today2.strftime("%d%m%Y%H%M%S")
        member2 = db.basvuru.find(hex)
        for i in member2:
            info = int(i['uye_id'])
            member = await interaction.guild.fetch_member(info)
            RedEmbed = discord.Embed(
            title = f"Başvuru Reddedildi",
            description = f'<@{info}> kullanıcısının başvurusu reddedildi\nreddeden yetkili {interaction.user}',
            colour = discord.Colour.red()
        )
            db.red.insert_one(
                    {
                        "uye_id": info,
                        "t_hesap": tarih3,
                    }
                )
            db.basvuru.delete_one(hex)
            await interaction.response.edit_message(embed=RedEmbed, view=None)
            await basvuru_kanal.send(f"<@{info}> ``({info})`` kullanıcısının başvurusu {interaction.user} tarafından ``{self.sebep}`` sebebiyle **REDDEDİLDİ** ❌")
            await member.send(f"Başvurun {interaction.user} tarafından ``{self.sebep}`` sebebiyle reddedildi.")
        

class LeoYetkili(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Başvuru Yap', style=discord.ButtonStyle.green, custom_id='leo_basvuru')
    async def but_basvur(self, interaction: discord.Interaction, button: discord.ui.Button):
        hex = {"uye_id": interaction.user.id}
        today2 = datetime.datetime.now()
        tarih3 = today2.strftime("%d%m%Y%H%M%S")
        guild = bot.get_guild(server_id)
        member = await guild.fetch_member(interaction.user.id)
        yetkili = guild.get_role(yeni_yetkili_rol_id) 
        admin = guild.get_role(admin_rol_id)
        if not member:
            await interaction.response.send_message("Yetkili başvurusu yapabilmek için sunucumuzda bulunman lazım.")
        elif yetkili in member.roles or admin in member.roles:
            await interaction.response.send_message("Dostum zaten yetkilisin.")
        elif db.blacklist.count_documents(hex) == 1:
            await interaction.response.send_message("Üzgünüm karalistede olduğun için başvuru yapamazsın\nBir hata olduğunu düşünüyorsan yetkililer ile iletişime geçebilirsin")
        elif db.basvuru.count_documents(hex) == 1: 
            await interaction.response.send_message(f"Zaten bekleyen bir başvurun var başvuru durumunu <#{basvuru_durum_kanal_id}> kanalından takip edebilirsin")
        elif db.red.count_documents(hex) == 1:
            member2 = db.red.find(hex)
            for i in member2:
                sure_kontrol = int(i['t_hesap'])
                islem = int(tarih3) - sure_kontrol
                if islem < basvuru_sure:
                   kalan = basvuru_sure - islem
                   dakika, kalan = divmod(kalan, 60)
                   saat, dakika = divmod(dakika, 60)
                   gun, saat = divmod(saat, 24)
                   await interaction.response.send_message(f"Daha önceden başvuru yaptın ve red yedin yeni başvurunu ``{gun}`` gün ``{saat}`` saat ``{dakika}`` dakika  ``{kalan}`` saniye sonra gönderebilirsin") 
                if islem >= basvuru_sure:
                    db.red.delete_one(hex)
                    await interaction.response.send_modal(BasvuruModal())
        elif db.red.count_documents(hex) == 0:
            await interaction.response.send_modal(BasvuruModal())
        else:
            await interaction.response.send_message("Database ile alakalı bir hata oluştu lütfen bir yetkili ile iletişime geçiniz")

    @discord.ui.button(label='Ana Menüye Dön', style=discord.ButtonStyle.red, custom_id='leo_anamenu')
    async def but_anamenu(self, interaction: discord.Interaction, button: discord.ui.Button):
        button_label = "Canlı Destek"
        button_url = f"https://discord.com/channels/{server_id}/{destek_kanal_id}"
        LeoDMEmbed = discord.Embed(
                title = f'DM Bilgi',
                description ="``1.`` Yetkili başvurusu hakkında bilgi almak için ``Yetki Bilgi`` Butonuna tıklayınız\n``2.`` İstek/Öneri için ``istek/öneri`` Butonuna tıklayınız\n``3.`` Canlı destek için ``Canlı Destek`` Butonuna tıklayınız\n",
                colour = discord.Colour.blue()
            )
        LeoDMEmbed.set_footer(text=footer)
        view = LeoDM()
        button = discord.ui.Button(style=discord.ButtonStyle.link, label=button_label, url=button_url)
        view.add_item(button)
        await interaction.response.edit_message(embed=LeoDMEmbed, view=view)

class LeoDM(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Yetki Bilgi', style=discord.ButtonStyle.primary, custom_id='leo_x')
    async def but_x(self, interaction: discord.Interaction, button: discord.ui.Button):
        LeoYetkiEmbed = discord.Embed(
                title = f'Yetki Bilgi',
                description ="**Yetkili Başvurusu İçin Şartlar**\n``1.`` Günlük en az 5 davet\n``2.`` Günlük minimum 1 saat sesli odalarda bulunma\n``3.`` Üst yetkilinin söylediklerini yerine getirme\n``4.`` Yetkiyi kötüye kullanmama\n\n**Başvuruyu gönderdiğinizde kuralları kabul etmiş sayılacaksınız.**",
                colour = discord.Colour.blue()
            )
        LeoYetkiEmbed.set_footer(text=footer)
        await interaction.response.edit_message(embed=LeoYetkiEmbed, view=LeoYetkili())
    
    @discord.ui.button(label='İstek/Öneri', style=discord.ButtonStyle.primary, custom_id='leo_y')
    async def but_y(self, interaction: discord.Interaction, button: discord.ui.Button):
        today2 = datetime.datetime.now()
        tarih3 = today2.strftime("%Y%m%d%H%M%S")
        hex = {"uye_id": interaction.user.id}
        if db.oblacklist.count_documents(hex) == 1:
            await interaction.response.send_message(f"Üzgünüm karalistede olduğun için öneri yapamazsın\nBir hata olduğunu düşünüyorsan yetkililer ile iletişime geçebilirsin")
        elif db.oneri.count_documents(hex) == 1:
            member2 = db.oneri.find(hex)
            for i in member2:
                sure_kontrol = int(i['t_hesap'])
                islem = int(tarih3) - sure_kontrol
                if islem < oneri_sure:
                    kalan = oneri_sure - islem
                    dakika, kalan = divmod(kalan, 60)
                    saat, dakika = divmod(dakika, 60)
                    gun, saat = divmod(saat, 24)
                    await interaction.response.send_message(f"Daha önceden öneri yaptın yeni önerini ``{gun}`` gün ``{saat}`` saat ``{dakika}`` dakika  ``{kalan}`` saniye sonra gönderebilirsin")
                elif islem > oneri_sure:
                    await interaction.response.send_modal(Istek())
        elif db.oneri.count_documents(hex) == 0:
            await interaction.response.send_modal(Istek())
        else: 
            print("bir hata var istek öneri kısmı")
     

class LeoButtonListener(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('!'), intents=intents) # ! yerine prefixinizi yazabilirsiniz - you can prefix here currentprefix is !

    async def setup_hook(self) -> None:
        self.add_view(LeoDM())
        self.add_view(LeoYetkili())
        self.add_view(LeoOnayRed())

bot = LeoButtonListener()


@bot.tree.command(name="basvuru-blacklist", description="Etiketlediğiniz üyeyi başvuru yapamaması için kara listeye alır")
@app_commands.describe(uye = "Kara listeye almak/çıkarmak istediğiniz üye")
@app_commands.describe(uye = "Kara listeye alma/çıkarma Sebebiniz")
async def bbl(interaction: discord.Interaction, uye: discord.Member, sebep: str="Sebep belirtilmemiş"):
    log_channel = bot.get_channel(black_list_log)
    role = interaction.guild.get_role(admin_rol_id)
    today2 = datetime.datetime.now()
    tarih3 = today2.strftime("%d/%m/%Y %H.%M:%S")
    hex = {"uye_id": uye.id}
    if role not in interaction.user.roles:
        await interaction.response.send_message(f"Bu komutu kullanma yetkin yok komutu kullanabilmek için <@&{admin_rol_id}> rolüne sahip olman lazım", ephemeral=True)
    elif role in interaction.user.roles:
        if db.blacklist.count_documents(hex) == 1:
            db.blacklist.delete_one(hex)
            pp = interaction.user.avatar.with_size(64)
            pp2 = uye.avatar.with_size(64)
            blembed = discord.Embed(
                title = "Başvuru Black List'den Çıkarma İşlem Başarılı",
                description = f"**»** İşlemi Yapan Yetkili: ``{interaction.user}``\n**»** İşlemi Yapan Yetkili ID: ``{interaction.user.id}``\n**»** İşlem Yapılan Üye: ``{uye}``\n**»** İşlem Yapılan Üye ID: ``{uye.id}``\n**»** Sebep: ``{sebep}``",
                colour = discord.Colour.green()
            )
            blembed.set_thumbnail(url=pp2)
            blembed.set_footer(text=f"Yetkili: {interaction.user}   ---   {tarih3}", icon_url=pp)
            await interaction.response.send_message(embed=blembed)
            await log_channel.send(embed=blembed)
        elif db.blacklist.count_documents(hex) == 0:
            db.blacklist.insert_one(
                {
                    "uye_id": uye.id,
                    "yetkili_id": interaction.user.id,
                    "tarih": f"{tarih3}",
                    "sebep": f"{sebep}"
                }
            )
            pp = interaction.user.avatar.with_size(64)
            pp2 = uye.avatar.with_size(64)
            blembed = discord.Embed(
                title = "Başvuru Black List'e Ekleme İşlem Başarılı",
                description = f"**»** İşlemi Yapan Yetkili: ``{interaction.user}``\n**»** İşlemi Yapan Yetkili ID: ``{interaction.user.id}``\n**»** İşlem Yapılan Üye: ``{uye}``\n**»** İşlem Yapılan Üye ID: ``{uye.id}``\n**»** Sebep: ``{sebep}``",
                colour = discord.Colour.red()
            )
            blembed.set_thumbnail(url=pp2)
            blembed.set_footer(text=f"Yetkili: {interaction.user}   ---   {tarih3}", icon_url=pp)
            await interaction.response.send_message(embed=blembed)
            await log_channel.send(embed=blembed)
        else:
            await interaction.response.send_message("Bilinmeyen bir hata oldu lütfen geliştirici ile iletişime geçiniz")
    else:
        await interaction.response.send_message("Bilinmeyen bir hata oldu lütfen geliştirici ile iletişime geçiniz")


@bot.tree.command(name="oneri-blacklist", description="Etiketlediğiniz üyeyi öneri yapamaması için kara listeye alır")
@app_commands.describe(uye = "Kara listeye almak/çıkarmak istediğiniz üye")
@app_commands.describe(uye = "Kara listeye alma/çıkarma Sebebiniz")
async def obl(interaction: discord.Interaction, uye: discord.Member, sebep: str="Sebep belirtilmemiş"):
    log_channel = bot.get_channel(black_list_log)
    role = interaction.guild.get_role(admin_rol_id)
    today2 = datetime.datetime.now()
    tarih3 = today2.strftime("%d/%m/%Y %H.%M:%S")
    hex = {"uye_id": uye.id}
    if role not in interaction.user.roles:
        await interaction.response.send_message(f"Bu komutu kullanma yetkin yok komutu kullanabilmek için <@&{admin_rol_id}> rolüne sahip olman lazım", ephemeral=True)
    elif role in interaction.user.roles:
        if db.oblacklist.count_documents(hex) == 1:
            db.oblacklist.delete_one(hex)
            pp = interaction.user.avatar.with_size(64)
            pp2 = uye.avatar.with_size(64)
            blembed = discord.Embed(
                title = "Öneri Black List'den Çıkarma İşlem Başarılı",
                description = f"**»** İşlemi Yapan Yetkili: ``{interaction.user}``\n**»** İşlemi Yapan Yetkili ID: ``{interaction.user.id}``\n**»** İşlem Yapılan Üye: ``{uye}``\n**»** İşlem Yapılan Üye ID: ``{uye.id}``\n**»** Sebep: ``{sebep}``",
                colour = discord.Colour.green()
            )
            blembed.set_thumbnail(url=pp2)
            blembed.set_footer(text=f"Yetkili: {interaction.user}   ---   {tarih3}", icon_url=pp)
            await interaction.response.send_message(embed=blembed)
            await log_channel.send(embed=blembed)
        elif db.oblacklist.count_documents(hex) == 0:
            db.oblacklist.insert_one(
                {
                    "uye_id": uye.id,
                    "yetkili_id": interaction.user.id,
                    "tarih": f"{tarih3}",
                    "sebep": f"{sebep}"
                }
            )
            pp = interaction.user.avatar.with_size(64)
            pp2 = uye.avatar.with_size(64)
            blembed = discord.Embed(
                title = "Öneri Black List'e Ekleme İşlem Başarılı",
                description = f"**»** İşlemi Yapan Yetkili: ``{interaction.user}``\n**»** İşlemi Yapan Yetkili ID: ``{interaction.user.id}``\n**»** İşlem Yapılan Üye: ``{uye}``\n**»** İşlem Yapılan Üye ID: ``{uye.id}``\n**»** Sebep: ``{sebep}``",
                colour = discord.Colour.red()
            )
            blembed.set_thumbnail(url=pp2)
            blembed.set_footer(text=f"Yetkili: {interaction.user}   ---   {tarih3}", icon_url=pp)
            await interaction.response.send_message(embed=blembed)
            await log_channel.send(embed=blembed)
        else:
            await interaction.response.send_message("Bilinmeyen bir hata oldu lütfen geliştirici ile iletişime geçiniz")
    else:
        await interaction.response.send_message("Bilinmeyen bir hata oldu lütfen geliştirici ile iletişime geçiniz")


@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel):
        button_label = "Canlı Destek"
        button_url = f"https://discord.com/channels/{server_id}/{destek_kanal_id}"
        if message.author != bot.user:
            LeoDMEmbed = discord.Embed(
                title = f'DM Bilgi',
                description ="``1.`` Yetkili başvurusu hakkında bilgi almak için ``Yetki Bilgi`` Butonuna tıklayınız\n``2.`` İstek/Öneri için ``istek/öneri`` Butonuna tıklayınız\n``3.`` Canlı destek için ``Canlı Destek`` Butonuna tıklayınız\n",
                colour = discord.Colour.blue()
            )
            LeoDMEmbed.set_footer(text=footer)
            view = LeoDM()
            button = discord.ui.Button(style=discord.ButtonStyle.link, label=button_label, url=button_url)
            view.add_item(button)
            await message.channel.send(embed=LeoDMEmbed, view=view)

        await bot.process_commands(message)

@bot.event 
async def on_ready():
    print(f'{bot.user.name}, göreve hazır')
    await bot.change_presence(activity=discord.Game(name=footer))
    try:
        synced = await bot.tree.sync()
        print(f" Entegre edilen slash komut sayısı: {len(synced)}")
    except Exception as a:
        print(a)

bot.run(token)

#LEO4BEY TARAFINDAN YAZILMIŞTIR İZİNSİZ PAYLAŞILMASI YASAKTIR
#https://www.leo4bey.com