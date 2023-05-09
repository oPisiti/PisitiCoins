from pynput import keyboard
from time import sleep
import os

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


# Keyboard
KEYS_PRESSED = {
    "up":    False,
    "down":  False,
    "enter": False
}

def update_keys_pressed(key) -> None:
    """ Updates the currently pressed keys' dictionary """
    
    global KEYS_PRESSED 
    KEYS_PRESSED = {
        "up":    key == keyboard.Key.up,
        "down":  key == keyboard.Key.down,
        "enter": key == keyboard.Key.enter
    }
    pass

# Adding listener for keyboard
listener = keyboard.Listener(
    suppress   = True,
    on_press   = update_keys_pressed,)
listener.start()


def OptionsMenu(opt, greeting = "Choose an Option:"):
    """
    This function loops printing a greeting and the options
    The current option is printed in green and when chosen (enter key) returns that string
    While the user chooses an option (arrow keys), everything inside this function is rewritten on top
    of what is on screen. Nothing other than what is written INSIDE this function gets rewritten
    """

    global KEYS_PRESSED

    os.system('color')      # This command needs to be called in order for the colors to be changed
    chosen = False
    choice = 0

    while True:

        # Printing greeting and options
        print(greeting)
        for i in range(len(opt)):
            if i == choice:    
                print(f"{bcolors.OKGREEN}{opt[i]}{bcolors.ENDC}")

            else:
                print(opt[i]) 

        # Handling key presses
        if KEYS_PRESSED["up"]:                 
            if choice > 0: choice -= 1 
            else:          choice = len(opt) - 1
            
            KEYS_PRESSED["up"] = False  

        elif KEYS_PRESSED["down"]:
            if choice < len(opt) - 1: choice +=1
            else:                     choice = 0

            KEYS_PRESSED["down"] = False  

        elif KEYS_PRESSED["enter"]: 
            KEYS_PRESSED["enter"] = False

            return opt[choice]


        # Moving to the first line
        for i in range(len(opt) + 1):
            print("", end = bcolors.UPONELINE)  # Returns only the amount of lines used in this function

        # Preventing the screen to flick
        sleep(0.1)

if __name__ == "__main__":
    print("MY HUMBLE CODE")
    greeting = "Who is the best StormLight Archive character?"
    options = ["Dalinar", "Kaladin", "Syl", "Jasnah", "Shallan", "Pattern"] 

    a = OptionsMenu(options, greeting)
    print(a)
    input()