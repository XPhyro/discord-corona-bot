import asyncio
import datetime as dt
import hashlib
import json
from multiprocessing import Queue

import discord

# T#from tweepy import OAuthHandler, Stream, StreamListener

import requests

from config import *
from secrets import *


# T#class TwitterListener(StreamListener):
# T#    def on_data(self, data):
# T#        global q
# T#        q.put(data)
# T#        return True
# T#
# T#    def on_error(self, status):
# T#        print(f"ERROR_TWITTER:\n{self}\n{status}")


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bg_task = self.loop.create_task(self.my_background_task())

    async def on_ready(self):
        print(f"Logged in as\n{self.user.name}\n{self.user.id}\n")

        await self.change_presence(
            activity=discord.Streaming(
                name=DISCORD_PRESENCE_STREAM_NAME, url=DISCORD_PRESENCE_STREAM_URL
            )
        )

    # T#        twitter_listener = TwitterListener()
    # T#
    # T#        twitter_auth = OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    # T#        twitter_auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    # T#
    # T#        twitter_stream = Stream(twitter_auth, twitter_listener)
    # T#        twitter_stream.filter(follow=[TWITTER_ACCOUNT_TO_FOLLOW])

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        if message.content.startswith("!koca"):
            q = str(message.author.mention)
            args = [i.lower().replace("ı", "i") for i in message.content.split()[1:]]
            if len(args) == 0:
                print(f"Messaging {message.author} on {message.channel}.")
                await message.channel.send(f"Ben Dr. Fahrettin Koca {q}.")
                return

            if args[0] == "yardim":
                print(f"Messaging {message.author} on {message.channel}.")
                msg = (
                    f"{q} Değerli vatandaşlarımın benden isteyebilecekleri şunlardır:\n"
                )
                msg += "\n"
                msg += "etiket: Veri paylaşımlarımda sizi etiketlememi, veya zaten etiketliyorsam listeden çıkarmamı sağlar.\n"
                msg += "yardım: Bu yazıyı paylaşmamı sağlar.\n"
                msg += "diğer komutlar: heal/iyileştir\n"
                msg += "\n"
                msg += "İstekler şu şekilde kullanılır: !koca (komut) [seçenek] {argüman} [seçenek] {argüman}..."
                await message.channel.send(msg)
            elif args[0] == "etiket":
                if message.channel.id != DISCORD_CHANNEL_ID:
                    await message.channel.send(
                        f"Bu kanaldan etiket listesine ekleyemem {q}."
                    )
                    return
                with open(MENTIONS_FILENAME, "r") as f:
                    r = f.readlines()
                if q + "\n" in r:
                    print(f"Removing {q} from mention list.")
                    r.remove(q + "\n")
                    with open(MENTIONS_FILENAME, "w+") as f:
                        f.write("".join(r))

                    await message.channel.send(f"Etiket listesinden çıkarıldın {q}.")
                else:
                    print(f"Adding {q} to mention list.")
                    r.append(q + "\n")
                    with open(MENTIONS_FILENAME, "w+") as f:
                        f.write("".join(r))

                    await message.channel.send(f"Etiket listesine eklendin {q}.")
            elif args[0] == "heal" or args[0] == "iyileştir":
                print(f"Messaging {message.author} on {message.channel}.")
                await message.channel.send(
                    f"Bütün sağlık çalışanlarımız gece gündüz, dişini tırnağına takmadan (koronaya yardımcı olur diye), sizler için çalışmakta. Ülkemizin ve dünyanın en yakın zamanda bu korona isimli illetten kurtulmasını, vefat edenlerimize rahmet ve yakınlarınan sabır ve baş sağlığı, hastalarımıza ise şifa diliyorum {q}."
                )
            else:
                print(f"Messaging {message.author} on {message.channel}.")
                await message.channel.send(
                    f"Değerli vatandaşım, lütfen özrümü kabul edin, çünkü dediğinizi anlayamadım {q}."
                )

    async def my_background_task(self):
        await self.wait_until_ready()

        channel = self.get_channel(DISCORD_CHANNEL_ID)
        print(f"Found channel {channel}.")

        while not self.is_closed():
            f = requests.get("https://corona-stats.online/?format=json").text
            j = json.loads(f)
            with open(UPDATE_FILENAME) as uf:
                update = int(uf.readlines()[0])
                uf.close()

            k = []
            for i in j["data"]:
                if i["country"] == "Turkey":
                    k = i
                    break

            if update >= k["updated"]:
                print(f"Old data: {update}\nNew data: {k['updated']}.")
                print("Passing since no new data is avaliable.")
                await asyncio.sleep(600)
                continue
            print(f"Old data: {update}\nNew data: {k['updated']}.")

            update = k["updated"]
            with open(UPDATE_FILENAME, "w+") as uf:
                uf.write(str(update))
                uf.close()
            with open(MENTIONS_FILENAME, "r") as mf:
                mentions = mf.readlines()
            msg = ""
            for i in mentions:
                if msg != "\n":
                    msg += i
            msg += "```"
            msg += "Toplam vaka......: {}\n"
            msg += "Bugünkü vaka.....: {}\n"
            msg += "Toplam ölü.......: {}\n"
            msg += "Bugünkü ölü......: {}\n"
            msg += "Toplam iyileşen..: {}\n"
            msg += "Aktif............: {}\n"
            msg += "Durumu ağır......: {}\n"
            msg += "\n"
            msg += "Güncelleme tarihi: {}"
            msg += "```"
            msg = msg.format(
                k["cases"],
                k["todayCases"],
                k["deaths"],
                k["todayDeaths"],
                k["recovered"],
                k["active"],
                k["critical"],
                dt.datetime.fromtimestamp(update // 1000),
            )
            newIdentifier = msg.splitlines()[-9:-2]
            newIdentifier.pop(3)
            newIdentifier.pop(1)
            newIdentifier = "".join(newIdentifier)

            newHash = hashlib.sha256(newIdentifier.encode("utf-8")).hexdigest()
            with open(HASH_FILENAME, "r") as mif:
                oldHash = mif.read()

            if newHash != oldHash:
                with open(HASH_FILENAME, "w+") as mif:
                    mif.write(newHash)
                print("New hash has been written.")
                await channel.send(msg)
                print(f"Message sent: \n{msg}")
            else:
                print("Passing since hashes are equal.")

            # T#            await asyncio.sleep(60)
            # T#
            # T#            while q.qsize():
            # T#                await channel.send(q.get())

            await asyncio.sleep(5)


# T#q = Queue()

client = MyClient()
client.run(DISCORD_TOKEN)
