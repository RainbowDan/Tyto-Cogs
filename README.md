# Tyto-Cogs
My custom cogs for Red. Specific to a server I use.
Currently working on the cryptoprice cog.

### ToDo List
- Coin search feature
  - Grab coin list from cryptocompare API as a csv (using pandas)
  - Retrieve data for specified coin from the dataset
  
## Known Issues
- Some coin symbols on cryptocompare don't actually match up with the expected currency, 
e.g BCC should be Bitconnect but returns Bitcoin Core (wtf even is that?)
  - This is a cryptocompare bug that I can't completely eradicate. Search feature 
  should hopefully mitigate the frustration of this, though.
- Just had a big rewrite so likely lots of bugs to quash
