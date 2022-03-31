import argparse
from ast import If

import logging
from logging.config import dictConfig
from pickle import TRUE
import sys
import datetime
from datetime import date
import time
import os
import reportic_database_class

# GLOBALS
__version__ = "0.1.0"
__author__ = "Eugen Maksymenko <eugen.maksymenko@gmx.net>"
# relative dir for the database
relative_path_to_project = (f"{os.path.dirname(__file__)}/..")
file_dir_database = "/database"
relative_file = "/reportic_database.sqlite"
DATABASEPATH = relative_path_to_project + file_dir_database+relative_file


class MissingSubCommand(ValueError):
    pass


class bcolors:
    """Colors for Terminal output"""
    RED = '\033[31m'
    YELLOW = '\u001b[33m'
    GREEN = '\033[92m'
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# command list
CMD_LIST = ["Add new Entry",
            "Select KW",
            "Delete ",
            "List current Workreport",
            "Export Workreport",
            "Configurate User",
            "Exit the programm",
            ]


# Logging module
DEFAULT_LOGGING_DICT = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {'format': '[%(levelname)s] %(funcName)s: %(message)s'},
    },
    'handlers': {
        'default': {
            'level': 'NOTSET',  # will be set later
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        __name__: {
            'handlers': ['default'],
            'level': 'INFO',
            # 'propagate': True
        }
    }
}
#: Map verbosity level (int) to log level
LOGLEVELS = {None: logging.WARNING,  # 0
             0: logging.ERROR,
             1: logging.WARNING,
             2: logging.INFO,
             3: logging.DEBUG,
             }
#: Instantiate our logger
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def parsecli(cliargs=None) -> argparse.Namespace:
    """Parse CLI with :class:`argparse.ArgumentParser` and return parsed result
    :param cliargs: Arguments to parse or None (=use sys.argv)
    :return: parsed CLI result
    """
    parser = argparse.ArgumentParser(description=__doc__,
                                     epilog="Version %s written by %s " % (
                                         __version__, __author__)
                                     )

    parser.add_argument('-v', '--verbose',
                        action='count',
                        default=0,
                        help="increase verbosity level")

    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + __version__
                        )

    args = parser.parse_args(args=cliargs)
    # Setup logging and the log level according to the "-v" option
    dictConfig(DEFAULT_LOGGING_DICT)
    log.setLevel(LOGLEVELS.get(args.verbose, logging.DEBUG))

    log.debug("CLI result: %s", args)

    # help for the user when no subcommand was passed
    if "func" not in args:
        # create initial database
        if os.path.exists(DATABASEPATH) != True:
            create_database_dir()
            create_database()

        cli_menue()

    # parser.print_help()
    # raise MissingSubCommand("Expected subcommand")

    # Setup logging and the log level according to the "-v" option
    dictConfig(DEFAULT_LOGGING_DICT)
    log.setLevel(LOGLEVELS.get(args.verbose, logging.DEBUG))
    log.debug("CLI result: %s", args)

    return args


def create_database():
    log.debug("create_database()")
    sql_data = None
    sql_database = reportic_database_class.Database(DATABASEPATH, sql_data)
    sql_database.close


def create_database_dir():
    # log.debug(DATABASEPATH)
    try:
        os.mkdir(f"../{file_dir_database}")
        log.debug(f"Directory  created at{DATABASEPATH}")
    except:
        log.debug(f"Path {DATABASEPATH} was not created")


def main(cliargs=None) -> int:
    """Entry point for the application script
    :param cliargs: Arguments to parse or None (=use :class:`sys.argv`)
    :return: error code
    """
    clean_console()
    try:
        args = parsecli(cliargs)
        # do some useful things here...
        # If everything was good, return without error:
        return 0

    except MissingSubCommand as error:
        log.fatal(error)
        return 888


def get_time_strings():
    """Get current time, date and KW as return values"""
    log.debug("get_time_strings() was executed")
    today = date.today()
    formated_date = today.strftime("%d-%m-%Y")
    current_time = time.localtime()
    calendar_week = datetime.date.today().isocalendar()[1]
    return current_time, formated_date, calendar_week,


def check_day_evening(current_time_obj):
    """Function for checking if its day or evening"""
    log.debug("check_day_evening was executed")
    if current_time_obj.tm_hour >= 17:
        return "evening"
    else:
        return "day"


def cli_commands_sub_menue() -> bool:
    """Numbers and outputs elements of all CMDS Strigs"""
    log.debug("cli_commands_sub_menue was executed")
    cmd_list_counter = 1
    for x in CMD_LIST:
        print(f"{cmd_list_counter}:{x}")
        cmd_list_counter += 1
    return TRUE


def cli_menue() -> bool:
    """Display User Interface in the Command Line"""
    log.debug("cli_menue() was executed")
    current_time, date, calendar_week = get_time_strings()
    # check if its day or evening
    print(f"Good {check_day_evening(current_time)}")
    print(f"Today is {date}")
    print(f"We have the {calendar_week} KW")
    cli_commands_sub_menue()
    # run user input looop
    cli_menue_interface()
    return TRUE


def cli_menue_interface():
    """Loop for user interface"""
    log.debug("cli_menue_interface() was executed")
    keep_going = True
    while keep_going == True:
        menue_selector_number = input("Choose an option: ")
        if menue_selector_number == "7":
            # exit the programm
            clean_console()
            quit()
        if menue_selector_number == "6":
            clean_console()
            cli_menue_config_user()

        if menue_selector_number == "4":
            # list all week entries
            cli_week_report()
        if menue_selector_number == "1":
            # list all week entries
            clean_console()
            cli_add_entry()


def cli_menue_config_user():
    """User input of the config name"""
    # get current user data from database
    sql_database = reportic_database_class.Database(DATABASEPATH)
    first_name, last_name, team_name = reportic_database_class.Database.get_user_table(
        sql_database)

    print(f"""
          Current first Name: {first_name}
          Current last  Name: {last_name}
          Current Team  Name: {team_name}
          """)

    first_name = input("Enter your first name: ")
    last_name = input("Enter your last name: ")
    team_name = input("Enter your Team name: ")
    try:
        sql_database.set_user_table(first_name, last_name, team_name)
        print("Changes have been made to the database")
    except Exception as e:
        log.debug(f"""
                Error message: {e}
                cli_menue_config_user()
                Changes have not been adopted to the database!
                """)
    cli_menue_return()


def cli_week_report():
    # clean console
    log.debug("cli_week_report() was executed")
    clean_console()
    print("Weekly Report")
    print(f"KW {datetime.date.today().isocalendar()[1]}")
    print("Name:<PLACEHOLDER>     Team:<PLACEHOLDER>")
    print(f"{bcolors.RED}RED:{bcolors.ENDC}")
    print(f"{bcolors.GREEN}Amber:{bcolors.ENDC}")
    print(f"{bcolors.YELLOW}GREEN:{bcolors.ENDC}")
    cli_menue_return()


def cli_menue_return():
    while True:
        return_to_main_menue = input(
            "Enter 'b' to return to main menue or press 'e' to exit  ")
        if return_to_main_menue == "b":
            # clean and return to main menue
            cli_return_to_cli_menue()
            break
        if return_to_main_menue == "e":
            # clean and end programm
            clean_console()
            quit()


def clean_console():
    """OS cleans the console window"""
    log.debug("clean_console() was executed")
    os.system('cls' if os.name == 'nt' else 'clear')


def cli_return_to_cli_menue():
    """Return you to the main menue"""
    log.debug("cli_return_to_cli_menue() was executed")
    clean_console()
    cli_menue()


def cli_add_entry():
    """Add new entry to the current Calender Week to the database"""
    category_list = ["GREEN", "AMBER", "RED", "MEETING"]
    clean_console()
    print("""
          Add new entry to the work report
          """)
    entry_text = input("Add new Entry: ")

    print("Choose a category")
    category_counter = 1
    for x in category_list:
        print(f"{category_counter}:{category_list[category_counter-1]} ")
        category_counter += 1

    category_selector = input(
        f"Chooose an option from 1 to {category_counter-1}  ")

    category = category_list[int(category_selector)-1]

    print(f"Entry: {entry_text}   Category: {category}")

    # get time and kw
    date_obj, date_formatted, calender_week = get_time_strings()
    print(
        f"Date1: {date_obj} Date2: {date_formatted} CalenderWeekNumber: {calender_week}")
    # database handling
    sql_database = reportic_database_class.Database(DATABASEPATH)
    sql_database.set_entry(category, entry_text, calender_week, date_formatted)

    cli_menue_return()


if __name__ == "__main__":
    sys.exit(main())
