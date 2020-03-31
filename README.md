# discord-corona-bot

A bot that regularly checks COVID-19 statistics and sends them to a specific discord channel.

# Usage

Fill the constants in [secrets-example.py](secrets-example.py) and rename it to *secrets.py*, then run [main.py](main.py). 

The script does not check whether the needed files exist; therefore, you should have the files beforehand. If they are not there, be sure to create the files that are defined as constants in [main.py](main.py). Also make sure that the content of UPDATE_FILENAME is "0" for your first initialisation (i.e. run this: echo 0 > update).

# Requisites

This bot was written using Python 3.8.2.

You should also have installed these libraries:

  Library   | Version
|-----------|-------|
| [discord.py](https://github.com/Rapptz/discord.py) | 1.3.2 |
| requests | 2.23.0 |
