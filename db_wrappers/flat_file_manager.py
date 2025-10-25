import os
import json
import shutil
from typing import List


class FlatFileManager:
    """
    Manages storing and retrieving chat conversations in flat JSON files.
    """

    def __init__(self, storage_dir="data"):
        """
        Initializes the FlatFileManager for a specific user.

        Args:
            storage_dir (str): The unique identifier for the user.
        """
        self.storage_dir = storage_dir
        self._ensure_storage_exists()

    def _ensure_storage_exists(self) -> None:
        """
        --- TODO 1: Create the storage directory ---
        Ensures that the directory for storing data files exists.
        If it doesn't exist, this method should create it.
        Hint: Use os.makedirs() and its `exist_ok` parameter.
        """
        os.makedirs(self.storage_dir, exist_ok=True)
        
    def _ensure_user_dir(self, user_id: str):
        """
        Creates and returns the directory path for a user.
        """
        user_path = os.path.join(self.storage_dir, user_id)
        os.makedirs(user_path, exist_ok=True)
        return user_path

    def get_conversation(self, user_id: str, thread_name: str):
        """
        --- TODO 4: Retrieve a user's conversation ---
        1 - Find the filepath in the conversations index
            - If DNE return empty list []
        2 - Reads the conversation from the JSON file.
            - If the file exists, load the JSON data and return it.
            - If the file does not exist it should return an empty list `[]` without raising an error.
            Hint: Use a try-except block to handle error case.
        """
        user_path = self._ensure_user_dir(user_id)
        filepath = os.path.join(user_path, f"{thread_name}.json")
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_conversation(self, user_id: str, thread_name: str, messages: List[any]):
        """
        --- TODO 5: Save a user's conversation ---
        1 - Add the conversation ID and filepath to self.conversation_index
        2 - Save conversation index to disk
            - T
        3 - Save the given list of messages to the storage dir/filepath as a JSON file.
            This method should overwrite the entire file with the new contents of the `messages` list.
            - Use JSON formatting to make the file human-readable (e.g., indentation).
            Hint: Use `json.dump()` with the `indent` parameter.
        """
        user_path = self._ensure_user_dir(user_id)
        filepath = os.path.join(user_path, f"{thread_name}.json")
        with open(filepath, "w") as f:
            json.dump(messages, f, indent=4)
