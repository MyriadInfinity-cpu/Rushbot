import asyncio
import discord
from datetime import datetime

from Random_Helpers import *
from SheetUpdate import *

intents = discord.Intents.default()
intents.message_content = True

client = discord.Bot(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    game = discord.Game("$rush help")
    await client.change_presence(status=discord.Status.idle, activity=game)
    await client.sync_commands()

@client.event
async def on_message(message):
    if message.author == client.user: # ignore own messages
        return
    if message.content.startswith('$rush help'):
        output = await help_txt()
        await send_response(output, message.channel)
    elif message.content.startswith('$rush'): # respond to commands only
        output = await handle_command(message.content)
        await send_response(output, message.channel)

def sum_numbers(input_string):
    total = 0
    current_number = ''
    current_sign = 1  # 1 for positive, -1 for negative

    for char in input_string:
        if char.isdigit():
            current_number += char
        else:
            if current_number:
                total += current_sign * int(current_number)
                current_number = ''
            if char == '+':
                current_sign = 1
            elif char == '-':
                current_sign = -1

    if current_number:
        total += current_sign * int(current_number)
    print(f"{input_string} produced {total}")
    return total

async def handle_command(inp):
    try:
        lines = inp.splitlines()  # Split message into lines

        if not lines:
            return "Error: message is empty."

        first_line = lines[0].strip()
        
        # differentiate between commands with and without bonuses
        if not first_line.startswith('$rush hustle'):
            plus_location = -1
            plus_location = first_line.find('+')
            try:
                bonus = sum_numbers(first_line[plus_location+1:])
            except ValueError:
                return "Error: bonus not found. Please use '$rush help' for formatting instructions."
        
        message_body = "\n".join(lines[1:])

        # Routing the command
        out = ""
        if first_line.startswith('$rush fixerdeal'):
            out = await fixer_deal(message_body, bonus)
        elif first_line.startswith('$rush salvage'):
            out = await salvage_txt(first_line, bonus)
        elif first_line.startswith('$rush therapy'):
            out = await therapy_txt(first_line, bonus)
        elif first_line.startswith('$rush hustle'):
            out = await hustle_txt(first_line)
        elif first_line.startswith('$rush help'):
            out = await help_txt()
        return out
    except Exception as e:
        return "An error occurred. Please use `$rush help` for formatting guidelines. If you believe this is a bug, I'm Myriad (myriad2223)'s problem child, feel free to ping him to poke him about it. Here's the error that occurred:" + str(e)

async def fixer_deal(inp, bonus): # inp is the message body, bonus is the fixer bonus
    # Extract information as objects
    outp = ""
    total_cost = 0
    total_value = 0
    total_sale_price = 0
    total_sale_cost = 0
    deals = 1
    lines = inp.splitlines()
    for line in lines:
        newLine = reformat(line)
        deal = OneDeal.helper(newLine)
        deal.roll_it(bonus)
        print(deal.ret())
        outp += "**Deal " + str(deals) + ":** " + deal.ret()[0] + "\n"
        total_cost += deal.ret()[1]
        total_value += deal.ret()[2]
        total_sale_price += deal.ret()[3]
        total_sale_cost += deal.ret()[4]
        deals = deals+1
    outp += f"Total cost: {total_cost}eb, Total value: {total_value}eb. You saved {total_value-total_cost}eb today.\n"
    if total_sale_price != 0:
        outp += f"Total sale price: {total_sale_price}eb, Total sale cost: {total_sale_cost}eb. You profited {total_sale_price-total_sale_cost}eb today.\n"
        outp += f"Your total balance change is {total_sale_price-total_cost}eb."
    return outp

def reformat(inp):
    # reformat price categories, bonus, prices
    # input data is i.e. "6f5 100eb premium", "10% 10x 100eb Premium"
    parts = inp.split(" ")

    print("Scrubbing input for deal ")
    print(parts)
    if inp.startswith("6f5"):
        return f"6f5 {scrubCash(parts[1])} {scrubCategory(parts[2])}"
    elif inp.lower().startswith("sell"):
        return f"sell {parts[1]} {scrubQuantity(parts[2])} {scrubCash(parts[3])} {scrubCategory(parts[4])}"
    elif inp.lower().startswith("buy"):
        return f"buy {parts[1]} {scrubQuantity(parts[2])} {scrubCash(parts[3])} {scrubCategory(parts[4])}"
    else:
        return f"{parts[0]} {scrubQuantity(parts[1])} {scrubCash(parts[2])} {scrubCategory(parts[3])}"

def scrubCash(inp):
    # Scrub cash from the input, i.e. "100eb" -> 100
    return int(inp[:-2])

def scrubQuantity(inp):
    # Scrub quantity from the input, i.e. "10x" -> 10
    return int(inp[:-1])

def scrubCategory(inp):
    # Properly capitalise the category, i.e. "premium" -> "Premium"
    print("Scrubbing category: " + inp)
    if "everyday" in inp.lower():
        return "Everyday"
    elif "very" in inp.lower():
        return "Very_Expensive"
    elif "super" in inp.lower():
        return "Super_Luxury"
    elif "cheap" in inp.lower():
        return "Cheap"
    elif "everyday" in inp.lower():
        return "Everyday"
    elif "costly" in inp.lower():
        return "Costly"
    elif "premium" in inp.lower():
        return "Premium"
    elif "expensive" in inp.lower():
        return "Expensive"
    elif "luxury" in inp.lower():
        return "Luxury"
    else:
        return "Error: category not recognised."

async def salvage_txt(line, bonus):
    if "any" in line.lower():
        cat_value = random.randint(1, 6)
        # cat_value = 1
        cat = ""
        if cat_value == 1:
            cat = "Cyberware"
        elif cat_value == 2:
            cat = "Weapons"
        elif cat_value in [3, 4]:
            cat = "General Gear"
        elif cat_value == 5:
            cat = "Armour"
        elif cat_value == 6:
            cat = "Cyberdecks/Programs"

        roll = DiceRoller.roll_d10_crit()
        roll2 = roll[1]+bonus
        return f"You rolled `d10 ({roll[0]}) + {bonus} = {roll[1]+bonus}` and find {salvage_lookup_any(roll2)} of `d6 ({cat_value})` {cat}."
    elif "specific" in line.lower():
        roll = DiceRoller.roll_d10_crit()
        roll2 = roll[1]+bonus
        return f"You rolled `d10 ({roll[0]}) + {bonus} = {roll[1]+bonus}` and find {salvage_lookup_specific(roll2)} of your chosen category."
    return "Please pick a category (use `$rush help` for formatting guidelines)."

def salvage_lookup_any(inp): #inp is the total roll
    if inp > 29:
        return "1000eb"
    elif inp > 24:
        return "500eb"
    elif inp > 17:
        return "100eb"
    elif inp > 15:
        return "50eb"
    elif inp > 13:
        return "20eb"
    elif inp > 9:
        return "10eb"
    # Salvage anything
    return "Error occurred. Please contact Myriad."

def salvage_lookup_specific(inp):
    # Salvage specific
    if inp > 29:
        return "500eb"
    elif inp > 24:
        return "100eb"
    elif inp > 17:
        return "50eb"
    elif inp > 15:
        return "20eb"
    elif inp > 13:
        return "10eb"
    else:
        return "Error occurred. Please contact Myriad."

async def therapy_txt(line, bonus):
    if "standard" in line.lower():
        roll = DiceRoller.roll_d10_crit()
        if (roll[1] + bonus) > 15:
            return f"Roll: d10 ({roll[0]}) + {bonus} = {roll[1]+bonus} vs. DV15 :white_check_mark:"
        else:
            return f"Roll: d10 ({roll[0]}) + {bonus} = {roll[1]+bonus} vs. DV15 :no_entry:\n-# Make sure your bonus is i.e. `+12+4`, not just `12+4`."
    elif "extreme" in line.lower():
        roll = DiceRoller.roll_d10_crit()
        if (roll[1] + bonus) > 17:
            return f"Roll: d10 ({roll[0]}) + {bonus} = {roll[1]+bonus} vs. DV17 :white_check_mark:"
        else:
            return f"Roll: d10 ({roll[0]}) + {bonus} = {roll[1]+bonus} vs. DV17 :no_entry:\n-# Make sure your bonus is i.e. `+12+4`, not just `12+4`."
    else:
        return "No category specified. Please use `$rush help` for syntax."
    
async def help_txt():
    return "Hello! I'm Rushbot, and I'm here to help you with fixer deals, tech jobs, hustles, salvaging, and therapy. Here's how you can use me:\n\n" \
           "**Fixer Deal:**\n" \
           "```$rush fixerdeal +14+4\n" \
           "sell 10% 2x 500eb expensive\n" \
           "6f5 100eb premium\n" \
           "10% 10x 100eb Premium\n" \
           "```\n" \
           "**Salvage (also available via slash command /salvage):**\n" \
           "- `$rush salvage any +14+8`\n" \
           "- `$rush salvage specific +14+6`\n" \
           "**Therapy (also available via slash command /therapy):**\n" \
           "- `$rush therapy standard +12+5`\n" \
           "- `$rush therapy extreme +17`\n" \
           "**Hustle (also available via slash command /hustle):**\n" \
           "- `$rush hustle solo 4`\n" \
           "- `$rush hustle netrunner 8`\n" \
           "**Slash Commands:**\n" \
           "I have slash commands for the aforementioned Salvage, Therapy, and Hustle, as well as Tech jobs (Fabricate, Upgrade, Repair)." \
           "If you have any more questions or feature suggestions, I'm the problem child of Myriad (@myriad2223). Feel free to bother him.\n\n" \
           "Note: Slash commands for individual Fixer deals and inference for larger ones are next on the docket unless someone has a *really* banger idea for something better to do first."

async def hustle_txt(inp): # Rolls a d6, sets reward based on the roll and the role + rank
    # role, roll, rank
    inp = inp[len("$rush hustle "):]# sanitise input

    lookup = hustle_role_lookup(inp)
    print(lookup)
    role = lookup[0]
    rank = lookup[1]

    if role == -1 | rank == -1:
        return "An error occurred. Please use `$rush help` for formatting instructions."
    roll = random.randint(1, 6)

    arr = get_hustles()
    inp = inp.capitalize()
    print(f"Arguments for arr: [{role}][{roll-1}][{rank}]")
    return f"Roll: 1d6 ({roll}) for a {inp}: {arr[role][roll-1][rank]}eb."

def get_hustles():
    array_hustles = [
        [ # Rockerboy
            [200, 300, 600],
            [0, 100, 300],
            [300, 500, 800],
            [300, 500, 800],
            [300, 500, 800],
            [200, 300, 600]
        ],
        [ # Solo
            [100, 200, 500],
            [200, 300, 600],
            [200, 300, 600],
            [100, 200, 500],
            [0, 100, 300],
            [100, 200, 500]
        ],
        [ # Netrunner
            [100, 200, 500],
            [200, 300, 600],
            [0, 100, 300],
            [200, 300, 600],
            [200, 300, 600],
            [200, 300, 600]
        ],
        [ # Tech
            [0, 100, 300],
            [100, 200, 500],
            [200, 300, 600],
            [100, 200, 500],
            [100, 200, 500],
            [100, 200, 500]
        ],
        [ # Medtech
            [100, 200, 500],
            [200, 300, 600],
            [100, 200, 500],
            [0, 100, 300],
            [200, 300, 600],
            [100, 200, 500]
        ],
        [ # Media
            [300, 500, 800],
            [200, 300, 600],
            [200, 300, 600],
            [200, 300, 600],
            [0, 100, 300],
            [300, 500, 800]
        ],
        [ # Lawman
            [100, 200, 500],
            [200, 300, 600],
            [0, 100, 300],
            [100, 200, 500],
            [200, 300, 600],
            [200, 300, 600]
        ],
        [ # Exec
            [300, 500, 800],
            [0, 100, 300],
            [200, 300, 600],
            [300, 500, 800],
            [300, 500, 800],
            [200, 300, 600]
        ],
        [ # Fixer
            [200, 300, 600],
            [200, 300, 600],
            [200, 300, 600],
            [0, 100, 300],
            [200, 300, 600],
            [300, 500, 800]
        ],
        [ # Nomad
            [100, 200, 500],
            [100, 200, 500],
            [100, 200, 500],
            [200, 300, 600],
            [100, 200, 500],
            [0, 100, 300]
        ]
    ]
    return array_hustles

def hustle_role_lookup(inp): # inp is a string now btw, i.e. "netrunner 8"
    inp = inp.lower()
    print(inp)
    rank = -1 # find the role rank
    for char in inp:
        if char.isdigit():
            rank = int(char)

    role = -1 # find what role they are
    if inp.startswith("rockerboy"):
        role = 0
    elif inp.startswith("solo"):
        role = 1
    elif inp.startswith("netrunner"):
        role = 2
    elif inp.startswith("tech"):
        role = 3
    elif inp.startswith("medtech"):
        role = 4
    elif inp.startswith("media"):
        role = 5
    elif inp.startswith("lawman"):
        role = 6
    elif inp.startswith("exec"):
        role = 7
    elif inp.startswith("fixer"):
        role = 8
    elif inp.startswith("nomad"):
        role = 9
    
    if role == -1 or rank == -1:
        return (-1, -1)

    return (role, hustle_rank_lookup(rank))

def hustle_rank_lookup(inp):
    if 1 <= inp <= 4:
        return 0
    elif 5 <= inp <= 7:
        return 1
    elif 8 <= inp <= 10:
        return 2
    else:
        return -1

async def send_response(inp, channel):
    await channel.send(inp)

# Slash command functions below
@client.command(description="Rolls a hustle")
async def hustle(
    ctx: discord.ApplicationContext, 
    role: discord.Option(str, choices=["Rockerboy", "Solo", "Netrunner", "Tech", "Medtech", "Media", "Lawman", "Exec", "Fixer", "Nomad"]),
    rank: int):
    await ctx.respond(await hustle_txt(f"$rush hustle {role} {rank}"))

@client.command(description="Rolls therapy")
async def therapy(
    ctx: discord.ApplicationContext,
    category: discord.Option(str, choices=["Standard", "Extreme"]),
    bonus: discord.Option(int, description="Total Medical Tech skill base after CPS-23 but before LUCK"),
    luck: discord.Option(int, description="How much LUCK you're spending", required=False)):
    await ctx.respond(await therapy_txt(f"$rush therapy {category} +{bonus}+{luck}", (bonus+luck)))

@client.command(description="Rolls salvage")
async def salvage(
    ctx: discord.ApplicationContext,
    category: discord.Option(str, choices=["Any", "Specific"]),
    bonus: discord.Option(int, description="Total Basic Tech skill base (including Field Expertise but not LUCK)"),
    luck: discord.Option(int, description="How much LUCK you're spending", required=False)):
    await ctx.respond(await salvage_txt(f"$rush salvage {category} +{bonus}+{luck}", (bonus+luck)))

tech_jobs = client.create_group("tech", "Tech-related commands")

@tech_jobs.command(description="Rolls a fabrication job")
async def fabricate(
    ctx: discord.ApplicationContext,
    category: discord.Option(str, description="Price category of fabricated item", choices=["Cheap", "Everyday", "Costly", "Premium", "Expensive", "Very Expensive", "Luxury", "Super Luxury"]),
    bonus: discord.Option(int, description="Skill base without LUCK or Maker bonuses"),
    fabricate_ranks: discord.Option(int, description="Points in Fabrication Expertise Maker specialty"),
    luck: discord.Option(int, description="How much LUCK you're spending", required=False)):
    category_dv = lookup_tech_category_dv(category)
    roll = DiceRoller.roll_d10_crit()
    bonus_total = bonus+luck+fabricate_ranks
    total_roll = roll[1]+bonus_total
    out = ""
    if (total_roll) > category_dv:
        out = f"Roll: d10 ({roll[0]}) + {bonus_total} = {total_roll} vs. DV{category_dv} :white_check_mark:"
    else:
        out = f"Roll: d10 ({roll[0]}) + {bonus_total} = {total_roll} vs. DV{category_dv} :no_entry:"
    await ctx.respond(out)
@tech_jobs.command(description="Rolls an upgrade job")
async def upgrade(
    ctx: discord.ApplicationContext,
    category: discord.Option(str, description="Price category of upgraded item", choices=["Cheap", "Everyday", "Costly", "Premium", "Expensive", "Very Expensive", "Luxury", "Super Luxury"]),
    bonus: discord.Option(int, description="Skill base without LUCK or Maker bonuses"),
    upgrade_ranks: discord.Option(int, description="Points in Upgrade Expertise Maker specialty"),
    luck: discord.Option(int, description="How much LUCK you're spending", required=False)):
    category_dv = lookup_tech_category_dv(category)
    roll = DiceRoller.roll_d10_crit()
    bonus_total = bonus+luck+upgrade_ranks
    total_roll = roll[1]+bonus_total
    out = ""
    if (total_roll) > category_dv:
        out = f"Roll: d10 ({roll[0]}) + {bonus_total} = {total_roll} vs. DV{category_dv} :white_check_mark:"
    else:
        out = f"Roll: d10 ({roll[0]}) + {bonus_total} = {total_roll} vs. DV{category_dv} :no_entry:"
    await ctx.respond(out)
@tech_jobs.command(description="Rolls a repair job")
async def repair(
    ctx: discord.ApplicationContext,
    category: discord.Option(str, description="Price category of repaired item", choices=["Cheap", "Everyday", "Costly", "Premium", "Expensive", "Very Expensive", "Luxury", "Super Luxury"]),
    bonus: discord.Option(int, description="Skill base without LUCK or Maker bonuses"),
    field_expertise_ranks: discord.Option(int, description="Points in Field Expertise Maker specialty"),
    luck: discord.Option(int, description="How much LUCK you're spending", required=False)):
    category_dv = lookup_tech_category_dv(category)
    roll = DiceRoller.roll_d10_crit()
    bonus_total = bonus+luck+field_expertise_ranks
    total_roll = roll[1]+bonus_total
    out = ""
    if (total_roll) > category_dv:
        out = f"Roll: d10 ({roll[0]}) + {bonus_total} = {total_roll} vs. DV{category_dv} :white_check_mark:"
    else:
        out = f"Roll: d10 ({roll[0]}) + {bonus_total} = {total_roll} vs. DV{category_dv} :no_entry:"
    await ctx.respond(out)

@client.command(description="Rolls pharmaceutical creation")
async def pharma(
    ctx: discord.ApplicationContext,
    tech: discord.Option(int, description="Your TECH stat"),
    medical_tech: discord.Option(int, description="Your total points in Medical Tech (i.e. Pharma + Cryo)"),
    luck: discord.Option(int, description="How much LUCK you're spending", required=False)):
    dv = 13
    roll = DiceRoller.roll_d10_crit()
    bonus_total = tech+medical_tech+luck
    total_roll = roll[1]+bonus_total
    out = ""
    if (total_roll) > dv:
        out = f"Roll: d10 ({roll[0]}) + {bonus_total} = {total_roll} vs. DV{dv} :white_check_mark:\n"
        out = out + f"You make {medical_tech} doses of pharmaceuticals."
    else:
        out = f"Roll: d10 ({roll[0]}) + {bonus_total} = {total_roll} vs. DV{dv} :no_entry:"
    await ctx.respond(out)

def lookup_tech_category_dv(category):
    if category == "Cheap":
        return 9
    elif category == "Everyday":
        return 9
    elif category == "Costly":
        return 13
    elif category == "Premium": 
        return 17
    elif category == "Expensive":
        return 21
    elif category == "Very Expensive":
        return 24
    elif category == "Luxury":
        return 29
    elif category == "Super_Luxury":
        return 29
    else:
        return -1
    
@client.command(description="Rolls a d10 with bonuses, which explode as in CPR.")
async def roll_cpr(
    ctx: discord.ApplicationContext,
    str: discord.Option(str, description="Input i.e. '5 +14+2' (always rolls a d10, no spaces)"),
    opposition: discord.Option(str, description="Roll against something. Flat number = DV, bonus i.e. +12 = opposed roll", required=False),
    comment: discord.Option(str, description="Optional comment", required=False)):

    out = ""
    bonus = -1
    parts = str.split(" ")
    if len(parts) == 1: # if its just one, only roll once
        multi = False
        pos = parts[0].find('+')
        pos2 = parts[0].find('-')
        if pos != -1 and pos2 != -1:
            if pos > pos2:
                pos = pos2
        elif pos == -1 and pos2 != -1:
            pos = pos2
        bonus = sum_numbers(parts[0][pos:])
    elif len(parts) != 2: # if it aint 1 its gotta be 2
        out = "Error. Please format the main input with no spaces aside from the one between quantity and roll (if any), i.e. '5 1d10+14+2'."
    else:
        multi = True
        if "x" in parts[0]: # catching "5x <roll>" rather than "5 <roll>"
            parts[0] = parts[0].replace("x", "")
        pos = parts[1].find('+')
        pos2 = parts[1].find('-')
        if pos != -1 and pos2 != -1:
            if pos > pos2:
                pos = pos2
        elif pos == -1 and pos2 != -1:
            pos = pos2
        bonus = sum_numbers(parts[1][pos:])
    
    if multi:
        repeats = int(parts[0])
    else: 
        repeats = 1
    
    for i in range(repeats):
        if opposition and '+' in opposition: # rolling against an opposed roll
            opp_bonus = sum_numbers(opposition[opposition.find('+')+1:])
            roll = DiceRoller.roll_d10_crit()
            opp_roll = DiceRoller.roll_d10_crit()
            out = out + f"{i}. You: `d10 ({roll[0]}) + {bonus} = {roll[1]+bonus}` vs. Opponent: `d10 ({opp_roll[0]}) + {opp_bonus} = {opp_roll[1]+opp_bonus}`"
            if (roll[1]+bonus) > (opp_roll[1]+opp_bonus):
                out += " :white_check_mark:\n"
            else:
                out += " :no_entry:\n"
        elif opposition: # rolling against a flat number
            opp = int(opposition)
            roll = DiceRoller.roll_d10_crit()
            out = out + f"{i}. You: `d10 ({roll[0]}) + {bonus} = {roll[1]+bonus}` vs. DV{opp}"
            if (roll[1]+bonus) > opp:
                out += " :white_check_mark:\n"
            else:
                out += " :no_entry:\n"
        else: # just a normal roll
            print("1")
            roll = DiceRoller.roll_d10_crit()
            out = out + f"{i}. You: `d10 ({roll[0]}) + {bonus} = {roll[1]+bonus}`\n"
    if comment:
        out = out + f"\nComment: {comment}"
    print(out)
    await ctx.respond(out)

@client.command(description="COMMAND IN TESTING", guild_ids=[YOUR GUILD IDS HERE])
async def sheet_update_for_thread(ctx: discord.ApplicationContext,
    gig_name: discord.Option(str, description="The name of the gig."),
    eb: discord.Option(int, description="The eurodollar reward.", required=False),
    ip: discord.Option(int, description="The IP reward.", required=False),
    date: discord.Option(str, description="MM/DD/YYYY i.e. 3/20/2025", required=False),
    tags: discord.Option(str, description="i.e. \"fix,event\"", required=False),
    ):
    eb = eb if eb else 0
    ip = ip if ip else 0
    date = date if date else 1/1/1970
    tags = tags if tags else "None"

    command_author = ctx.author
    print(command_author)
    print("Starting game application process")
    await ctx.respond("Applications are being loaded in. Please hold...", ephemeral=True)
    if any(role.name == "Chargen Staff" for role in ctx.author.roles):
        print("Authorised, user is Chargen Staff")
    elif any(role.name == "World Team" for role in ctx.author.roles):
        print("Authorised, user is World Team")
    else:
        print("Not authorised")
        await ctx.respond("You are not authorised to use this command, you silly goose.", ephemeral=True)
    
    channel_id = ctx.channel_id
    channel = client.get_channel(channel_id)
    channel_name = channel.name
    thread_author = channel.owner_id

    to_apply = []

    messages = await channel.history(limit=2000).flatten()
    messages = messages[::-1]

    print("Adding game to sheet")
    print(gig_name, get_user_name_by_discord_id(thread_author), "Complete", date, eb, ip, tags)
    add_game(gig_name, get_user_name_by_discord_id(thread_author), "Complete", date, eb, ip, tags)
    for message in messages:
        if "http" not in message.content:
            continue
        # print(f"{message.author.id} / {message.author.name} at {message.created_at.strftime('%d/%m/%Y, %H:%M:%S')}:")
        # print(message.content)

        author = get_user_name_by_discord_id(message.author.id)
        # print("Author: "+author)
        characters_of_message_owner = get_one_user_active_characters_by_name(author)
        character_names_of_message_owner = [character[1] for character in characters_of_message_owner]
        for character in character_names_of_message_owner:
            # Check for character name in message
            if character in message.content:
            # print([channel_name, author, character])
                to_apply.append([gig_name, author, character])
                continue  # Avoid duplicate if alias also matches
            # Check for aliases in message
            aliases = get_one_character_aliases(author, character)
            for alias in aliases:
                if alias and alias in message.content:
                    to_apply.append([gig_name, author, character])
                    break  # Only add once per character
    
    seen = set()
    unique_to_apply = []
    for item in to_apply:
        key = tuple(item)
        if key not in seen:
            seen.add(key)
            unique_to_apply.append(item)
    # unique_to_apply = sorted(unique_to_apply, key=lambda item: item[1].lower())
    # print("To apply: ")
    # print(unique_to_apply)
    
    player_data = infer_players(messages, unique_to_apply, thread_author)
    applicant_data = unique_to_apply
    print(format_character_json_list_for_readability(applicant_data))
    print(format_character_json_list_for_readability(player_data))

    modified_applicant_data = [
        applicant + ["Played"] if applicant in player_data
        else applicant + ["Applied"]
        for applicant in applicant_data
    ]

    for applicant in modified_applicant_data:
        add_application(applicant[0], applicant[1], applicant[2], applicant[3])
        print(f"Added application for player {applicant[1]} with character {applicant[2]}, status {applicant[3]}")
    
    response_string = "Gig: " + gig_name + "\n"
    response_string += "GM: " + get_user_name_by_discord_id(thread_author) + "\n"
    if eb:
        response_string += "EB: " + str(eb) + "\n"
    if ip:
        response_string += "IP: " + str(ip) + "\n"
    if date:
        response_string += "Date: " + date + "\n"
    if tags:
        response_string += "Tags: " + tags + "\n"
    response_string += "\nI have inferred that the following characters were applied:"
    response_string += "\n" + format_character_json_list_for_readability(applicant_data)
    response_string += "\n\nAnd the following played in the game:"
    response_string += "\n" + format_character_json_list_for_readability(player_data)
    response_string += "\n\nPlease check and confirm that this is correct, adjusting the World Team sheet if necessary."
    await ctx.respond(response_string)

    #update_sheet_archive_characters()
    #update_sheet_archive_players()

@client.command(description="COMMAND IN TESTING", guild_ids=[643531969669627945, 1061931924010045522])
async def register_character(ctx: discord.ApplicationContext,
    player_name: discord.Option(str, description="Name of the character's player"),
    character_name: discord.Option(str, description="Name of the character"),
    role: discord.Option(str, choices=["Rocker", "Solo", "Netrunner", "Tech", "Medtech", "Media", "Lawman", "Exec", "Fixer", "Nomad"])):
    
    print("Starting character registration process")
    if any(role.name == "Chargen Staff" for role in ctx.author.roles):
        print("Authorised, user is Chargen Staff")
    elif any(role.name == "World Team" for role in ctx.author.roles):
        print("Authorised, user is World Team")
    else:
        print("Not authorised")
        await ctx.respond("You are not authorised to use this command, you silly goose.", ephemeral=True)
    
    today_date = datetime.today().strftime("%m/%d/%Y")
    already_there = sheet_register_character(player_name, character_name, today_date, "Active", role)

    response_string = f"Registered character {character_name} for player {player_name} with role {role}."
    await ctx.respond(response_string)

    if already_there == "new":
        await ctx.send("Please also run /register_player to register this player.")

    if len(get_one_user_active_characters_by_name(player_name))>=3:
        await ctx.send(f"This player already has 3 characters registered on the WT sheet, btw. Not on you, {player_name}, don't worry. Do let World Team know, though. I'll ping my creator as well rq. <@403983344263757844>")

    update_sheet_archive_characters()
    update_sheet_archive_players()

@client.command(description="COMMAND IN TESTING", guild_ids=[643531969669627945, 1061931924010045522])
async def retire_character(ctx: discord.ApplicationContext,
    ping_player: discord.Option(str, description="Ping the player here"),
    character_name: discord.Option(str, description="Name of the character")):
    player_name = get_user_name_by_discord_id(ping_player)

    print("Starting character retirement process")
    if any(role.name == "Chargen Staff" for role in ctx.author.roles):
        print("Authorised, user is Chargen Staff")
    elif any(role.name == "World Team" for role in ctx.author.roles):
        print("Authorised, user is World Team")
    else:
        print("Not authorised")
        await ctx.send("You are not authorised to use this command, you silly goose.", ephemeral=True)
    
    sheet_retire_character(player_name, character_name)

    response_string = f"Retired {character_name} of player {player_name}. They will (presumably) be missed."
    await ctx.send(response_string)

    update_sheet_archive_characters()
    update_sheet_archive_players()

@client.command(description="COMMAND IN TESTING", guild_ids=[643531969669627945, 1061931924010045522])
async def kill_character(ctx: discord.ApplicationContext,
    ping_player: discord.Option(str, description="Ping the player here"),
    character_name: discord.Option(str, description="Name of the character")):
    player_name = get_user_name_by_discord_id(ping_player)

    print("Starting character killing process (well presumably they were already dead)")
    if any(role.name == "Chargen Staff" for role in ctx.author.roles):
        print("Authorised, user is Chargen Staff")
    elif any(role.name == "World Team" for role in ctx.author.roles):
        print("Authorised, user is World Team")
    else:
        print("Not authorised")
        await ctx.send("You are not authorised to use this command, you silly goose.", ephemeral=True)
    
    sheet_kill_character(player_name, character_name)

    response_string = f"Marked {character_name} of player {player_name} as dead. All the way to the top, choom. See you in the next life."
    await ctx.send(response_string)

    update_sheet_archive_characters()
    update_sheet_archive_players()

@client.command(description="COMMAND IN TESTING", guild_ids=[643531969669627945, 1061931924010045522])
async def register_player(ctx: discord.ApplicationContext,
    player_name: discord.Option(str, description="Name of the character's player (same as registered for character)"),
    ping_player: discord.Option(str, description="Ping the player here")):

    print("Starting player linking process")
    if any(role.name == "Chargen Staff" for role in ctx.author.roles):
        print("Authorised, user is Chargen Staff")
    elif any(role.name == "World Team" for role in ctx.author.roles):
        print("Authorised, user is World Team")
    else:
        print("Not authorised")
        await ctx.respond("You are not authorised to use this command, you silly goose.", ephemeral=True)
    
    if not is_player_registered(player_name, ping_player):
        print("Player not registered")
        await ctx.respond(f"Registering player to WT sheet.", ephemeral=True)
        asyncio.create_task(sheet_register_player(player_name, ping_player))
    else:
        print("Player already registered")
        await ctx.respond("Player already registered.", ephemeral=True)
    
    update_sheet_archive_characters()
    update_sheet_archive_players()
    
@client.command(description="Tell Rushbot to update its archives of players/characters.", guild_ids=[643531969669627945, 1061931924010045522])
async def order_archive_update(ctx: discord.ApplicationContext):
    await ctx.respond("Sheet is updating. Hopefully. I'll send a message when it succeeds or fails.")
    resp = await run_updates()
    if resp:
        await ctx.send("Sheet updated.")
    else:
        await ctx.send("An error occurred while updating the sheet. Please contact Myriad.")

async def run_updates():
    print("Running updates...")
    try:
        update_sheet_archive_characters()
        update_sheet_archive_players()
        return True
    except Exception as e:
        print(f"run_updates error: {e}")
        return False

def infer_players(messages, applicant_list, author):
    thread_author = author
    best_message = None
    best_count = 0
    player_list = []
    for message in messages:
        print("Checking message author is correct:")
        print(message.author.id)
        print(thread_author)
        if message.author.id != thread_author:
            continue
        else:
            print("Message author is correct.")
        print("Checking message content:")
        print(message.content)
        count = 0
        for applicant in applicant_list:
            # Check character name
            if applicant[2] in message.content:
                count += 1
            # Check aliases
            else:
                aliases = get_one_character_aliases(applicant[1], applicant[2])
                for alias in aliases:
                    if alias and alias in message.content:
                        count += 1
                        break
        if count > best_count:
            best_count = count
            best_message = message

    print("Best message: " + str(best_message.content))
    for applicant in applicant_list:
        found = False
        # Check character name
        if applicant[2] in best_message.content:
            found = True
        # Check aliases
        else:
            aliases = get_one_character_aliases(applicant[1], applicant[2])
            for alias in aliases:
                if alias and alias in best_message.content:
                    found = True
                    break
        if found:
            player_list.append(applicant)
    return player_list

def format_character_json_list_for_readability(list):
    out = ""
    out_list = []
    for item in list:
        out_list.append(item[2])
    
    for i in range(len(list)):
        out += f"{i+1}. {list[i][1]} ({list[i][2]})\n"
    return out


message = """$rush fixerdeal +21
sell 10% 2x 500eb expensive
6f5 100eb premium
10% 10x 100eb Premium
"""

async def test_handle_command():
     print(await handle_command(message))

# Run the test function
# import asyncio
# asyncio.run(test_handle_command())

@client.listen()
async def on_connect():
    print("Connected")
    await client.sync_commands()

client.run('YOUR BOT TOKEN HERE')