#  //)) \\// /| // Python
# //     // //|//  Notes
#
# Simple and fast notetaking app for remembering things
# Created by Dan Spencer (2020) for Windows

import os, sys, csv
from secrets import token_hex
from datetime import datetime
from textwrap import wrap
from time import sleep


csv_filename = './pynotes.csv'
csv_bak_dir = './backup'
csv_bak_filename = os.path.join(csv_bak_dir, './pynotes_bak1.csv') # Backup file
csv_bak_exit_fn = os.path.join(csv_bak_dir, './pynotes_bak2.csv')
csv_fieldnames = ['id', 'date', 'category', 'content']

autosave = True
backup_on_exit = True
auto_view_notes = True # Notes are displayed automatically
changes_saved = True # Track if a file has been saved after changes are made
status = None # Initial status message
default_sort = 'date' # The method of sorting on startup and when adding a note
exit_delay = 1.5

title = r"""  
 //)) \\// /| // Python
//     // //|//  Notes
"""
prompt = '>>> '


class Note:
    """Contains information about a note.

    Designed to be loaded from a csv file and store in a list with other
    Note objects using load_notes function."""

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


def load_notes():
    """Load notes from csv file as Note class-objects.
        Returns list of Note objects."""

    notes = []
    with open(csv_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=csv_fieldnames)

        next(reader) # Skip header
        for note in reader:
            notes.append(Note(note['id'], note['date'], note['category'],
                         note['content']))
            if note['category'].lower() not in cat_list:
                cat_list.append(note['category'].lower()) # Fill category list

    return notes


def save_notes(filename=csv_filename, backup_on_save=True):
    """Save notes to csv file; Use filename kwarg to save to another file."""

    if backup_on_save == True:
        backup_notes() # Backup notes when saving manually

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_fieldnames)

        writer.writeheader()
        for note in pyn_notes:
            row = ({'id': note.hex_id, 'date': note.date, 
                    'category': note.category, 'content': note.content})
            writer.writerow(row)

    global changes_saved
    changes_saved = True
    return "Changes to notes have been saved!"


def backup_notes(filename=csv_bak_filename):
    """Backup notes to a separate file."""

    with open(csv_filename, 'r') as csvfile:
            with open(filename, 'w') as csvbakfile:
                for row in csvfile:
                    csvbakfile.write(row)
    
    return "Backup complete!"


def add_note(sort_on_add=True):
    """Create a new note object.
    
    sort_on_add: bool: Sorts notes by date if true"""

    clear_disp("Create a new note...")

    content = input(prompt)
    if content == '':
        return "Note was not created. Cannot be blank."

    category = cat_note()
    hex_id = token_hex(4)
    date = datetime.today().strftime("%m-%d-%y %H:%M")

    # Create a new Note obj and add to pyn_notes list
    pyn_notes.append(Note(hex_id, date, category, content))

    if sort_on_add == True:
        sort_notes() # Sort list of notes

    # Set changes_saved variable to false and return status message
    global changes_saved
    changes_saved = False
    return f"Created new note in '{category}' category with ID '{hex_id}'"
    

def del_note():
    """Delete an existing note."""

    view_notes(enter=False) # Call with arg to skip pressing ENTER
    
    print("Select note # to delete...")
    try:
        note_index = int(input(prompt)) - 1 # Subtract one due to display diff

        if 0 <= note_index < len(pyn_notes):
            if del_note_confirm(note_index):
                del pyn_notes[note_index]

                global changes_saved
                changes_saved = False
                return f"Note {note_index + 1} was deleted..."
            else:
                raise Exception
    except Exception:
        return "Could not delete note. Please use a valid index."


def del_note_confirm(note_index):
    """Confirm the deletion of a note."""

    print(f"\nAre you sure you want to delete note {note_index + 1}? (yes or no)")
    confirm = input(prompt)

    if confirm.lower() in ['y', 'yes']:
        return True
    else:
        return False


def edit_note():
    """Edit an existing note."""

    view_notes(enter=False)

    print("Select note # to edit...")
    try:
        note_index = int(input(prompt)) - 1 # Subtract one due to display diff

        if 0 <= note_index < len(pyn_notes):
            clear_disp(f"Current text: {pyn_notes[note_index].content}")

            edit_text = input(prompt)
            if edit_text == '':
                edit_text = pyn_notes[note_index].content # Use current text

            # Edit note category
            edit_cat = cat_note()

            # Update note object
            pyn_notes[note_index].content = edit_text
            pyn_notes[note_index].category = edit_cat

            global changes_saved
            changes_saved = False
            return f"Note {note_index} was modified successfully!"
    except Exception:
        return "Could not edit note. Please use a valid index."


def cat_note(cat_confirm=True):
    """Set the category for a note.
    
    cat_confirm: bool: Confirms the creation of a new category"""

    print("\nEnter a category (default: general)...")
    print("Category list: ", end='')
    print(*cat_list, sep=', ')

    category = input(prompt).lower() # Convert to lower-case
    if category == '':
        category = 'general'
    # Confirm creation of category if it does not already exist
    elif category not in cat_list and cat_confirm == True:
        print("\nCategory does not exist. Would you like to create it?")
        
        if input(prompt).lower() in ['y', 'yes']:
            cat_list.append(category)
        else:
            category = 'general'

    return category


def disp_notes(enter=True, newlines=True):
    """Display all saved notes.

    enter: bool: wait for user to press ENTER
    newlines: bool: print newlines between notes"""

    clear_disp("Displaying all notes")

    hex_id, date, category, content = csv_fieldnames
    print(f"#   {hex_id.upper():10}{date.title():16}{category.title():15} "
          f"{content.title()}")

    for pos, note in enumerate(pyn_notes, start=1):
        # Split note into list using textwrap.wrap function
        split_note = wrap(note.content, width=70)

        print(f"{str(pos):<4}{note.hex_id:10}{note.date:16}"
              f"<{note.category+'>':15}", end='')
        for pos, line in enumerate(split_note):
            if pos == 0:
                print(f"'{line}'")
            else:
                print(f"{' ' * 46}'{line}'") # Pad with spaces

        if newlines == True:
            print() # Add a newline between notes

    # Press enter to exit function and return to main loop
    if enter == True:
        input("Press ENTER to continue...")


def view_notes(enter=True, cat='all', limit=200):
    """View notes in a basic manner
    
    cat: str: View only select category
    limit: int: How many notes to view"""
    
    clear_disp(f"Viewing notes (category: {cat})")

    _, _, category, content = csv_fieldnames # _ values are not used
    print(f"#   {category.title():15} {content.title()}")

    for pos, note in enumerate(pyn_notes, start=1):
        if cat == 'all' or cat.lower() == note.category:
            # Split note into list using textwrap.wrap function
            split_note = wrap(note.content, width=90)

            print(f"{str(pos):<4}<{note.category+'>':15}", end='')
            for pos, line in enumerate(split_note):
                if pos == 0:
                    print(f"'{line}'")
                else:
                    print(f"{' ' * 20}'{line}'") # Pad with spaces

        # Display limit for notes
        if pos == limit:
            print(f"Displaying first {limit} notes ({pyn_notes_num - limit} remaining)")
            break

    print() # Blank line
    # Press enter to exit function and return to main loop
    if enter == True:
        input("Press ENTER to continue...")


def sort_notes(sort_by=default_sort):
    """Sorts the list of note objects. Requires the pyn_notes global list.

    sort_by: str: default is default_sort which is a global variable"""

    if sort_by == 'date':
        pyn_notes.sort(key=lambda x: x.date, reverse=True)
    elif sort_by == 'category':
        pyn_notes.sort(key=lambda x: x.category, reverse=False)
    else:
        return f"Notes could not be sorted by '{sort_by}'..."

    global changes_saved
    changes_saved = False
    return f"Notes have been sorted by {sort_by}!"


def clear_disp(msg):
    """Clear the display. Then show title and a message."""

    os.system('cls')
    print(title)
    print(msg, '\n')


def pyn_help():
    """Display the list of commands."""

    clear_disp('Command list')

    cmd_dict = {
        'help': 'Display all available commands   (alt: h)',
        'add':  'Create a new note                (alt: a, new)',
        'del':  'Delete an existing note          (alt: x, delete)',
        'edit': 'Edit an existing note            (alt: e)',
        'save': 'Save notes to csv file           (alt: s)',
        'view': 'View basic info of saved notes   (alt: v <category>)',
        'disp': 'Display all info for saved notes (alt: d, display)',
        'sort': 'Sort notes by date or category   (alt: o <sort_by>',
        'exit': 'Exit Python Notes                (alt: q, quit)'
    }

    for cmd, desc in cmd_dict.items():
        print(f"{cmd.upper() + ':':<8}{desc}")

    print() # Blank line
    input("Press ENTER to continue...") # Wait for user to press Enter key


cat_list = [] # List of categories
pyn_notes = load_notes() # This is where we load our notes into memory

# MAIN LOOP ====================================================================
while True:
    os.system('cls') # Clear the screen
    print(title)

    pyn_notes_num = len(pyn_notes) # Number of notes in total

    # View notes automatically
    if auto_view_notes == True:
        view_notes(enter=False, limit=18)

    # Use a default status message that displays help text
    if status == None:
        status = "Enter a command. Type HELP for a list of commands."

    # Print a different status message depending on if changes are saved
    status_saved = f"Status: {status}"
    status_unsaved = f"Status (Unsaved): {status}"
    print(status_saved if changes_saved == True else status_unsaved)
    status = None # Reset status msg

    command = input(prompt) # Get a command from user

    # Check if command has multiple arguments
    if len(command.split()) > 1:
        command = command.split()

        if command[0].lower() in ['view', 'v'] and len(command) == 2:
            view_notes(cat=command[1])
        elif command[0].lower() in ['sort', 'o'] and len(command) == 2:
            status = sort_notes(sort_by=command[1])
        else:
            status = "The command or number of arguments given was invalid."

    # Otherwise use standard single argument commands
    elif command.lower() in ['help', 'h']:
        pyn_help()
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
    elif command.lower() in ['sort', 'o']:
        status = sort_notes()
    elif command.lower() in ['exit', 'quit', 'q']:
        if backup_on_exit == True:
            print("Backing up notes...")
            backup_notes(filename=csv_bak_exit_fn)
        if autosave == True:
            print("Saving changes and exiting...")
            save_notes()
        sleep(exit_delay)
        sys.exit(0)
