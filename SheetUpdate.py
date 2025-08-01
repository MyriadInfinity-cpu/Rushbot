from __future__ import print_function
import os.path
import pickle
import json
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of the spreadsheet.
SPREADSHEET_ID = 'YOUR SPREADSHEET ID HERE'
RANGE_NAME = 'Game Data!A1'

def get_sheet():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If no valid credentials are available, prompt the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('YOUR SPREADSHEET JSON HERE', SCOPES)
            creds = flow.run_local_server(port=5678)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    return sheet

def get_test():
    sheet = get_sheet()

    # Fetch the current count of external applicants, which is in cell J2 on the
    # Information sheet.
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="Games Input!A2:CO"
    ).execute()
    values = result.get('values', [])
    # print(f"Current values: {values}")
    return values

def get_all_characters():
    with open('character_archive.json', 'r') as json_file:
        values = json.load(json_file)
    return values

def get_one_user_all_characters_by_name(user_name):
    print("Retrieving characters for user ")
    print(user_name)
    
    character_values = "error"
    with open('character_archive.json', 'r') as json_file:
        character_values = json.load(json_file)

    matching_characters = [
        character for character in character_values
        if character and character[0].strip() == user_name.strip()
    ]

    # print(f"Character info: {matching_characters}")
    return matching_characters

def get_one_character_aliases(user_name, character_name):
    print("Retrieving aliases for character ")
    print(character_name)
    character_values = "error"
    with open('character_archive.json', 'r') as json_file:
        character_values = json.load(json_file)
        aliases = []
        for character in character_values:
            if character and character[0].strip() == user_name.strip() and character[1].strip() == character_name.strip():
                if len(character) > 5 and character[5].strip():
                    aliases = [alias.strip() for alias in character[5].split(',')]
                break
        return aliases

def get_one_user_active_characters_by_name(user_name):
    inp = get_one_user_all_characters_by_name(user_name)
    active_characters = [
        character for character in inp
        if character[3].strip() == "Active"
    ]
    return active_characters

def get_user_name_by_discord_id(discord_id):
    player_values = "error"
    with open('player_archive.json', 'r') as json_file:
        player_values = json.load(json_file)

    # Find the row with the matching Discord ID
    for row in player_values:
        if row and len(row) > 1 and str(discord_id).strip() in row[1].strip():
            return row[0]  # Return the player's name

    return None  # Return None if no match is found

def add_application(game, player, character, status):
    sheet = get_sheet()

    # The data to append (each inner list is a row)
    values = [
        [game, player, character, status],
    ]
    body = {
        'values': values
    }

    # Append the data to the sheet.
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="APPLICATION_DATA!A2",
        valueInputOption='USER_ENTERED',  # Let Google Sheets parse the input (e.g., numbers, formulas)
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    print(f"{result.get('updates').get('updatedCells')} cells appended.")

def add_game(game_name, gm, status, date, eb, ip, tags):
    sheet = get_sheet()

    event = False
    fix = False
    if "fix" in tags.lower():
        fix = True
    if "event" in tags.lower():
        event = True
    # The data to append (each inner list is a row)
    values = [
        [game_name, gm, status, date, eb, ip, None, event, fix],
    ]
    body = {
        'values': values
    }

    print(f"Adding game:")
    print(values)
    # Append the data to the sheet.
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="GAME_DATA!A2",
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    print(f"{result.get('updates').get('updatedCells')} cells appended.")

def import_old_games(inp):
    sheet = get_sheet()
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"Games Input!A{inp}:CO"
    ).execute()
    games_input = result.get('values', [])

    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="Old Character Data!A2:B"
    ).execute()
    character_data = result.get('values', [])

    # Getting the old applicants
    for i in games_input: # loop through each inputted game
        # game name
        game_name = i[0]
        game_status = i[1]
        print(game_name, game_status)

        # retrieve the applicant count
        try:
            applicant_count = int(i[42])
        except ValueError:
            applicant_count = 0
        print(f"Applicant count: {applicant_count}")

        # retrieve names of all applicants
        applicant_names = i[43::] 
        print(f"Applicant names: {applicant_names}")

        # retrieve names of the actual picked players
        player_names = [name for name in i[8:18] if name.strip() != ""]
        print(f"Player names: {player_names}")

        combined_names = list(set(applicant_names + player_names))
        # now, applicant_names contains a list of names of all applied characters
        # get that character's associated player and add to APPLICATION_DATA
        character_data = get_all_characters()
        for i in character_data:
            if i[1].strip() == "":
                continue
            for c in combined_names:
                if c == i[1]:
                    print(f"Found character {i[1]} with associated player {i[0]}")
                    # Add application
                    if i[1] in player_names:
                        add_application(game_name, i[0], i[1], "Played")
                    else:
                        add_application(game_name, i[0], i[1], "Applied")
                    break
    
    return ""

def sheet_kill_character(player_name, character_name):
    sheet = get_sheet()
    character_data = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="CHARACTER_DATA!A2:E"
    ).execute()
    character_values = character_data.get('values', [])

    # Find the character to kill
    for i in character_values:
        if i[0].strip() == player_name and i[1].strip() == character_name:
            # Update the status to "Dead"
            i[3] = "Dead"
            break
        else:
            i[0] = None
            i[1] = None
            i[2] = None
            i[3] = None
            i[4] = None

    # Write the updated data back to the sheet
    body = {
        'values': character_values
    }
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="CHARACTER_DATA!A2:E",
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    print(f"{result.get('updatedCells')} cells updated.")

def sheet_retire_character(player_name, character_name):
    sheet = get_sheet()
    character_data = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="CHARACTER_DATA!A2:E"
    ).execute()
    character_values = character_data.get('values', [])

    # Find the character to retire
    for i in character_values:
        if i[0].strip() == player_name and i[1].strip() == character_name:
            # Update the status to "Retired"
            i[3] = "Retired"
            break

    # Write the updated data back to the sheet
    body = {
        'values': character_values
    }
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="CHARACTER_DATA!A2:E",
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    print(f"{result.get('updatedCells')} cells updated.")

def sheet_register_character(player_name, character_name, date_approved, status, role):
    sheet = get_sheet()
    already_registered = False

    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="CHARACTER_DATA!A2:E"
    ).execute()
    existing_characters = result.get('values', [])

    # Check if player_name is already registered (assuming player_name is stored in the first column)
    for row in existing_characters:
        if row and row[0].strip() == player_name.strip():
            print(f"Player {player_name} is already registered.")
            already_registered = True
            break

    # New character information wahoo
    new_character = [player_name, character_name, date_approved, status, role]

    # Write the updated data to the sheet
    body = {
        'values': [new_character]
    }
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="CHARACTER_DATA!A2:E",
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    print(f"{result.get('updates').get('updatedCells')} cells appended.")

    if not already_registered:
        return "new"
    return "old"

def is_player_registered(player_name, discord_id):
    sheet = get_sheet()
    already_registered = False

    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="PLAYER_DATA!A2:E"
    ).execute()
    existing_players = result.get('values', [])

    print(f"Checking for registration of discord_id {discord_id} and player_name {player_name}.")
    # Check if player_name or ID is already registered
    for row in existing_players:
        if row and len(row) < 2:
            continue
        else:
            if row and row[0].strip() == row[1].strip():
                continue
        if row and row[1].strip() == discord_id.strip():
            print("TTTTTTTTTT")
            print(f"Player {discord_id} is already registered.")
            already_registered = True
            break

    if already_registered == True:
        return True
    else:
        return False
    
async def sheet_register_player(player_name, discord_id):
    sheet = get_sheet()

    player_data = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="PLAYER_DATA!A2:E"
    ).execute()
    player_values = player_data.get('values', [])

    # Find the player being sought
    for i in player_values:
        if i[0].strip() == player_name.strip():
            print(f"Found player {player_name}.")
            # Update the LOOKUP_SHEET at cell A2
            body = {
                'values': [[player_name]]
            }
            print(body)
            result = sheet.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"LOOKUP_SHEET!A2",
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            print(f"{result.get('updatedCells')} cells updated in LOOKUP_SHEET.")
            break

    time.sleep(0.5)
    # now find the row of the player in PLAYER_DATA from the lookup sheet
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="LOOKUP_SHEET!A3"
    ).execute()
    print(f"Extracted row {result} from lookup sheet.")

    row = result.get('values', [])[0][0]
    # Update player's row with Discord ID
    body = {
        'values': [[discord_id]]
    }
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"PLAYER_DATA!B{row}",
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    print(f"{result.get('updatedCells')} cells updated in PLAYER_DATA.")

    # clear the LOOKUP_SHEET
    body = {
        'values': [[""]]
    }
    print(body)
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"LOOKUP_SHEET!A2",
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    print(f"{result.get('updatedCells')} cells updated in LOOKUP_SHEET to clear.")

def update_sheet_archive_characters():
    print("Updating character archive...")
    sheet = get_sheet()
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="CHARACTER_DATA!A2:G"
    ).execute()
    values = result.get('values', [])
    with open('character_archive.json', 'w') as json_file:
        json.dump(values, json_file, indent=2)
    print("Done.")

def update_sheet_archive_players():
    print("Updating player archive...")
    sheet = get_sheet()
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="PLAYER_DATA!A2:C"
    ).execute()
    values = result.get('values', [])
    with open('player_archive.json', 'w') as json_file:
        json.dump(values, json_file, indent=2)
    print("Done.")

# update_sheet_archive_players()
# update_sheet_archive_characters()

# Also print the values
# print(values)
# import_old_games(1000)
# print(get_all_characters())
# add_application("Boardroom blitz", "Jennyglitz", "The Shrike", "Accepted")
# print(get_one_user_active_characters_by_name("Jennyglitz"))
# kill_character("Jennyglitz", "Lizzy Steele")
# print(get_one_user_active_characters_by_name("Jennyglitz"))
# print(sheet_register_character("Rushbot", "Testing Man", "2025-04-02", "Active", "Solo"))
# sheet_register_player("Rushbot", "123456789012345678")
# print(get_user_name_by_discord_id("403983344263757844"))
# print(get_one_user_active_characters_by_name(get_user_name_by_discord_id("403983344263757844")))
# print(get_one_character_aliases("Rache", "Python"))