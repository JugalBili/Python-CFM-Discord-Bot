from discord.ext import commands 
import discord # pip install discord.py 
import os
from dotenv import load_dotenv # pip install python-dotenv
import mysql.connector # pip install mysql-connector-python
import datetime
from tabulate import tabulate # pip install tabulate
import asyncio
import pytz # pip install pytz

# Initializes the Discord bot and set the command
bot = commands.Bot(command_prefix = "^", intents = discord.Intents.default())
reminder_channel = None

# Loads the contents of the .env file and assigns them to variables 
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
guild_id = int(os.getenv("GUILD_ID"))
reminder_role = int(os.getenv("ROLE_ID"))
reminder_channel = int(os.getenv("REMINDER_CHANNEL_ID"))
channel_name = os.getenv("CHANNEL_NAME")
user = os.getenv("SQL_USER")
passw= os.getenv("SQL_PASS")
host = os.getenv("SQL_SERVER")
port = int(os.getenv("PORT"))
db = os.getenv("SQL_NAME")

tz = pytz.timezone("US/Eastern")
today = (datetime.datetime.now(tz)).date()
todayDate = datetime.datetime(year = today.year, month= today.month, day = today.day)
headers = ["Course", "Assignment", "Start Date", "Due Date"]

# Connects to the MySQL Database 
mydb = mysql.connector.connect(
    host=host,
    database=db,
    user=user,
    password=passw,
    port=port
)
print(mydb)
mycursor = mydb.cursor()


def get_items(command: str, course: str, day_delta):
    """ This function recieves 3 arguments and executes queries in the MySQL Database
    and returns the list results from the query. 

    Arguments: 

    command -- The string section of the command given by the user ('startin' or 'duein')
    course -- The string of the course given with the command (can be 'all')
    day_delta -- A datetime.timedelta object which allows MySQL to return a list of assignments starting/due in the future 

    """

    #reconnects to database if connection is lost
    if(mydb.is_connected()):
        pass
    else:
        mydb.reconnect(attempts = 1, delay=0)

    if command.lower() == "startin":
        if course.lower() == "all":
            mycursor.execute(f"SELECT * FROM Deadlines WHERE Deadlines.`Start Date`>='{todayDate}' AND Deadlines.`Start Date`<'{todayDate+day_delta}' AND Deadlines.Course <> 'Last Ping' ORDER BY `Start Date` ASC")
        else:
            mycursor.execute(f"SELECT * FROM Deadlines WHERE Deadlines.Course='{course.upper()}' AND Deadlines.`Start Date`>='{todayDate}' AND Deadlines.`Start Date`<'{todayDate+day_delta}' AND Deadlines.Course <> 'Last Ping' ORDER BY Course ASC, `Start Date` ASC")

    if command.lower() == "duein":
        if course.lower() == "all":
            mycursor.execute(f"SELECT * FROM Deadlines WHERE Deadlines.`Due Date`>='{todayDate}' AND Deadlines.`Due Date`<'{todayDate+day_delta}' AND Deadlines.Course <> 'Last Ping' ORDER BY `Due Date` ASC")
        else:
            mycursor.execute(f"SELECT * FROM Deadlines WHERE Deadlines.Course='{course.upper()}' AND Deadlines.`Due Date`>='{todayDate}' AND Deadlines.`Due Date`<'{todayDate+day_delta}' AND Deadlines.Course <> 'Last Ping' ORDER BY Course ASC, `Due Date` ASC")
    
    return mycursor.fetchall()



def check_list(results):
    """ This function checks the length of the results array given and returns
    a string if it is empty, or returns a tabulated/formatted chart if not empty.

    Arguments: 

    results -- An array of the values from the queried MySQL database which was performed
    in the above function. 

    """
    if len(results) == 0:
        return "None ＼(^o^)／"
    else:
        return tabulate(results, headers = headers) 

@bot.event 
async def on_ready():
    """ Function is executed when the bot initially connects to the server """

    print("Logged on as {0}!".format(bot))
    print(bot.user)

    # Creates a loop task for the function backcground_task() for the deailt 9 AM reminder feature
    bot.loop.create_task(background_task())


# removes the built-in help command 
bot.remove_command('help')

@bot.command(name="help")
async def help(ctx):
    """ Function is executed when the user enters the help command '!help'. 
    
    Creates and sends a discord Embed object which consists a list of all commands currently present in the bot. 
    """

    if (ctx.message.channel.name == channel_name): # checks to see if the channel is the same as the one specified at the beginning of the file

        embed = discord.Embed(
            title = "Help Menu",
            colour = 6282752,
            description = "**There are 4 commands built-in currently:**\n\n"+
            "\t`^assign <course/'ALL'>`  - Displays all assignments of the given course\n\n" +
            "\t`^startin <course/'ALL'> <#_of_days>`  - Displays assignments of the given course which starts within the days given\n\n"+
            "\t`^duein <course/'ALL'> <#_of_days>`  - Displays assignments of the given course which are due within the days given\n\n"+
            "\t`^courses`  - Displays the list of courses\n\n\n"+
            "For information about the bot, please visit the [github page](https://github.com/JugalBili/Python-CFM-Discord-Bot)"
        )

        await ctx.send(embed=embed) # sends the embed message to the discord channel


@bot.command(name="courses")
async def courses(ctx):
    """ Executed when the user enters the courses command '^courses'.

    Creates and sends a discord Embed object which consists a list of all courses which can be used in other commands. 
    """
    if (ctx.message.channel.name == channel_name):

        embed = discord.Embed(
            title = "List of Courses",
            colour = 6673663, 
            description= "- `AFM101`\n- `AFM132`\n- `CS135`\n- `MATH135`\n- `MATH137`"
            )

        await ctx.send(embed=embed) # sends the embed message to the discord channel


@bot.command(name="assign")
async def assign(ctx, course: str):
    """ Executed when the user enters the assignment command '^assign'.

    Recieves a course as an argument to the command (or 'all') and sends queries the MySQL database to 
    get all entries which match the course entered and sorts it in start date time in ascending order. 

    Argument:

    course -- The string of the course given with the command (can be 'all')

    """
    if (ctx.message.channel.name == channel_name):

        #reconnects to database if connection is lost
        if(mydb.is_connected()):
            pass
        else:
            mydb.reconnect(attempts = 1, delay=0)
            

        if course.lower() == "all":
            mycursor.execute(f"SELECT * FROM Deadlines WHERE Deadlines.Course <> 'Last Ping' ORDER BY Course ASC, `Start Date` ASC")
        else:
            mycursor.execute(f"SELECT * FROM Deadlines WHERE Deadlines.Course='{course.upper()}' ORDER BY Course ASC, `Start Date` ASC")
        
        result= mycursor.fetchall()

        #formats the start and due dates in the result 
        for x in range(len(result)):
            result[x] = list(result[x])
            result[x][2] = result[x][2].strftime("%a, %b %d %Y, %I:%M %p") 
            result[x][3] = result[x][3].strftime("%a, %b %d %Y, %I:%M %p")

        await ctx.send(f"```\n{tabulate(result, headers = headers)}\n```") # sends the tabulated queries to the discord channel

    else:
        return


@bot.command(name="duein")
async def due_in(ctx, course: str, days: int):
    """ Executed when the user enters the due in command '^duein'.

    Recieves a course as an argument to the command (or 'all') and the number of days to check 
    when assignments are due in. It calls the get_items function to sends queries the MySQL database to get all 
    entries which match the entered arguments.

    Arguments:

    course -- The string of the course given with the command (can be 'all')
    days -- Integer of the number of days to check when the assignemnt is due in

    """

    if (ctx.message.channel.name == channel_name):
        day_delta = datetime.timedelta(days = days+1)

        result = get_items("duein", course, day_delta)

        #formats the start and due dates in the result 
        for x in range(len(result)):
            result[x] = list(result[x])
            result[x][2] = result[x][2].strftime("%a, %b %d %Y, %I:%M %p") 
            result[x][3] = result[x][3].strftime("%a, %b %d %Y, %I:%M %p")

        
        # sends a message saying there are no assignments due if the resultant queried database list is empty 
        if len(result) == 0:
            await ctx.send(f"```\nThere are no assignments due in {days} days! :smiley:\n```")
        
        # else sends the tabulated graph of the list 
        else:
            await ctx.send(f"```\n{tabulate(result, headers = headers)}\n```")

    else:
        return


@bot.command(name="startin")
async def start_in(ctx, course: str, days: int):
    """ Executed when the user enters the stat in command '^startin'.

    Recieves a course as an argument to the command (or 'all') and the number of days to check 
    when assignments are starting in. It calls the get_items function to sends queries the MySQL database to get all 
    entries which match the entered arguments.

    Arguments:

    course -- The string of the course given with the command (can be 'all')
    days -- Integer of the number of days to check when the assignemnt is due in

    """

    if (ctx.message.channel.name == channel_name):
        day_delta = datetime.timedelta(days = days+1)

        result = get_items("startin", course, day_delta)

        #formats the start and due dates in the result 
        for x in range(len(result)):
            result[x] = list(result[x])
            result[x][2] = result[x][2].strftime("%a, %b %d %Y, %I:%M %p") 
            result[x][3] = result[x][3].strftime("%a, %b %d %Y, %I:%M %p")

        # sends a message saying there are no assignments starting if the resultant queried database list is empty 
        if len(result) == 0:
            await ctx.send(f"There are no assignments starting in {days} days! :smiley:")
        
        # else sends the tabulated graph of the list 
        else:
            await ctx.send(f"```\n{tabulate(result, headers = headers)}\n```")

    else:
        return


@assign.error
@start_in.error
@due_in.error
@courses.error
async def errors(ctx, error):
    """ This function is only called if an error occures in one of the command functions. 
    
    Sends a embed object specefied message if the error is a BadArgument or MissingRequiredArgumtne error, 
    else sends a general error message. 
    """
    message = ctx.message.content

    if isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):

        if "^assign" in message: 
            embed = discord.Embed(
                title = "Error", 
                colour = 16718848,
                description = "Please enter a course (or 'ALL')\n`^assign <class/'ALL'>`"
            )
            await ctx.send(embed=embed)

        elif "^startin" in message: 
            embed = discord.Embed(
                title = "Error", 
                colour = 16718848,
                description = "Please enter a course (or 'ALL') and number of days\n`^startin <class/'ALL'> <#_of_days>`"
            )
            await ctx.send(embed=embed)

        elif "^duein" in message: 
            embed = discord.Embed(
                title = "Error", 
                colour = 16718848,
                description = "Please enter a course (or 'ALL') and number of days\n`^duein <class/'ALL'> <#_of_days>`"
            )
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
                title = "Error", 
                colour = 16718848,
                description = "An Error has occured, please try again."
            )
        await ctx.send(embed = embed)


# constant time datetime object which sets the time when to send the reminder
constantTime = datetime.datetime.combine(datetime.date.min, datetime.time(hour = 9, minute= 00, second = 00), tz)
delta = datetime.timedelta(minutes = 5) # timedelta object which essentially acts as a 5 minute error to the reminder

async def background_task():
    """ This task is the background task which enables the dailt 9 AM reminders to work. """

    # use this for actual: old_date = datetime.datetime.now() - datetime.timedelta(days=1)
    # for testing: old_date = datetime.datetime.now() - datetime.timedelta(minutes=1)
    old_date = old_date = datetime.datetime.now() - datetime.timedelta(days=1)
    
    while not bot.is_closed():
        now = datetime.datetime.now(tz)
        min_now = datetime.datetime.combine(datetime.date.min, now.time(), tz)
        #print(now.time())

        # use this for actual: if (min_now >= constantTime and min_now <= (constantTime+delta)) and old_date.day != now.day:
        # for testing: if now.minute%1 == 0  and old_date.minute != now.minute:

        # if the current time is >= than the constantTime set and <= to the constantTime + the 5 minuet delta 
        #     and the date fo the rpevious reminder is the day before, it sends a reminder to the chat
        if (min_now >= constantTime and min_now <= (constantTime+delta)) and old_date.day != now.day:
            print("old minute: "+str(old_date.minute) + " Now minute: " + str(now.minute))
            formatted_time = now.strftime("%a, %b %d %Y at %I:%M %p")

            start_result = get_items("startin", "all", datetime.timedelta(days = 1))
            due_result = get_items("duein", "all", datetime.timedelta(days = 1))

            #formats the start and due dates in the result 
            for x in range(len(start_result)):
                start_result[x] = list(start_result[x])
                start_result[x][2] = start_result[x][2].strftime("%a, %b %d %Y, %I:%M %p") 
                start_result[x][3] = start_result[x][3].strftime("%a, %b %d %Y, %I:%M %p")

            #formats the start and due dates in the result 
            for x in range(len(due_result)):
                due_result[x] = list(due_result[x])
                due_result[x][2] = due_result[x][2].strftime("%a, %b %d %Y, %I:%M %p") 
                due_result[x][3] = due_result[x][3].strftime("%a, %b %d %Y, %I:%M %p")

            #for testing: await bot.get_channel(reminder_channel).send(f"{formatted_time} : \nTest")

            await bot.get_channel(reminder_channel).send(f"**{formatted_time}**"+
                f"\n\nAssignments Starting Today:\n```{check_list(start_result)}```\nAssignments Due Today:\n```{check_list(due_result)}```<@&{reminder_role}>\n\n")


            # the following updates the 'last ping' row in the database
                # this is only to make sure the database does not get deactivated due to inactivity of writing to database
            mycursor.execute("SELECT * FROM Deadlines WHERE Deadlines.Course='Last Ping'")
            result= mycursor.fetchall()

            toAdd = "INSERT INTO Deadlines (Course, `Start Date`) VALUES (%s, %s)"
            values = ("Last Ping", now)

            if len(result) == 0: 
                mycursor.execute(toAdd, values)
                mydb.commit()
                print("'Last Ping' Row was updated")

            else:
                mycursor.execute(f"DELETE FROM Deadlines WHERE Course = 'Last Ping'")
                mydb.commit()

                mycursor.execute(toAdd, values)
                mydb.commit()
                print("'Last Ping' Row was updated")

            old_date = now
               
        await asyncio.sleep(30) #loops every 30 seconds


# runs the bot loop given the the bot api token 
bot.run(token)
