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
        # Check if these seem like single coins or not
        if symbol.isalnum() and comparison_symbol.isalnum():
            data = await get_coin_data(symbol, comparison_symbol, exchange)
        else:
            await self.bot.say("`price only supports single coin lookup,"
                               "please see `compare for multi-track drifting.")
        if data:
            price = data[symbol][comparison_symbol][0]
            c24h = data[symbol][comparison_symbol][1]
            await self.bot.say("Current price of {} is {} ({}%)"
                               .format(symbol.upper(), price, c24h))

    @commands.command(name='compare', pass_context=True)
    async def compare(self, ctx, symbol, comparison_symbol='USD', exchange=''):
        result = ""
        data = await get_coin_data(symbol, comparison_symbol, exchange)

        for fsym, v in data.items():
            result += (fsym.center(30, '-') + '\n')
            for tsym, val in dict(v).items():
                price = val[0]
                pctchange = (val[1] + '%')
                result += ("{}{}\n".format(price.ljust(15),
                                           pctchange.rjust(15)))
        await self.bot.say("```" + result + "```")

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

    async def get_coin_data(self, fsyms, tsyms, exchange):
        price = ""
        changepct24hour = ""
        url = ("https://min-api.cryptocompare.com"
               "/data/pricemultifull?fsyms={}&tsyms={}"
               .format(fsyms.upper(),
                       tsyms.upper()))
        if exchange:
            url += ('&e={}'.format(exchange))
        fsyms = fsyms.split(',')
        tsyms = tsyms.split(',')
        result = {}

        try:
            page = await aiohttp.get(url)
            data = dict(page.json())
            if 'Response' in data:
                error = data['Message']
                raise KeyError(error)
            elif 'DISPLAY' in data:
                data = data['DISPLAY']
                for fsym in fsyms:
                    coin_data = data[fsym]
                    if fsym not in result:
                        result[fsym] = {}
                    for tsym in tsyms:
                        values = coin_data[tsym]
                        price = values['PRICE']
                        changepct24hour = values['CHANGEPCT24HOUR']
                        result[fsym].update({tsym: [price, changepct24hour]})
        except KeyError as e:
            print('KeyError:', e)
            await self.bot.say("`KeyError: " + str(e))
            return
        except SyntaxError as e:
            print('SyntaxError:', e)
            await self.bot.say("`SyntaxError: " + str(e))
            return


def setup(bot):
    if soupAvailable:
        bot.add_cog(CryptoPrice(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
