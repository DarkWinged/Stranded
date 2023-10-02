#! /usr/bin/env python3
# James L. Rogers | github.com/DarkWinged

#imports
import os
import json
import tkinter as tk
from app.engine import Engine
from app.event import Event
from app.npc import Npc
from app.location import Location
from app.item import Item
from app.transition import Transition
from app.player import Player
from app.container import Container
from app.journal import Journal


def load_data() -> dict[str, any]:
    data = {}
    with open(
        f"{'/'.join(os.path.abspath(__file__).split('/')[:-1])}/data/title.txt", 
        'r',
        encoding="utf-8"
        ) as title_file:
        data['title'] = title_file.readlines()

    with open(
        f"{'/'.join(os.path.abspath(__file__).split('/')[:-1])}/data/opening.txt",
        "r",
        encoding="utf-8"
        ) as plot:
        plot = plot.read().splitlines()
    plot_splice = []
    splice_len = 50
    for i in range(0, len(plot), splice_len):
        plot_splice.append(plot[i:i+splice_len])
    data['opening'] = plot_splice

    with open(
              f"{'/'.join(os.path.abspath(__file__).split('/')[:-1])}/data/help.txt",
              "r",
              encoding="utf-8"
              ) as help_file:
        data['help'] = help_file.read()
    
    with open(
              f"{'/'.join(os.path.abspath(__file__).split('/')[:-1])}/data/map.txt",
              "r",
              encoding="utf-8"
              ) as map_file:
        data['map'] = map_file.read()

    object_types = ['locations', 'items', 'transitions', 'players', 'containers', 'npcs', "journals", 'events']

    for object_type in object_types:
        with open(
            f"{'/'.join(os.path.abspath(__file__).split('/')[:-1])}/data/{object_type}.json",
            "r",
            encoding="utf-8"
            ) as loading:
            data[object_type] = json.load(loading)
    
    with open(
        f"{'/'.join(os.path.abspath(__file__).split('/')[:-1])}/data/victory.txt", 
        'r',
        encoding="utf-8"
        ) as victory_file:
        data['victory'] = victory_file.read()
    
    with open(
        f"{'/'.join(os.path.abspath(__file__).split('/')[:-1])}/data/defeat.txt", 
        'r',
        encoding="utf-8"
        ) as defeat_file:
        data['defeat'] = defeat_file.read()

    return data

def load_game_objects(data: dict[str, any]):
    objects = {}

    objects['npcs'] = {}
    for npc in data['npcs']:
        npc_obj = Npc(npc['obj_id'],
                    npc['name'],
                    npc['description'],
                    npc['state'],
                    npc.get('inventory', []),
                    npc.get('dialogue', [])
                    )
        objects['npcs'][npc_obj.obj_id] = npc_obj

    objects['locations'] = {}
    for location in data['locations']:
        entities = []
        if 'entities' in location.keys():
            for entity in location['entities']:
               entities.append((entity['kind'], entity['obj_id']))
        location_obj = Location(location['obj_id'],
                                location['name'],
                                location['description'],
                                location.get('entities', [])
                                )
        objects['locations'][location_obj.obj_id] = location_obj

    objects['journals'] = {}
    for journal in data['journals']:
        journal_obj = Journal(journal['obj_id'],
                        journal['name'],
                        journal['description'],
                        journal['dialogue'],
                        journal['story']
                        )
        objects['journals'][journal_obj.obj_id] = journal_obj

    objects['items'] = {}
    for item in data['items']:
        item_obj = Item(item['obj_id'], item['name'], item['description'], None)
        objects['items'][item_obj.obj_id] = item_obj

    objects['transitions'] = {}
    for transition in data['transitions']:
        transition_obj = Transition(transition['obj_id'],
                                    transition['name'],
                                    transition['description'],
                                    transition['state'],
                                    transition['state_descriptions'],
                                    transition['state_transitions'],
                                    transition['state_list'],
                                    transition.get('key_info', {}),
                                    transition['target'],
                                    transition['blocking_states']
                                    )
        objects['transitions'][transition_obj.obj_id] = transition_obj

    objects['players'] = {}
    for player in data['players']:
        inventory = []
        if player.get('inventory', []):
            for item in player['inventory']:
                inventory.append((item['kind'], item['obj_id']))
        player_obj = Player(player['obj_id'],
                            player['name'],
                            player['description'],
                            player['state'],
                            player.get('inventory', [])
                            )
        objects['players'][player_obj.obj_id] = player_obj

    objects['containers'] = {}
    for container in data['containers']:
        inventory = []
        if container.get('inventory', []):
            for item in container['inventory']:
                inventory.append((item['kind'], item['obj_id']))
        container_obj = Container(container['obj_id'],
                                  container['name'],
                                  container['description'],
                                  container['state'],
                                  container.get('inventory', [])
                                  )
        objects['containers'][container_obj.obj_id] = container_obj

    objects['events'] = {}
    for event_data in data['events']:
        # Convert event_data to Event object
        event = Event(
            event_data['obj_id'],
            event_data['name'],
            event_data['description'],
            event_data['state'],
            event_data['triggers'],
            event_data['affected_objects'],
            event_data['change']
        )
        objects['events'][event.obj_id] = event

    return objects


def main():
    top_level_path = os.path.dirname(os.path.abspath(__file__))

    # Load game data and objects
    data = load_data()
    game_objects = load_game_objects(data)

    # Create a Tkinter root window
    root = tk.Tk()
    root.title("Text Adventure Game")

    # Create an instance of the Engine class
    engine = Engine(root, data, game_objects, top_level_path)

    # Run the game loop
    engine.run()

if __name__ == "__main__":
    main()
