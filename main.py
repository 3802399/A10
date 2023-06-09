import settings
import gui
import weather
import sys

class Main:
    def __init__(self):
        self.api = 0

        # get API key if possible, exit if not
        try:
            self.get_api()
        except FileNotFoundError:
            print("Cannot find API key file. Exiting.")
            sys.exit()

        # make sure settings file exists
        try:
            settings.Settings.open_file()
        except FileNotFoundError:
            print("Cannot find settings file. Exiting.")
            sys.exit()

        # make sure if settings file exists, it is valid JSON
        try:
            settings.Settings.open_file_check_json()
        except json.decoder.JSONDecodeError:
            print("Settings file not valid JSON file. Exiting.")
            sys.exit()

        # after basic checks done, continue

        preferred_display = settings.Settings.get_display_mode()

        if preferred_display == "gui":
            self.open_gui()
        elif preferred_display == "cli":
            self.open_cli()
        else:
            print("Error: display mode in settings must either be 'gui' or 'cli'. ")
            restoration = input("Would you like to restore it via this app? (y/n)")

            if restoration.lower() == "y":
                display = ""

                while display not in ["gui", "cli"]:
                    display = input("Enter display mode ('gui' or 'cli'): ").lower()

                settings.Settings.save_param("display", display)
            else:
                print("Exiting application.")
                return

    def get_api(self):
        # get api key from file
        file = open("api_key", "r")

        self.api = file.read().strip()

        file.close()

    def open_gui(self):
        fav_cities = settings.Settings.get_fav_cities()
        main = gui.GUIMain(fav_cities, self.api)
        main.mainloop()

    def open_cli(self):
        # introduction
        print("------------------------------ WEATHER ------------------------------\n\n")

        # print the weather for all favourite cities
        fav_cities = settings.Settings.get_fav_cities()
        wthr = weather.Weather(self.api)

        for city in fav_cities:
            wthr.get_weather(city)
            print(wthr.pretty_print())
            print("\n------------------------------\n")

        print("\n------------------------------\n")

        # if the user doesn't want to quit, ask the user for the name of a city they want to find the weather for
        while True:
            # ask user if they want to quit
            quit = input("Quit? (y/n)").lower()

            if quit == "y":
                return

            # ask city from user to display weather for said city
            city = input("Enter city name: ")
            wthr.get_weather(city)
            print(wthr.pretty_print())
            print("------------------------------\n")

if __name__ == "__main__":
    main = Main()
