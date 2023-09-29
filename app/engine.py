import tkinter as tk
from tkinter import Scrollbar
import os
import platform
import pygame
from app.parser import Parser
from app.action_processor import ActionProcessor
from app.event_handler import EventHandler
from app.sound_manager import SoundManager

class Engine:
    def __init__(self, root, data, game_objects, top_level_path):
        self.root = root
        self.data = data
        self.game_objects = game_objects
        self.parser = Parser()
        self.event_handler = EventHandler(self.game_objects)
        self.game_state = {
            "current_scene": "title",
            "current_location": 1,
            "location_name": '',
            "god_mode": False,
            "user_command": '',
            "previous_text": '',
        }
        self.sound_manager = SoundManager(f"{top_level_path}/data/echoes-of-time-v2-by-kevin-macleod-from-filmmusic-io.mp3", music_volume=0.5)
        self.sound_manager.play_music()
        self.action_processor = ActionProcessor(self.sound_manager)
        
        self.setup_ui()
        self.show_scene("title")

    def setup_ui(self):
        self.text_display = tk.Label(self.root, text="", wraplength=600, justify="left")
        self.text_display.pack()

        self.status_display = tk.Label(self.root, text="", wraplength=600, justify="left")
        self.status_display.pack()

        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack()

        self.input_label = tk.Label(self.input_frame, text="> ")
        self.input_label.pack(side=tk.LEFT)

        self.input_entry = tk.Entry(self.input_frame, width=50)
        self.input_entry.pack(side=tk.LEFT)

        self.input_entry.bind("<Return>", self.handle_input)

    def show_scene(self, scene_name, *args):

        scenes = {
            "title": self.title,
            "opening": self.opening,
            "help": self.help_func,
            "map": self.map_func,
            "playing": self.playing,
            "victory": self.victory,
            "defeat": self.defeat,
        }
        text = ""
        if args:
            text += args[0]
            text += '\n' + scenes.get(scene_name, self.title)()
        else:
            text = scenes.get(scene_name, self.title)()
        self.text_display.config(text=text)

        status_text = f"{self.game_objects['players'][0].state} @ {self.game_state['location_name']}"
        self.status_display.config(text=status_text)

    def handle_input(self, event):
        input_text = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        result = self.handle_user_input(input_text)
        self.show_scene(self.game_state['current_scene'], result)
        
    def run(self):
        self.root.mainloop()

    def process_parsed_text(self, parsed_text):
        result = ""
        if "start" == parsed_text[0]:
            if self.game_state['current_scene'] == "title":
                self.game_state['current_scene'] = "opening"
        elif "quit" == parsed_text[0]:
            return "Quitting..."
        elif "help" == parsed_text[0]:
            self.game_state["previous_scene"] = self.game_state['current_scene']
            self.game_state['current_scene'] = "help"
        elif "goto" == parsed_text[0] and self.game_state['current_scene'] == "playing" and self.game_state['god_mode']:
            if len(parsed_text) > 1 and parsed_text[1].isdigit():
                target_location = int(parsed_text[1])
                if target_location in self.game_objects['locations'].keys():
                    self.game_state["current_location"] = target_location
        elif "map" == parsed_text[0]:
            self.game_state["previous_scene"] = self.game_state['current_scene']
            self.game_state['current_scene'] = "map"
        elif "poweroverwhelming" == parsed_text[0] and self.game_state['current_scene'] == "playing":
            if not self.game_state['god_mode']:
                self.game_state['god_mode'] = True
            else:
                self.game_state['god_mode'] = False
        elif "disable" == parsed_text[0] and self.game_state['god_mode']:
            if len(parsed_text) > 1 and parsed_text[1].isdigit():
                if len(parsed_text) == 3 and parsed_text[2].isdigit():
                    start = int(parsed_text[1])
                    end = int(parsed_text[2])
                    for event_id in range(start, end + 1):
                        if event_id in self.game_objects['events'].keys():
                            self.game_objects['events'][event_id].state = 'inactive'
                else:
                    target_event = int(parsed_text[1])
                    self.game_objects['events'][target_event].state = 'inactive'
        elif "enable" == parsed_text[0] and self.game_state['god_mode']:
            if len(parsed_text) > 1 and parsed_text[1].isdigit():
                if len(parsed_text) == 3 and parsed_text[2].isdigit():
                    start = int(parsed_text[1])
                    end = int(parsed_text[2])
                    for event_id in range(start, end + 1):
                        if event_id in self.game_objects['events'].keys():
                            self.game_objects['events'][event_id].state = 'active'
                else:
                    target_event = int(parsed_text[1])
                    self.game_objects['events'][target_event].state = 'active'
        elif "music" == parsed_text[0] and self.game_state['current_scene'] != "playing":
            result = self.action_processor.process(parsed_text[0], None, None, self.game_state, *parsed_text[1:])
        else:
            self.game_state['user_command'] = parsed_text
        return result

    def handle_user_input(self, input_text: str):
        result = ""
        if self.game_state['current_scene'] == "help":
            self.game_state['current_scene'] = self.game_state['previous_scene']
            self.game_state['previous_scene'] = "help"
        elif self.game_state['current_scene'] == "map":
            self.game_state['current_scene'] = self.game_state['previous_scene']
            self.game_state['previous_scene'] = "map"
        elif self.game_state['current_scene'] == "opening":
            self.game_state['current_scene'] = "playing"
        elif input_text:
            parsed_text = self.parser.parse(input_text)
            if parsed_text:
                result = self.process_parsed_text(parsed_text)
                if result == "Quitting...":
                    quit(0)
                self.game_state['user_command'] = parsed_text
        return result


    def title(self):
        title_text = ""
        for index, line in enumerate(self.data['title']):
            title_text += f"{line}\n"

        message = "Type START to play"
        return f"{title_text}\n{message}"

    def opening(self):
        opening_text = ""
        for index, string_list in enumerate(self.data['opening']):
            for string_index, string in enumerate(string_list):
                opening_text += f"{string}\n"
        self.game_state["location_name"] = self.game_objects["locations"][self.game_state['current_location']].name
        return opening_text

    def help_func(self):
        return self.data['help']

    def map_func(self):
        return self.data['map']

    def generate_location_text(self, location):
        text = location.description
        if 0 < len(location.entities):
            text = f"{text}\nAround you, you can see:"
            for kind, obj_id in location.entities:
                entity = self.game_objects[f"{kind}s"][obj_id]
                text = f"{text}\n\t{entity.name}"
        return text

    def playing(self):
        text = self.generate_location_text(self.game_objects["locations"][self.game_state['current_location']])
        event_txt = ""
        command = self.game_state['user_command']
        if command and command != "":
            result = self.action_processor.process(
                                                command[0],
                                                self.game_objects["locations"][self.game_state['current_location']],
                                                self.game_objects,
                                                self.game_state,
                                                *command[1:]
                                                )
            if isinstance(result, str):
                text = self.generate_location_text(self.game_objects["locations"][self.game_state['current_location']])
                text = f"{text}\n\n {result}"
            elif isinstance(result, tuple):
                kind, target_obj_id = result
                if kind == "location":
                    self.game_state["current_location"] = target_obj_id
                    location = self.game_objects["locations"][target_obj_id]
                    self.game_state["location_name"] = location.name
                    text = self.generate_location_text(location)

            if "events" in self.game_objects:
                events = self.game_objects["events"]
                for event_id in events.keys():
                    if events[event_id].state == "active":
                        event_result = self.event_handler.process_event(events[event_id],
                                                                        self.game_state['current_location'],
                                                                        self.game_state["god_mode"])
                        event_txt += f"{event_result}"
                text += f"\n{event_txt}"
            self.game_state["previous_text"] = text
        if not command:
            text = self.game_state.get("previous_text", text)

        return text

    def victory(self):
        return self.data['victory']

    def defeat(self):
        return self.data['defeat']
