from msvcrt import getch
import os

class bcolors:
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

# This function loops printing a greeting and the options
# The current option is printed in green and when chosen (enter key) returns that string
# While the user chooses an option (arrow keys), everything inside this function is rewritten on top
# of what is on screen. Nothing other than what is written INSIDE this function gets rewritten
def OptionsMenu(opt, greeting = "Choose an Option:"):
    os.system('color')      # This command needs to be called in order for the colors to be changed
    chosen = False
    choice = 0

    while True:

        print(greeting)
        for i in range(len(opt)):
            if i == choice:    
                print(f"{bcolors.OKGREEN}{opt[i]}{bcolors.ENDC}")

            else:
                print(opt[i]) 
        
        stroke = ord(getch())

        if stroke == 72:        # Up
            if choice > 0:
                choice -= 1 
            else:
                choice = len(opt) - 1          
        elif stroke == 80:      # Down
            if choice < len(opt) - 1:
                choice +=1
            else:
                choice = 0
        elif stroke == 13:      # Enter
            return opt[choice]

        # Moving to the first line
        for i in range(len(opt) + 1):
            print("", end = bcolors.UPONELINE)  # Returns only the amount of lines used in this function
        


if __name__ == "__main__":
    print("MY HUMBLE CODE")
    greeting = "Who is the best StormLight Archive character?"
    options = ["Dalinar", "Kaladin", "Syl", "Jasnah", "Shallan", "Pattern"] 

    a = OptionsMenu(options, greeting)
    print(a)
    input()