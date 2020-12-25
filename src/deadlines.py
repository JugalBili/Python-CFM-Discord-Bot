from discord.ext import commands 
import discord # pip install discord.py 
import os
from dotenv import load_dotenv # pip install python-dotenv
import mysql.connector # pip install mysql-connector-python
import datetime
from tabulate import tabulate # pip install tabulate
import asyncio


bot = commands.Bot(command_prefix = "!", intents = discord.Intents.default())
reminder_channel = None

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
guild_id = int(os.getenv("GUILD_ID"))
reminder_role = int(os.getenv("ROLE_ID"))
channel_name = os.getenv("CHANNEL_NAME")
user = os.getenv("SQL_USER")
passw= os.getenv("SQL_PASS")
host = os.getenv("SQL_SERVER")
port = int(os.getenv("PORT"))
db = os.getenv("SQL_NAME")

today = datetime.datetime.today()
todayDate = datetime.datetime(year = today.year, month= today.month, day = today.day)
headers = ["Course", "Assignment", "Start Date", "Due Date"]

mydb = mysql.connector.connect(
    host=host,
    database=db,
    user=user,
    password=passw,
    port=port
)
print(mydb)
mycursor = mydb.cursor()


def get_items(command: str, course: str, days: int, day_delta):
    if command.lower() == "startin":
        if course.lower() == "all":
            mycursor.execute(f"SELECT * FROM Deadlines WHERE Deadlines.`Start Date`>='{todayDate}' AND Deadlines.`Start Date`<'{todayDate+day_delta}' ORDER BY Course ASC, `Start Date` ASC")
        else:
            mycursor.execute(f"SELECT * FROM Deadlines WHERE Deadlines.Course='{course.upper()}' AND Deadlines.`Start Date`>='{todayDate}' AND Deadlines.`Start Date`<'{todayDate+day_delta}' ORDER BY Course ASC, `Start Date` ASC")

    if command.lower() == "duein":
        if course.lower() == "all":
            mycursor.execute(f"SELECT * FROM Deadlines WHERE Deadlines.`Due Date`>='{todayDate}' AND Deadlines.`Due Date`<'{todayDate+day_delta}' ORDER BY Course ASC, `Due Date` ASC")
        else:
            mycursor.execute(f"SELECT * FROM Deadlines WHERE Deadlines.Course='{course.upper()}' AND Deadlines.`Due Date`>='{todayDate}' AND Deadlines.`Due Date`<'{todayDate+day_delta}' ORDER BY Course ASC, `Due Date` ASC")
    
    return mycursor.fetchall()



def check_list(results):
    if len(results) == 0:
        return "None ＼(^o^)／"
    else:
        return tabulate(results, headers = headers)

@bot.event 
async def on_ready():
    print("Logged on as {0}!".format(bot))
    print(bot.user)
    global reminder_channel
    
    for channels in (await discord.Guild.fetch_channels(await bot.fetch_guild(guild_id))):
        if channels.name == "bot-reminders":
            reminder_channel = channels.id

    bot.loop.create_task(background_task())


bot.remove_command('help')

@bot.command(name="help")
async def help(ctx):

    if (ctx.message.channel.name == channel_name):

        embed = discord.Embed(
            title = "Help Menu",
            colour = 6282752,
            description = "**There are 3 commands built-in currently:**\n\n"+
            "\t`!assign <course/'ALL'>`  - Displays all assignments of the given course\n\n" +
            "\t`!startin <course/'ALL'> <#_of_days>`  - Displays assignments of the given course which starts within the days given\n\n"+
            "\t`!duein <course/'ALL'> <#_of_days>`  - Displays assignments of the given course which are due within the days given\n\n"+
            "\t`!courses`  - Displays the list of courses\n"
        )

        await ctx.send(embed=embed)


@bot.command(name="courses")
async def courses(ctx):

    if (ctx.message.channel.name == channel_name):

        embed = discord.Embed(
            title = "List of Courses",
            colour = 6673663, 
            description= "- `AFM101`\n- `AFM132`\n- `CS135`\n- `MATH135`\n- `MATH137`"
            )

        await ctx.send(embed=embed)


@bot.command(name="assign")
async def assign(ctx, course: str):
    if (ctx.message.channel.name == channel_name):

        if course.lower() == "all":
            mycursor.execute(f"SELECT * FROM Deadlines ORDER BY Course ASC, `Start Date` ASC")
        else:
            mycursor.execute(f"SELECT * FROM Deadlines WHERE Deadlines.Course='{course.upper()}' ORDER BY Course ASC, `Start Date` ASC")
        
        result= mycursor.fetchall()

        await ctx.send(f"```\n{tabulate(result, headers = headers)}\n```")

    else:
        return


@bot.command(name="duein")
async def due_in(ctx, course: str, days: int):
    if (ctx.message.channel.name == channel_name):
        day_delta = datetime.timedelta(days = days+1)

        result = get_items("duein", course, days, day_delta)
        
        if len(result) == 0:
            await ctx.send(f"```\nThere are no assignments due in {days} days! :smiley:\n```")
        
        else:
            await ctx.send(f"```\n{tabulate(result, headers = headers)}\n```")

    else:
        return


@bot.command(name="startin")
async def start_in(ctx, course: str, days: int):
    if (ctx.message.channel.name == channel_name):
        day_delta = datetime.timedelta(days = days+1)

        result = get_items("startin", course, days, day_delta)

        if len(result) == 0:
            await ctx.send(f"There are no assignments starting in {days} days! :smiley:")
        
        else:
            await ctx.send(f"```\n{tabulate(result, headers = headers)}\n```")

    else:
        return


@assign.error
@start_in.error
@due_in.error
@courses.error
async def errors(ctx, error):
    message = ctx.message.content

    if isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):

        if "!assign" in message: 
            embed = discord.Embed(
                title = "Error", 
                colour = 16718848,
                description = "Please enter a course (or 'ALL')\n`!assign <class/'ALL'>`"
            )
            await ctx.send(embed=embed)

        elif "!startin" in message: 
            embed = discord.Embed(
                title = "Error", 
                colour = 16718848,
                description = "Please enter a course (or 'ALL') and number of days\n`!startin <class/'ALL'> <#_of_days>`"
            )
            await ctx.send(embed=embed)

        elif "!duein" in message: 
            embed = discord.Embed(
                title = "Error", 
                colour = 16718848,
                description = "Please enter a course (or 'ALL') and number of days\n`!duein <class/'ALL'> <#_of_days>`"
            )
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
                title = "Error", 
                colour = 16718848,
                description = "An Error has occured, please try again."
            )
        await ctx.send(embed = embed)



constantTime = datetime.datetime.combine(datetime.date.min, datetime.time(hour = 9, minute= 00, second = 00))
delta = datetime.timedelta(minutes = 5)

async def background_task():
    # use this for actual: old_date = datetime.datetime.now() - datetime.timedelta(days=1)
    # for testing: old_date = datetime.datetime.now() - datetime.timedelta(minutes=1)
    old_date = datetime.datetime.now() - datetime.timedelta(days=1)

    while not bot.is_closed():
        now = datetime.datetime.now()
        min_now = datetime.datetime.combine(datetime.date.min, now.time())
        print(now.time())

        # use this for actual: if (min_now >= (constantTime-delta) and min_now <= (constantTime+delta)) and old_date.day != now.day:
        # for testing: if now.minute%1 == 0  and old_date.minute != now.minute:
        if (min_now >= constantTime and min_now <= (constantTime+delta)) and old_date.day != now.day:
            print("old minute: "+str(old_date.minute) + " Now minute: " + str(now.minute))
            formatted_time = now.strftime("%a, %b %d %Y at %I:%M %p")

            start_result = get_items("startin", "all", 0, datetime.timedelta(days = 1))
            due_result = get_items("duein", "all", 0, datetime.timedelta(days = 1))

            #for testing: await bot.get_channel(reminder_channel).send(f"{formatted_time} : \nTest")
            await bot.get_channel(reminder_channel).send(f"**{formatted_time}**"+
                f"\n\nAssignments Starting Today:\n```{check_list(start_result)}```\nAssignments Due Today:\n```{check_list(due_result)}```<@&{reminder_role}>")
            
            old_date = now
               
        await asyncio.sleep(30)


bot.run(token)