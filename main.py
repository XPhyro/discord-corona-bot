import datetime as dt
import hashlib
import discord
import asyncio
import json
import requests
from secrets import *


MENTIONS_FILENAME = "mentions"
UPDATE_FILENAME = "update"
HASH_FILENAME = "hash"


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bg_task = self.loop.create_task(self.my_background_task())


    async def on_ready(self):
        print(f"Logged in as\n{self.user.name}\n{self.user.id}\n")
    

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith("!koca"):
            q = str(message.author.mention)
            if "mention" in message.content:
                if message.channel.id != DISCORD_CHANNEL_ID:
                    await message.channel.send(f"Bu kanaldan mention listesine ekleyemem {q}.")
                    return
                with open(MENTIONS_FILENAME, "r") as f:
                    r = f.readlines()
                if q + "\n" in r:
                    print(f"Removing {q} from mention list.")
                    r.remove(q + "\n")
                    with open(MENTIONS_FILENAME, "w+") as f:
                        f.write("".join(r))

                    await message.channel.send(f"Mention listesinden çıkarıldın {q}.")
                else:
                    print(f"Adding {q} to mention list.")
                    r.append(q + "\n")
                    with open(MENTIONS_FILENAME, "w+") as f:
                        f.write("".join(r))

                    await message.channel.send(f"Mention listesine eklendin {q}.")
            else:
                print(f"Messaging {message.author} on {message.channel}.")
                await message.channel.send(f"Ben Dr. Fahrettin Koca {q}.")

    
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

            k = j["data"][11]
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
                    dt.datetime.fromtimestamp(update // 1000)
            )
            newIdentifier = "".join(msg.splitlines()[-9:-2])
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
            
            await asyncio.sleep(5)


client = MyClient()
try:
    client.run(DISCORD_TOKEN)
except discord.HTTPException as e:
    r = e.response
    for i in r:
        print(i)
