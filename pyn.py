# Python Notes (PYN)
# Simple and fast notetaking app for remembering things
# Created by Dan Spencer (2020)

# TODO --> Add ability to display only notes in a certain category

import os, sys, csv
from secrets import token_hex
from datetime import datetime


csv_filename = './pynotes.csv'
csv_bak_dir = './backup'
csv_bak_filename = os.path.join(csv_bak_dir, './pynotes_bak1.csv') # Backup file
csv_bak_exit_fn = os.path.join(csv_bak_dir, './pynotes_bak2.csv')
csv_fieldnames = ['id', 'date', 'category', 'content']

autosave = True
backup_on_exit = True

title = "Python Notes (PYN)"
status = None # Initial status message
prompt = '>>> '


class Note:

    def __init__(self, hex_id, date, category, content):
        self.hex_id = hex_id
        self.date = date
        self.category = category
        self.content = content

    def __repr__(self):
        return (f"Note(hex_id={self.hex_id}, date={self.date}, "
                f"category={self.category}, content={self.content}")


# Check if csv file exists; If not, create a new file with headers
if not os.path.isfile(csv_filename):
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_fieldnames)
        writer.writeheader()
        status = f"Created new csv file named '{csv_filename.split('/')[1]}'"

# Check if backup directory exists; Create one if necessary
if not os.path.exists(csv_bak_dir):
    os.mkdir(csv_bak_dir)


# Load notes from csv file as Note class-objects; Returns list of Note objects
def load_notes():
    notes = []
    with open(csv_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=csv_fieldnames)

        next(reader) # Skip header
        for note in reader:
            notes.append(Note(note['id'], note['date'], note['category'],
                         note['content']))

    return notes


# Save notes to csv file; Use filename kwarg to save to another file
def save_notes(filename=csv_filename, backup_on_save=False):
    if backup_on_save == True:
        backup_notes()

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_fieldnames)

        writer.writeheader()
        for note in pyn_notes:
            row = ({'id': note.hex_id, 'date': note.date, 
                    'category': note.category, 'content': note.content})
            writer.writerow(row)

    return "Changes to notes have been saved!"


# Backup notes to a separate file; Use filename kwarg to save to another file
def backup_notes(filename=csv_bak_filename):
    with open(csv_filename, 'r') as csvfile:
            with open(filename, 'w') as csvbakfile:
                for row in csvfile:
                    csvbakfile.write(row)
    
    return "Backup complete!"


# Add a new note and save to file
def add_note():
    os.system('cls')
    print(title)
    print("Create a new note...")
    content = input(prompt)

    print("Enter a category (default: general)...")
    category = input(prompt).lower() # Convert to lower-case
    if category == '': 
        category = 'general'

    hex_id = token_hex(4)
    date = datetime.today().strftime("%m-%d-%y %H:%M")
    # Create a new Note obj and add to pyn_notes list
    pyn_notes.append(Note(hex_id, date, category, content))

    # Return a status message
    return f"Created new note with ID '{hex_id}' in '{category}' category"
    

# Delete a note and save to file
def del_note():
    # Call with kwarg to skip pressing ENTER
    view_notes(enter=False)
    
    print("Select note # to delete...")
    try:
        note_index = int(input(prompt)) - 1 # Subtract one due to display diff

        if 0 <= note_index < len(pyn_notes):
            if del_note_confirm(note_index):
                del pyn_notes[note_index]
                return f"Note {note_index + 1} was deleted..."
    except Exception:
        return "Could not delete note. Please use a valid index."


# Confirm the deletion of a note
def del_note_confirm(note_index):
    print(f"Are you sure you want to delete note {note_index + 1}? (yes or no)")
    confirm = input(prompt)

    if confirm.lower() in ['y', 'yes']:
        return True
    else:
        return False


# Edit an existing note
def edit_note():
    view_notes(enter=False)

    print("Select note # to edit...")
    try:
        note_index = int(input(prompt)) - 1 # Subtract one due to display diff

        if 0 <= note_index < len(pyn_notes):
            print(f"Current Text: {pyn_notes[note_index].content}")
            edit_text = input(prompt)
            if edit_text == '':
                return f"Note {note_index} was NOT modified..."

            pyn_notes[note_index].content = edit_text
            return f"Note {note_index} was modified!"
    except Exception:
        return "Could not edit note. Please use a valid index."


# Display all saved notes; Returns a list of note IDs
def disp_notes(enter=True):
    os.system('cls')
    print(title)
    print("Displaying all notes...\n")

    hex_id, date, category, content = csv_fieldnames
    print(f"#   {hex_id.upper():10}{date.title():16}{category.title():12} "
        f"{content.title()}")

    for pos, note in enumerate(pyn_notes):
        print(f"{str(pos+1):<4}{note.hex_id:10}{note.date:16}"
            f"<{note.category+'>':12}'{note.content}'")

    # Press enter to exit function and return to main loop
    if enter == True:
        input("Press ENTER to continue...")


# View notes in a basic manner and by category if given
def view_notes(enter=True, cat='all'):
    os.system('cls')
    print(title)
    print(f"Viewing notes (category: {cat})...\n")

    _, _, category, content = csv_fieldnames # _ values are not used
    print(f"#   {category.title():12} {content.title()}")

    for pos, note in enumerate(pyn_notes):
        if cat == 'all' or cat.lower() == note.category:
            print(f"{str(pos+1):<4}<{note.category+'>':12}'{note.content}'")

    # Press enter to exit function and return to main loop
    if enter == True:
        input("Press ENTER to continue...")


cmd_dict = {
    'help': 'Display all available commands   (alt: h)',
    'add':  'Create a new note                (alt: a, new)',
    'del':  'Delete an existing note          (alt: x, delete)',
    'edit': 'Edit an existing note            (alt: e)',
    'save': 'Save notes to csv file           (alt: s)',
    'view': 'View basic info of saved notes   (alt: v <category>)',
    'disp': 'Display all info for saved notes (alt: d, display)',
    'exit': 'Exit Python Notes                (alt: q, quit)'
    }

pyn_notes = load_notes() # This is where we load our notes into memory

# MAIN LOOP ====================================================================
while True:
    os.system('cls') # Clear the screen
    print(title)
    # Use a default status message that displays help text
    if status == None:
        status = "Enter a command. Type HELP for a list of commands."
    print(f"Status: {status}")
    command = input(prompt) # Get a command from user
    status = None # Reset status msg

    # Check if command has multiple arguments
    if len(command.split()) > 1:
        command = command.split()

        if command[0].lower() in ['view', 'v'] and len(command) == 2:
            view_notes(cat=command[1])
            continue

    # Otherwise use standard single commands
    if command.lower() in ['help', 'h']:
        for cmd, desc in cmd_dict.items():
            print(f"{cmd.upper() + ':':<8}{desc}")
        input("Press ENTER to continue...") # Wait for user to press Enter key
    elif command.lower() in ['add', 'a', 'new']:
        status = add_note()
    elif command.lower() in ['del', 'x', 'delete']:
        status = del_note()
    elif command.lower() in ['edit', 'e']:
        status = edit_note()
    elif command.lower() in ['save', 's']:
        status = save_notes(backup_on_save=True)
    elif command.lower() in ['view', 'v']:
        view_notes()
    elif command.lower() in ['disp', 'd', 'display']:
        disp_notes()
    elif command.lower() in ['exit', 'quit', 'q']:
        if backup_on_exit == True:
            print("Backing up notes...")
            backup_notes(filename=csv_bak_exit_fn)
        if autosave == True:
            print("Saving changes and exiting...")
            save_notes()
        sys.exit(0)
