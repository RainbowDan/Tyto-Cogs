import discord
from discord.ext import commands
from cryptocompy import price
try: # check if BeautifulSoup4 is installed
	from bs4 import BeautifulSoup
	soupAvailable = True
except:
	soupAvailable = False
import aiohttp

class CryptoPrice:
	"""Check price of cryptocurrencies!"""

	def __init__(self, bot):
		self.bot = bot
		self.url = "https://rsihunter.com"

	@commands.command(name='price', pass_context=True)
	async def price(self, ctx, coin, returnCurr='USD', ex='all'):
		"""Checks current price and 24hr percentage change of a coin. Optionally specify the return currency and the exchange (eg GDAX)."""
		coin = coin.upper()
		returnCurr = returnCurr.upper()
		#Cryptocompare switches IOTA and IOT for some reason, this just fixes that
		if coin == "IOTA":
			coinSearch = "IOT"
		elif coin == "IOT":
			coinSearch = "IOTA"
		else:
			coinSearch = coin

		#Get dictionary of coin info, then try to get the price (p) and 24hr change (c24h) from the API.
		try:
			print("Trying to get " + coinSearch + " from API")
			dict = price.get_current_price(coinSearch, returnCurr, e=ex, try_conversion=True, full=True, format='display')
			print("Trying to get price from returned JSON")
			p = dict[coinSearch][returnCurr]['PRICE'].replace(" ", "")
			print("Trying to get 24hr change")
			c24h = dict[coinSearch][returnCurr]['CHANGEPCT24HOUR']
			print("Got everything, saying message")
			await self.bot.say("The current price of {} is {} ({}%)".format(coin,p,c24h))
		except KeyError as e:
			print("KeyError. Can't find data!", e)
			await self.bot.say("Something went wrong. Check console log for more information.")
		except TimeoutError as e:
			print("Timeout. API might be slow/down.", e)
			await self.bot.say("Timeout trying to contact cryptocompare API. Might be down/slow. Try again later?")

	@commands.command(name='rsi', pass_context=True)
	async def rsi(self, ctx):
		"""Grabs top 5 oversold coins from RSIHunter"""
		output = ""
		async with aiohttp.get(self.url) as response:
			soupObject = BeautifulSoup(await response.text(), "html.parser")
		try:
			currencydetails = soupObject.find_all(class_='currency-item coininfo', limit=5)
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
