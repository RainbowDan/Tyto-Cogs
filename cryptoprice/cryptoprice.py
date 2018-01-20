import discord
from discord.ext import commands
from cryptocompy import price
try:  # check if BeautifulSoup4 is installed
    from bs4 import BeautifulSoup
    soupAvailable = True
except:
    soupAvailable = False
import aiohttp
import asyncio


class CryptoPrice:
    """Check price of cryptocurrencies!"""

    def __init__(self, bot):
        self.bot = bot
        self.url = "https://rsihunter.com"

    @commands.command(name='price', pass_context=True)
    async def price(self, ctx, symbol, comparison_symbol='USD', exchange=''):
        """Checks current price of a coin.
        Optionally specify a return currency and exchange."""
        url = ('https://min-api.cryptocompare.com'
               '/data/pricemultifull?fsyms={}&tsyms={}'
               .format(symbol.upper(), comparison_symbol.upper()))
        if exchange:
            url += '&e={}'.format(exchange)
        try:
            page = await aiohttp.get(url)
            data = await page.json()
            if 'DISPLAY' in data:
                p = (data['DISPLAY'][symbol][comparison_symbol]['PRICE']
                     .replace(" ", ""))
                c24h = (data['DISPLAY']
                            [symbol]
                            [comparison_symbol]
                            ['CHANGEPCT24HOUR'])
                await self.bot.say("The current price of {} is {} ({}%)"
                                   .format(symbol, p, c24h))
                # return p, c24h
            elif 'Response' in data:
                error = data['Message']
                raise KeyError(error)
        except KeyError as e:
            await self.bot.say("``" + str(e).strip("'") + "``")
            print('KeyError:', e)

    @commands.command(name='rsi', pass_context=True)
    async def rsi(self, ctx):
        """Grabs top 5 oversold coins from RSIHunter"""
        output = ""
        async with aiohttp.get(self.url) as response:
            soupObject = BeautifulSoup(await response.text(), "html.parser")
        try:
            currencydetails = soupObject.find_all(
                              class_='currency-item coininfo',
                              limit=5)
            for i, coin in enumerate(currencydetails):
                rsi = coin.find(class_='progress').get_text().strip()
                ticker = coin.find_next('h3').get_text()
                output += ("#{} {} -- {}".format(i+1, ticker, rsi) + '\n')
        except:
            await print("error.")
        await self.bot.say('```' + output.strip() + '```')


def setup(bot):
    if soupAvailable:
        bot.add_cog(CryptoPrice(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
