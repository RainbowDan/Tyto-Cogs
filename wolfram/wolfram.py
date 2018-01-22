from .utils.dataIO import dataIO
import discord
from discord.ext import commands
import aiohttp
import urllib
import os
from .utils import checks


class Wolfram:
    """Probe Wolfram|Alpha for answers."""

    def __init__(self, bot):
        self.bot = bot
        self.settings_file = 'data/wolfram/wolfram.json'
        self.settings = dataIO.load_json(self.settings_file)

    @commands.command(name="wolfram", aliases=['wa'], pass_context=True)
    async def wolfram(self, ctx, *, query):
        """Searches wolfram|alpha for answers"""

        if self.settings['WOLFRAM_API_KEY']:
            query = urllib.parse.quote(query)
            apikey = self.settings['WOLFRAM_API_KEY']
            rurl = ("https://api.wolframalpha.com/v1/result?i={}&appid={}"
                    .format(query, apikey))

            async with aiohttp.get(rurl) as response:
                result = await response.text()
            response = str(result)
            await self.bot.say('```fix\n{}```'.format(response))
        else:
            message = ('No API key set! Please get one from '
                       'https://products.wolframalpha.com/api/')
            await self.bot.say('```{}```'.format(message))

    @commands.command(name='wolframapikey', pass_context=True)
    @checks.is_owner()
    async def wolframapikey(self, ctx, apikey):
        """Set API key from https://products.wolframalpha.com/api/"""
        self.settings['WOLFRAM_API_KEY'] = apikey
        dataIO.save_json(self.settings_file, self.settings)
        await self.bot.say('Key saved!')


def check_folder():
    if not os.path.exists("data/wolfram"):
        print("Creating data/wolfram folder...")
        os.makedirs("data/wolfram")


def check_file():
    wolfram = {}
    wolfram['WOLFRAM_API_KEY'] = False
    f = "data/wolfram/wolfram.json"
    if not dataIO.is_valid_json(f):
        print("Creating default wolfram.json...")
        dataIO.save_json(f, wolfram)


def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(Wolfram(bot))
