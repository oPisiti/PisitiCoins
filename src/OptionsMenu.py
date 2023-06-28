import os
import subprocess
from collections.abc import Iterable
from time import sleep

from pynput import keyboard


class bcolors:
    """ Font colors """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    UPONELINE = '\033[F'


def update_keys_pressed(key = True) -> None:
    """ Updates the currently pressed keys' dictionary """

    set_environ_bool("KEY_UP_IS_PRESSED",    key == keyboard.Key.up)
    set_environ_bool("KEY_DOWN_IS_PRESSED",  key == keyboard.Key.down)
    set_environ_bool("KEY_ENTER_IS_PRESSED", key == keyboard.Key.enter)
    set_environ_bool("ANY_VALID_KEY_IS_PRESSED",   get_environ_bool("KEY_UP_IS_PRESSED") or get_environ_bool("KEY_DOWN_IS_PRESSED") or get_environ_bool("KEY_ENTER_IS_PRESSED"))


def set_environ_bool(var_str: str, value_bool: bool) -> None:
    """ Sets an environment variable to a string equivalent to a boolean variable """
    
    os.environ[var_str] = "True" if value_bool else "False"


def get_environ_bool(var_str: str) -> bool:
    """ Returns a boolean equivalent to values of the strings 'True' and 'False' """

    value = os.environ[var_str].lower()

    match value:
        case "true":  return True
        case "false": return False
        case _:       raise ValueError(f"Value {os.environ[var_str]} has no boolean equivalent") 


def options_menu(opt: Iterable[str], greeting = "Choose an Option:") -> str:
    """
    This function loops printing a greeting and the options
    The current option is printed in green and when chosen (enter key) returns that string
    While the user chooses an option (arrow keys), everything inside this function is rewritten on top
    of what is on screen. Nothing other than what is written INSIDE this function gets rewritten
    """

    # Determining the clear screen command based on the OS
    clear_command = "cls" if os.name == "nt" else "clear" 

    # Adding listener for keyboard
    update_keys_pressed()
    listener = keyboard.Listener(
        suppress = True,
        on_press = update_keys_pressed)
    listener.start()

    chosen = False
    choice = 0

    while True:
        os.system(clear_command)

        # Printing greeting and options
        print(greeting)
        for i in range(len(opt)):
            if i == choice:    
                print(f"{bcolors.OKGREEN}{opt[i]}{bcolors.ENDC}")

            else:
                print(opt[i]) 

        # Waiting for a key to be pressed
        while not get_environ_bool("ANY_VALID_KEY_IS_PRESSED"): 
            sleep(0.1)

        # Handling key presses
        if get_environ_bool("KEY_UP_IS_PRESSED"):
            if choice > 0: choice -= 1 
            else:          choice = len(opt) - 1
            
            set_environ_bool("KEY_UP_IS_PRESSED", False)

        elif get_environ_bool("KEY_DOWN_IS_PRESSED"):
            if choice < len(opt) - 1: choice += 1
            else:                     choice  = 0

            set_environ_bool("KEY_DOWN_IS_PRESSED", False)

        elif get_environ_bool("KEY_ENTER_IS_PRESSED"):
            set_environ_bool("KEY_ENTER_IS_PRESSED", False)

            listener.stop()
            return opt[choice]


        # Resetting the keys
        update_keys_pressed()

        # Moving to the first line
        for i in range(len(opt) + 1):
            print("", end = bcolors.UPONELINE)  # Returns only the amount of lines used in this function
        

    listener.stop()
        

if __name__ == "__main__":
    print("MY HUMBLE CODE")
    greeting = "Who is the best StormLight Archive character?"
    options = ["Dalinar", "Kaladin", "Syl", "Jasnah", "Shallan", "Pattern"] 

    a = options_menu(options, greeting)
    print(a)
    input()