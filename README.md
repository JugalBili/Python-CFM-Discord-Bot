# Python - CFM Discord Bot

## Sections 
- [Description](#description)
    - [Features](#features)
    - [Commands](#commands)
- [Getting Started](#getting-started)
    - [Dependencies](#dependencies)
    - [Installing](#installing)
    - [Setting Up](#setting-up)
    - [Executing](#executing)
- [Author](#author)
- [License](#license)

---
## Description
This is a Discord Bot for our CFM University program made using the <span>discord</span>.py API and library. This bot is meant to help the students with time management of multiple courses and provide a way to check upcomming assignments. The data for the assignments of each course along with their respective start and due dates are stored on an MySQL Database and are queried as per the command given by the user. 

This bot is currently being run our CFM university program discord server, for assistance in setting up for your server, please dm me on discord `Xpert104 # 9623`

#### Features
- Daily 9:00 AM reminder for assignments starting and due on the day
- Provides a list of all assignments or by each course
- Provides a list of assignments starting in or due in `x` amount of days

#### Commands
- `!assign <course/'ALL'>`  Displays all assignments of the given course
- `!startin <course/'ALL'> <#_of_days>`  - Displays assignments of the given course which starts within the days given
- `!duein <course/'ALL'> <#_of_days>`  - Displays assignments of the given course which are due within the days given
- `!courses`  - Displays the list of courses

> **Note:** More commands may or may not be added in the future 


---
## Getting Started

### Dependencies/Libraries
- Python >= 3.6.0
- <span>discord</span>.py  == 1.5.1 `pip install discord.py`
- mysql-connector-python == 8.0.22 `pip install mysql-connector-python`
- python-dotenv == 0.15.0 `pip install python-dotenv`
- tabulate == 0.8.7 `pip install tabulate`
- Mac/Windows OS

<br />

### Installing 
```bash
$ git clone https://github.com/JugalBili/Python-CFM-Discord-Bot
```
Or you can download the zip directly from github. 

<br />


### Setting Up
This code will not run without following the set up process stated below. As this program uses the Discord API, you must first get an API token for your bot. A step-by-stp guide is given [here](https://www.writebots.com/discord-bot-token/). 
Since the provate information such as the discord bot token, channel id, ping role id, and database login information are stored as environmental variables, you must first create a `.env` file within the src folder.  

**Variables include the following:**
- DISCORD_TOKEN
- GUILD_ID
- ROLE_ID
- CHANNEL_NAME
- SQL_USER
- SQL_PASS
- SQL_SERVER
- SQL_NAME
- PORT
 > **Note:** Some of these variables may be an integer, but env files can only store strings. So when importing, cast those to an integer.  


<br />


### Executing
To execute to program, open the zip file into an IDE of your choice, or use the following in the termial: 
```bash
python CFM_Bot.py
```
> **Make Sure** to run the command inside the src folder

---
## Author 
**Jugal Bilimoria**
<br />December 21st 2020

<br />Project was made for our CFM University discord server to keep track of assignments and deadlines. 

---
## License 


MIT License

Copyright (c) 2020 Jugal Bilimoria

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.