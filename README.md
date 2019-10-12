# FbLaTeX
A Facebook messenger bot for displaying LaTeX, designed to run on a raspberry pi

## How to use
This bot runs on `fbchat` so you must make your bot its on Facebook account
Clone the package on your raspberry pi and run `python ./FbLaTeX.py/ [EMAIL OF BOT] [PASSWORD OF BOT] [ADMIN FB ID]`. You can get your FB ID from [here](https://findmyfbid.in/). The bot should send the admin account a "Running" message.
To interact with your bot, add it to a group and type "$[LATEX FORMULA]$" or "formula [LATEX FORMULA]" and the bot will respond with a picture of the formula, rendered with [CodeCogs](https://www.codecogs.com/latex/eqneditor.php).

## Debug
If you are using the admin users account you can interact with the bot.
Messaging the bot "You ok?" will cause the bot to respond with "I'm good" to let you know it is still running, sending "Goodnight" will cause the bot to respond with a random 5 character string which, when sent to the bot, will cause it to log off and stop responding. When the bot is sent a python file it will log off and stop responding and start running the new python file, previous versions will be saved in a `./old/` file.
