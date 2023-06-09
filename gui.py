import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import weather
import settings
from PIL import Image, ImageTk
import webbrowser
import tkintermapview

class MapWindow(tk.Frame):
    def __init__(self, close_win):
        tk.Frame.__init__(self)

        self.close_win = close_win
        self.marker = None

        # map
        self.map = tkintermapview.TkinterMapView(self, width=800, height=600, corner_radius=0)
        self.map.grid(row=0, column=0, columnspan=5, padx=5, pady=5, sticky='nsew')

        # go back button
        self.back = ttk.Button(self, text="Back", command=self.close_win)
        self.back.grid(row=1, column=0, padx=5, pady=5)

    def change_location(self, city, country):
        # delete any current marker
        if self.marker:
            self.marker.delete()
        # change the map to the current city, and show a red marker/pin on it
        self.marker = self.map.set_address(f"{city},{country}", marker=True)

class SettingsWindow(tk.Frame):
    def __init__(self, close_win, save_win):
        tk.Frame.__init__(self)

        # widgets

        # widget to select temp unit
        self.temp_name = ttk.Label(self, text="Temp Units")
        current_temp = settings.Settings.get_temp_unit()
        self.temp_selected = tk.StringVar(value=current_temp)

        temps = ("C", "F", "K")

        self.temp_btns = []

        for temp in temps:
            r = ttk.Radiobutton(self, text=temp, value=temp, variable=self.temp_selected)
            self.temp_btns.append(r)

        # set the radiobuttons to what is set in settings
        self.temp_selected.set(current_temp)

        # widget to select display mode
        self.display_name = ttk.Label(self, text="Display")
        current_display = settings.Settings.get_display_mode()
        self.display_selected = tk.StringVar(value=current_display)

        displays = ("gui", "cli")

        self.display_btns = []

        for display in displays:
            r = ttk.Radiobutton(self, text=display, value=display, variable=self.display_selected)
            self.display_btns.append(r)

        # set the radiobuttons to what is set in settings
        self.display_selected.set(current_display)

        # widget to select dark/light mode
        self.color_name = ttk.Label(self, text="Color Mode")
        current_color = settings.Settings.get_display_color()
        self.color_selected = tk.StringVar(value=current_color)

        colors = ("light", "dark")

        self.color_btns = []

        for color in colors:
            r = ttk.Radiobutton(self, text=color, value=color, variable=self.color_selected)
            self.color_btns.append(r)

        # set the radiobuttons to what is set in settings
        self.color_selected.set(current_color)

        # widget to change map view
        self.map_name = ttk.Label(self, text="Map Display")
        current_map = settings.Settings.get_map()
        self.map_selected = tk.StringVar(value=current_map)

        views = ("app", "web")

        self.view_btns = []

        for view in views:
            r = ttk.Radiobutton(self, text=view, value=view, variable=self.map_selected)
            self.view_btns.append(r)

        # set the radiobuttons to what is set in settings
        self.map_selected.set(current_map)

        # widget to close window
        self.close_win = close_win
        self.save_win = save_win

        self.close_btn = ttk.Button(self, text="Close", command=self.close_win)
        self.save_btn = ttk.Button(self, text="Save", command=self.save_win, style='Accent.TButton')

        # grid widgets
        row = 0
        index = 0 # to keep track of which setting we are one (temp, display, or color)

        names = [self.temp_name, self.display_name, self.color_name, self.map_name]
        radio_buttons = [self.temp_btns, self.display_btns, self.color_btns, self.view_btns]

        for btns in radio_buttons:
            # add name to column 0
            names[index].grid(row=row, column=0, padx=5, pady=5)

            # now add radio buttons for that setting
            for btn in btns:
                btn.grid(row=row, column=1, padx=5, pady=5)
                row += 1

            # add a separator
            sprtr = ttk.Separator(self, orient='horizontal')
            sprtr.grid(row=row, column=0, columnspan=2)

            row += 1
            index += 1

        self.close_btn.grid(row=row, column=0, padx=5, pady=5)
        self.save_btn.grid(row=row, column=1, padx=5, pady=5)

    def get_settings(self):
        return {"temp":self.temp_selected.get(), "display":self.display_selected.get(), "color":self.color_selected.get(), "map":self.map_selected.get()}

class WeatherWindow(tk.Frame):
    def __init__(self, fav_cities, api, access_settings, access_map):
        tk.Frame.__init__(self)

        self.api = api
        self.current_city = ""
        self.code = 0

        self.access_map = access_map

        # instance to get weather data from
        self.wthr = weather.Weather(self.api)

        # text to display on the favourite/unfavourite button, based on whether the city is favourited or not
        self.heart_full = "Unfavourite"
        self.heart_empty = "Favourite"

        self.enter_city_label = ttk.Label(self, text="Enter city name: ")

        # entry to get city name from user
        self.city_name = ttk.Entry(self)
        self.fav_cities = fav_cities

        # bind search box to enter key
        self.city_name.bind("<Return>", self.search_hit_enter)

        self.search_btn = ttk.Button(self, text="Search", command=self.search_city_from_entry, style='Accent.TButton')

        self.fav_button = ttk.Button(self, text=self.heart_empty, command=self.fav_this_city, style='Accent.TButton')
        # auto default fav button to disabled because we start out showing the weather of no city
        self.fav_button.config(state="disabled")

        # border for text box
        self.wthr_border = ttk.Frame(self, style='Card')

        # the large text box that will actually show the weather
        self.wthrbox = tk.Text(self.wthr_border, relief="flat")
        self.wthrbox_current_cursor = 1.0
        self.wthrbox.config(state="disabled")
        self.wthrbox.pack(fill="both", expand=True, padx=1, pady=1)

        # configure tags to be centered (like city name and temp)
        for tag_name in ["city_name", "city_temp", "city_desc", "error", "weather_data"]:
            if tag_name != "weather_data":
                self.wthrbox.tag_configure(tag_name, justify='center')

            self.wthrbox.tag_configure(tag_name, font=("normal"))

        self.wthrbox.tag_configure("city_temp", font=("bold", 15))
        self.wthrbox.tag_configure("city_name", font=("bold"))

        # tkinter treeview to display favourited cities
        self.columns = ("favourite_cities")
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings")

        self.tree.heading("favourite_cities", text="Favourite Cities")

        for city in self.fav_cities:
            self.tree.insert("", "end", values=(city,))

        self.tree.bind("<ButtonRelease-1>", self.item_selected_event)

        # add a scrollbar to treeview
        self.tree_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=self.tree_scroll.set)

        # add an image box to graphically display weather on top right corner
        self.img = tk.PhotoImage(file="icons/unknown.png")

        # add a settings button for user to access settings
        self.settings_btn = ttk.Button(self, text="Settings", command=access_settings)
        self.settings_app = None

        # add a button to open the map in a web browser
        self.browser_btn = ttk.Button(self, text="Open Map", command=self.open_map)

        # add a button to refresh city
        self.refresh_btn = ttk.Button(self, text="Refresh", command=self.refresh_city)

        # grid the widgets
        self.tree.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky='nsew')
        self.wthr_border.grid(row=1, column=4, columnspan=10, padx=5, pady=5, sticky='nsew')
        self.enter_city_label.grid(row=2, column=4, padx=5, pady=5, sticky='nsew')
        self.city_name.grid(row=2, column=5, padx=5, pady=5, sticky='nsew')
        self.search_btn.grid(row=2, column=6, padx=5, pady=5, sticky='nsew')
        self.fav_button.grid(row=2, column=13, padx=5, pady=5, sticky='nsew')
        self.settings_btn.grid(row=2, column=0, padx=5, pady=5, sticky='nsew')
        self.browser_btn.grid(row=2, column=1, padx=5, pady=5, sticky='nsew')
        self.refresh_btn.grid(row=2, column=2, padx=5, pady=5, sticky='nsew')

        self.tree_scroll.grid(row=1, column=3, sticky='ns')

    def open_map(self):
        current_city = self.wthr.city
        country = self.wthr.country

        if current_city:
            preferred_map = settings.Settings.get_map()

            if preferred_map == "web":
                webbrowser.get().open(f"https://www.google.com/maps/place/{current_city},{country}")
            else:
                self.access_map(current_city, country)
        else:
            messagebox.showerror("Error", "Cannot view map of city not selected")

    def item_selected_event(self, event):
        selected = self.tree.focus()
        temp = self.tree.item(selected, 'values')

        # check if user clicked on non-existent row
        if len(temp) < 1:
            return

        city = temp[0]

        self.search_city(city)

    # image_name will be OpenWeather's name (ex: 10d, 50d)
    def add_image_with_name(self, image_name):
        if image_name != "unknown":
            # if not unknown, the name is format of 'XXN', where X is a digit, and N is a letter
            image_name = image_name[:2] + 'n'

        image_path = f"icons/{image_name}.png"
        self.img = tk.PhotoImage(file=image_path)

        self.wthrbox.image_create(1.0, image=self.img)

    def search_hit_enter(self, event):
        self.search_city_from_entry()

    def search_city_from_entry(self):
        city = self.city_name.get()
        self.search_city(city)
        self.city_name.delete(0, "end")

    def refresh_city(self):
        city = self.wthr.city

        if city and city != "":
            # refresh weather data about city
            self.search_city(city)

    # instead of adding position numbers when adding text to the wthrbox, we can
    # add it here to make the code better and not have to reset the position numbers every time
    # i decide we should display more data
    def add_to_wthrbox(self, text, config):
        self.wthrbox.insert(self.wthrbox_current_cursor, text, config)

        for letter in text:
            if letter == "\n":
                self.wthrbox_current_cursor += 1

    def search_city(self, city):
        self.fav_cities = settings.Settings.get_fav_cities()
        self.wthr.get_weather(city)
        city = self.wthr.city

        if self.wthr.code != 200:
            # inform user of error
            self.wthrbox.config(state="normal")
            self.wthrbox.delete(1.0, "end")
            self.wthrbox.insert(1.0, self.wthr.msg, "error")
            self.wthrbox.config(state="disabled")

            self.fav_button.config(text=self.heart_empty)
            self.fav_button.config(state="disabled")

            self.add_image_with_name("unknown")
        else:
            # write new weather stuff in the text box
            self.wthrbox.config(state="normal")

            self.wthrbox.delete(1.0, "end")

            self.wthrbox_current_cursor = 4.0

            # show the data
            self.add_to_wthrbox(f"{self.wthr.desc}\n", "city_name")
            self.add_to_wthrbox(f"{self.wthr.temp} °{self.wthr.temp_method}\n", "city_temp")
            self.add_to_wthrbox(f"{city.title()}, {self.wthr.country}\n\n", "city_desc")

            self.add_to_wthrbox(f"Actual Temperature: {self.wthr.temp} °{self.wthr.temp_method}\n", "weather_data")
            self.add_to_wthrbox(f"Feels like: {self.wthr.feels_like} °{self.wthr.temp_method}\n", "weather_data")
            self.add_to_wthrbox(f"Range: {self.wthr.temp_range[0]} to {self.wthr.temp_range[1]} °{self.wthr.temp_method}\n\n", "weather_data")

            self.add_to_wthrbox(f"Humidity: {self.wthr.humidity} %\n", "weather_data")
            self.add_to_wthrbox(f"Visibility: {self.wthr.visibility} km\n", "weather_data")
            self.add_to_wthrbox(f"Pressure: {self.wthr.pressure} hPa\n", "weather_data")

            self.add_to_wthrbox(f"Wind speed: {self.wthr.wind_speed} km/h {self.wthr.wind_direction}\n\n", "weather_data")

            self.add_to_wthrbox(f"Last updated (local time): {self.wthr.current_time['hour']}:{self.wthr.current_time['minute']}:{self.wthr.current_time['second']} {['AM', 'PM'][self.wthr.current_time['hour_type']]}\n\n", "weather_data")

            self.add_to_wthrbox(f"Sunrise: {self.wthr.sunrise['hour']}:{self.wthr.sunrise['minute']}:{self.wthr.sunrise['second']} {['AM', 'PM'][self.wthr.sunrise['hour_type']]}\n", "weather_data")
            self.add_to_wthrbox(f"Sunset: {self.wthr.sunset['hour']}:{self.wthr.sunset['minute']}:{self.wthr.sunset['second']} {['AM', 'PM'][self.wthr.sunset['hour_type']]}\n", "weather_data")

            self.wthrbox.config(state="disabled")

            self.fav_button.config(state="normal")

            # change weather icon
            self.add_image_with_name(self.wthr.icon)

            # change favourite/unfavourite depending on whether it has been favourited or not
            if city in self.fav_cities:
                self.fav_button.config(text=self.heart_full)
            else:
                self.fav_button.config(text=self.heart_empty)

        self.current_city = city
        self.code = self.wthr.code

    def fav_this_city(self):
        city = self.current_city
        self.fav_cities = settings.Settings.get_fav_cities()

        # check if city is favourited or not
        if city not in self.fav_cities:
            # if it isn't, add it
            settings.Settings.add_fav_city(city)
            messagebox.showinfo(title="Success!", message=f"{city.title()} has been favourited!")

            # show full heart so user knows it is favourited
            self.fav_button.config(text=self.heart_full)

            # add favourite to favourites treeview
            self.tree.insert("", "end", values=(city,))
        else:
            settings.Settings.remove_fav_city(city)
            messagebox.showinfo(title="Success!", message=f"{city.title()} has been unfavourited.")

            # show empty heart to show it is not favourited
            self.fav_button.config(text=self.heart_empty)

            # delete city from favourites treeview
            x = self.tree.get_children()

            for item in x:
                if self.tree.item(item, 'values')[0] == city:
                    self.tree.delete(item)
                    break

class GUIMain(tk.Tk):
    def __init__(self, fav_cities, api):
        tk.Tk.__init__(self)

        self.title("Weather")

        # add forest theme
        self.colors_loaded = []
        self.bg_dark = "#313131"
        self.fg_dark = "#eeeeee"
        self.bg_light = "#ffffff"
        self.fg_light = "#313131"

        mode = settings.Settings.get_display_color()
        self.toggle_display_color(mode)

        # frames
        self.weather_frame = WeatherWindow(fav_cities, api, self.access_settings, self.access_map)
        self.settings_frame = SettingsWindow(lambda: self.close_win(self.settings_frame), self.save_win)
        self.map_frame = MapWindow(lambda: self.close_win(self.map_frame))

        self.weather_frame.pack(expand='yes')

    def access_settings(self):
        self.weather_frame.pack_forget()
        self.settings_frame.pack()

    def access_map(self, city, country):
        self.weather_frame.pack_forget()
        self.map_frame.change_location(city, country)
        self.map_frame.pack()

    # close frame
    def close_win(self, frame):
        frame.pack_forget()
        self.weather_frame.pack()

    # save settings and close settings window
    def save_win(self):
        # get current dark/light mode so that we don't try to reload same color because error will occur
        current_color = settings.Settings.get_display_color()
        saved_settings = self.settings_frame.get_settings()

        settings.Settings.save_temp_unit(saved_settings["temp"])
        settings.Settings.save_display_mode(saved_settings["display"])
        settings.Settings.save_map(saved_settings["map"])

        # refresh city in wthrbox
        self.weather_frame.refresh_city()
        # we intentionally save color later - because if the color isn't available, then we should not save that color to settings

        # TODO: add verification to check if color changed or not, otherwise error will occur
        if current_color != saved_settings["color"]:
            if self.toggle_display_color(saved_settings["color"]):
                # if color is available save it
                settings.Settings.save_display_color(saved_settings["color"])

        self.close_win(self.settings_frame)

    # toggle display color
    def toggle_display_color(self, color):
        # just_loaded is just to check whether this is the toggle_display_color call to load the new color
        # since we need to manually change the background colors of the frames, and the __init__ function of this class
        # loads the ttk theme (in this func) first, we need to make sure this function doesn't call those tk.Frames before
        # they are initialized
        just_loaded = False
        success = False

        if color in ["light", "dark"]:
            if color not in self.colors_loaded:
                try:
                    self.tk.call('source', f'forest-theme/forest-{color}.tcl')
                    self.colors_loaded.append(color)
                except:
                    print(f"Error: cannot find forest-{color} theme, which should have been included in the download.")
                    success = False

                just_loaded = True

            if color in self.colors_loaded:
                ttk.Style().theme_use(f'forest-{color}')

                # we need to manually change the background to black - otherwise the widgets will be dark mode but not the background
                if color == "dark" and not just_loaded:
                    self.weather_frame.configure(background=self.bg_dark)
                    self.settings_frame.configure(background=self.bg_dark)
                    self.map_frame.configure(background=self.bg_dark)
                    self.configure(background=self.bg_dark)

                    # manually change the color of the weather box otherwise it will not change
                    self.weather_frame.wthrbox.configure(background=self.bg_dark)
                    self.weather_frame.wthrbox.configure(foreground=self.fg_dark)
                elif color == "light" and not just_loaded:
                    self.weather_frame.configure(background=self.bg_light)
                    self.settings_frame.configure(background=self.bg_light)
                    self.map_frame.configure(background=self.bg_light)
                    self.configure(background=self.bg_light)

                    self.weather_frame.wthrbox.configure(background=self.bg_light)
                    self.weather_frame.wthrbox.configure(foreground=self.fg_light)

                success = True

        return success
