from app.game_object import GameObject
from app.intractable import Intractable
from app.location import Location
from app.container import Container
from app.npc import Npc
from app.sound_manager import SoundManager
from app.transition import Transition
from app.player import Player
from app.journal import Journal

class ActionProcessor:
    """Processes commands from the user and executes them returning the results.
    """    
    def __init__(self, sound_manager: SoundManager):
        """Initializes the ActionProcessor class.

        Args:
            sound_manager (SoundManager): Instance of the SoundManager class.
        """        
        self.soundManager = sound_manager

    def look(self, search_location: Location, game_objects: dict[str, GameObject], *args) -> str:
        """Command to look at the current location or a specific object.

        Args:
            search_location (Location): Location object to search for entities.
            game_objects (dict[str, GameObject]): Dictionary of game objects.

        Returns:
            str: Description of the current location, a specific object, or error message.
        """
        if args:
            looking_for = args[0]
            entities = [
                game_objects[f'{kind}s'][obj_id]
                for kind, obj_id
                in search_location.entities
                if game_objects[f'{kind}s'][obj_id].name == looking_for
            ]
            if entities:
                if isinstance(entities[0], Container):
                    container = entities[0]
                    if container.inventory:
                        text = f'{container.description}\n\tinventory:'
                        for kind, obj_id in container.inventory:
                            text = f'{text}\n\t\t{game_objects[f"{kind}s"][obj_id].name}'
                        return text
                return entities[0].description
            return f"You can't seem to find any {looking_for}s here, try using the help command."

    def music(self, *args) -> str:
        """Command to control the music.

        Returns:
            str: Result of the command, or error message.
        """        
        if args:
            if "pause" == args[0]:  # Spacebar to play/pause music
                if self.soundManager.sound_enabled:
                    self.soundManager.pause_music()
                    return 'music is paused'
            elif "play" == args[0]:  # Spacebar to play/pause music
                if self.soundManager.sound_enabled:
                    self.soundManager.play_music()
                    return 'music is playing'
            elif "up" == args[0]:  # Up arrow to increase music volume
                    self.soundManager.volume_up()
                    return f"volume: {self.soundManager.music_volume}"

            elif "down" == args[0]:  # Down arrow to decrease music volume
                self.soundManager.volume_down()
                return f"volume: {self.soundManager.music_volume}"
        else:
            return 'Invalid usage of command [music]. requires at least one argument. please use the help command for more information'
    
    def talk(self, search_location: Location, game_objects: dict[str, GameObject], *args) -> str:
        """Command to talk to npcs and read journals.

        Args:
            search_location (Location): Location object to search for entities.
            game_objects (dict[str, GameObject]): Dictionary of game objects.

        Returns:
            str: Dialogue of the npc or journal, or error message.
        """        
        if args:
            talking = args[0]
            journals = [
                game_objects[f'{kind}s'][obj_id]
                for kind, obj_id
                in search_location.entities
                if game_objects[f'{kind}s'][obj_id].name == talking 
                and isinstance(game_objects[f'{kind}s'][obj_id], Journal)
            ]
            npcs = [
                game_objects[f'{kind}s'][obj_id]
                for kind, obj_id
                in search_location.entities
                if game_objects[f'{kind}s'][obj_id].name == talking 
                and isinstance(game_objects[f'{kind}s'][obj_id], Npc)
            ]
            if journals:
                journal = journals[0]
                text = f'IMPORTTANT:\n\t{journal.story}\n\n Journal log:\n\t{journal.dialogue}'
                return text
            elif npcs:
                npc = npcs[0]
                text = f'{npc.dialogue}'
                return text

            return f"You can't seem to find any {talking}s here, try using the help command."
        return "Please specify who or what you want to talk to, type help to learn more about talking you native language."

    def move(self, search_location: Location, game_objects: dict[str, GameObject], *args) -> tuple[str, int] or str:
        """Command to move to a different location.

        Args:
            search_location (Location): Location object to search for entities.
            game_objects (dict[str, GameObject]): Dictionary of game objects.

        Returns:
            tuple[str, int] or str: Reference to the new location, or error message.
        """ 
        if args:
            moving = args[0]
            transitions: list[Transition] = [
                game_objects[f'{kind}s'][obj_id]
                for kind, obj_id
                in search_location.entities
                if game_objects[f'{kind}s'][obj_id].name == moving
                and isinstance(game_objects[f'{kind}s'][obj_id], Transition)
            ]
            if transitions:
                transition: Transition = transitions[0] 
                if not transition.blocked:
                    return transition.target
                return f"You can't go that way because the {moving} is {transition.state}"
            return f"You can't move to the {moving}, try using the help command."

    def invalid(self) -> str:
        """Invalid command error message.

        Returns:
            str: Error message.
        """        
        return "command not found please use the help command to see valid commands and examples"

    def take(self, search_location: Location, game_objects: dict[str, GameObject], *args) -> str:
        """Command to take items from the current location or a container.

        Args:
            search_location (Location): Location object to search for entities.
            game_objects (dict[str, GameObject]): Dictionary of game objects.

        Returns:
            str: Result of the command, or error message.
        """        
        if args:
            if len(args) == 1:
                looking_for = args[0]
                items = [
                    (kind, obj_id)
                    for kind, obj_id
                    in search_location.entities
                    if game_objects[f'{kind}s'][obj_id].name == looking_for
                    and not isinstance(game_objects[f'{kind}s'][obj_id], Transition)
                    and not isinstance(game_objects[f'{kind}s'][obj_id], Npc)
                ]
                player = game_objects['players'][0]
                if items:
                    item = items[0]
                    player.inventory.append(
                        search_location.entities.pop(search_location.entities.index(item))
                    )
                    kind, obj_id = item
                    return f"You pickup the {game_objects[f'{kind}s'][obj_id].name}."
                return f"You can't pick up the {looking_for}."
            if len(args) == 2:
                looking_for = args[0]
                container = args[1]
                containers = [
                    game_objects[f'{kind}s'][obj_id]
                    for kind, obj_id
                    in search_location.entities
                    if game_objects[f'{kind}s'][obj_id].name == container
                ]
                player = game_objects['players'][0]
                if containers:
                    container = containers[0]
                    if not isinstance(container, Container):
                        return f"{container.name.capitalize()} is not a container."
                    items = [
                        (kind, obj_id)
                        for kind, obj_id
                        in container.inventory
                        if game_objects[f'{kind}s'][obj_id].name == looking_for
                        and not isinstance(game_objects[f'{kind}s'][obj_id], Location)
                        and not isinstance(game_objects[f'{kind}s'][obj_id], Npc)
                    ]
                    if items:
                        item = items[0]
                        player.inventory.append(
                            container.inventory.pop(container.inventory.index(item))
                        )
                        kind, obj_id = item
                        return f"You take the {game_objects[f'{kind}s'][obj_id].name} from inside the {container.name}."

                    return f"You can't take the {looking_for} from the {container.name}"
                return f"You can't seem to find a {container} here."

    def drop(self, search_location: Location, game_objects: dict[str, GameObject], *args) -> str:
        """Command to drop items from the player's inventory or a container.

        Args:
            search_location (Location): Location object to search for entities.
            game_objects (dict[str, GameObject]): Dictionary of game objects.

        Returns:
            str: Result of the command, or error message.
        """        
        if args:
            if len(args) == 1:
                looking_for = args[0]
                player = game_objects['players'][0]
                items = [
                    (kind, obj_id)
                    for kind, obj_id
                    in player.inventory
                    if game_objects[f'{kind}s'][obj_id].name == looking_for
                ]
                if items:
                    item = items[0]
                    search_location.entities.append(
                        player.inventory.pop(player.inventory.index(item))
                    )
                    kind, obj_id = item
                    return f"You drop the {game_objects[f'{kind}s'][obj_id].name} on the ground."
                return f"You don't have a {looking_for}."
            if len(args) == 2:
                looking_for = args[0]
                container = args[1]
                containers = [
                                game_objects[f'{kind}s'][obj_id]
                                for kind, obj_id
                                in search_location.entities
                                if game_objects[f'{kind}s'][obj_id].name == container
                             ]
                player = game_objects['players'][0]
                if containers:
                    container = containers[0]
                    if not isinstance(container, Container):
                        return f"{container.name.capitalize()} is not a container."
                    items = [
                                (kind, obj_id)
                                for kind, obj_id
                                in player.inventory
                                if game_objects[f'{kind}s'][obj_id].name == looking_for
                            ]
                    if items:
                        item = items[0]
                        container.inventory.append(
                            player.inventory.pop(player.inventory.index(item))
                        )
                        kind, obj_id = item
                        return f"You put the {game_objects[f'{kind}s'][obj_id].name} in the {container.name}."
                    return f"You don't have a {looking_for}."
                return f"You can't seem to find a {container} here."

    def inventory(self, game_objects: dict[str, GameObject], *args) -> str:
        """Command to view the player's inventory.

        Args:
            game_objects (dict[str, GameObject]): Dictionary of game objects.

        Returns:
            str: Status of the player's inventory, or error message.
        """       
        player: Player = game_objects['players'][0]
        if len(args) == 1:
            looking_for = args[0]
            player = game_objects['players'][0]
            items = [
                (kind, obj_id)
                for kind, obj_id
                in player.inventory
                if game_objects[f'{kind}s'][obj_id].name == looking_for
            ]
            if items:
                item = items[0]
                kind, obj_id = item
                item_obj = game_objects[f'{kind}s'][obj_id]
                text = f"{item_obj.name}: {item_obj.description}"
                if kind == 'container':
                    items = [
                        (kind, obj_id)
                        for kind, obj_id
                        in item_obj.inventory
                    ]
                    if items:
                        text = f'{text}\n\tinventory:'
                        for item in items:
                            kind, obj_id = item
                            text = f"{text}\n\t\t{game_objects[f'{kind}s'][obj_id].name}"
                return text
            return f"You don't have a {looking_for}."
        if len(args) == 2:
            looking_for = args[1]
            player = game_objects['players'][0]
            containers = [
                game_objects[f'{kind}s'][obj_id]
                for kind, obj_id
                in player.inventory
                if game_objects[f'{kind}s'][obj_id].name == args[0]
                and isinstance(game_objects[f'{kind}s'][obj_id], Container)
            ]
            if containers:
                container = containers[0]
                items = [
                    (kind, obj_id)
                    for kind, obj_id
                    in container.inventory
                    if game_objects[f'{kind}s'][obj_id].name == looking_for
                ]
                if items:
                    item = items[0]
                    kind, obj_id = item
                    return f"{game_objects[f'{kind}s'][obj_id].name}: {game_objects[f'{kind}s'][obj_id].description}"
            return f"You don't have a {looking_for}."

        items = [
            (kind, obj_id)
            for kind, obj_id
            in player.inventory
        ]
        if items:
            text = '\ninventory:'
            for item in items:
                kind, obj_id = item
                text = f"{text}\n\t{game_objects[f'{kind}s'][obj_id].name}"
            return text
        return "Your inventory is empty."

    def use(self, search_location: Location, game_objects: dict[str, GameObject], *args) -> str:
        """Command to use items on other items or intractables.

        Args:
            search_location (Location): Location object to search for entities.
            game_objects (dict[str, GameObject]): Dictionary of game objects.

        Returns:
            str: Result of the command, or error message.
        """        
        if len(args) == 1:
            target = args[0]
            intractables: list[Intractable] = [
                game_objects[f'{kind}s'][obj_id]
                for kind, obj_id
                in search_location.entities
                if game_objects[f'{kind}s'][obj_id].name == target
                and isinstance(game_objects[f'{kind}s'][obj_id], Intractable)
            ]
            if intractables:
                intractable: Intractable = intractables[0]
                return intractable.cycle()
            return f"You can't use the {target} right now."
        if len(args) == 2:
            key_name = args[0]
            target_name = args[1]

            keys = [
                (kind, obj_id)
                for kind, obj_id
                in search_location.entities
                if game_objects[f'{kind}s'][obj_id].name == key_name
            ]
            if not keys:
                player = game_objects['players'][0]
                keys = [
                    (kind, obj_id)
                    for kind, obj_id
                    in player.inventory
                    if game_objects[f'{kind}s'][obj_id].name == key_name
                ]
            if not keys:
                return f"You don't have a {key_name} and there isn't one near you either."
            targets = [
                game_objects[f'{kind}s'][obj_id] 
                for kind, obj_id
                in search_location.entities
                if game_objects[f'{kind}s'][obj_id].name == target_name
                and isinstance(game_objects[f'{kind}s'][obj_id], Intractable)
            ]
            if targets:
                key = keys[0]
                target: Intractable = targets[0]
                return target.unlock(key, key_name)
            return f"There isn't a {target_name} here."

        if len(args) < 1:
            return 'Invalid usage of command [use]. requires at least one argument. please use the help command for more information'

    def process(self, command: str, search_location: Location, game_objects: dict[str, GameObject], game_state: dict[str, any], *args) -> tuple[str, int] or str:
        """Processes the command and returns the result.

        Args:
            command (str): Command to process.
            search_location (Location): Location object to search for entities.
            game_objects (dict[str, GameObject]): Dictionary of game objects.
            game_state (dict[str, any]): Current game state.

        Returns:
            tuple[str, int] or str: Result of the command, or error message.
        """        
        if command == 'look':
            return self.look(search_location, game_objects, *args)
        if command == "move":
            return self.move(search_location, game_objects, *args)
        if command == 'take':
            return self.take(search_location, game_objects, *args)
        if command == 'drop':
            return self.drop(search_location, game_objects, *args)
        if command == 'inventory':
            return self.inventory(game_objects, *args)
        if command == 'use':
            return self.use(search_location, game_objects, *args)
        if command == 'talk':
            return self.talk(search_location, game_objects, *args)
        if command == 'music':
            return self.music(game_state, *args)
        return self.invalid()
    
