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
            data = await self.get_coin_data(symbol, comparison_symbol, exchange)
        else:
            await self.bot.say("\`price only supports single coin lookup, "
                               "please see \`compare for multi-track drifting.")
            data = None
        if data:
            price = data[symbol][comparison_symbol][0]
            c24h = data[symbol][comparison_symbol][1]
            await self.bot.say("Current price of {} is {} ({}%)"
                               .format(symbol.upper(), price, c24h))
        else:
            print('No data.')

    @commands.command(name='compare', pass_context=True)
    async def compare(self, ctx, symbol, comparison_symbol='USD', exchange=''):
        """Multi-coin lookup, slower but prettier than price.
        Usage: symbol can be a list of coins, seperated by a comma.
               comparison_symbol can be a list, also.
               optionally specify an exchange."""
        result = ""
        data = await self.get_coin_data(symbol, comparison_symbol, exchange)

        for fsym, v in data.items():
            result += (fsym.center(30, '-') + '\n')
            for tsym, val in dict(v).items():
                price = val[0].replace('$','USD').replace('£','GBP')                
                pctchange = (val[1] + '%')
                result += ("{}{}\n".format(price.ljust(15),
                                           pctchange.rjust(15)))
        await self.bot.say("```\n" + result + "```")

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
        print(url)
        fsyms = fsyms.split(',')
        tsyms = tsyms.split(',')
        result = {}

        try:
            page = await aiohttp.get(url)
            print(page.text())
            data = await page.json()
            print(data)
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
            
            return result
        except KeyError as e:
            print('KeyError:', e)
            await self.bot.say("KeyError: " + str(e))
            return
        except SyntaxError as e:
            print('SyntaxError:', e)
            await self.bot.say("SyntaxError: " + str(e))
            return
        except Exception as e:
            print(e)
            


def setup(bot):
    if soupAvailable:
        bot.add_cog(CryptoPrice(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
