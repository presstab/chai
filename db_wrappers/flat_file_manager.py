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
        self.conversation_index = {} 
        self._init_index()

    def _ensure_storage_exists(self) -> None:
        """
        --- TODO 1: Create the storage directory ---
        Ensures that the directory for storing data files exists.
        If it doesn't exist, this method should create it.
        Hint: Use os.makedirs() and its `exist_ok` parameter.
        """
        os.makedirs(self.storage_dir, exist_ok=True)

    def _init_index(self) -> None:
        """
        --- TODO 2: Load the conversations index file
        1 - Check for the existence of self.storage_dir/conversations.json
        2 - If DNE, the create and save to disk using self.save_index()
        3 - Load the contents of conversations.json into self.conversation_index dictionary
        """
        index_file = os.path.join(self.storage_dir, "conversations.json")

        if not os.path.exists(index_file):
            self.save_index()

        try:
            with open(index_file, "r", encoding="utf-8") as f:
                self.conversation_index = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self.conversation_index = {}
            self.save_index()

    def save_index(self) -> None:
        """
        --- TODO 3: Save the conversations index to disk ---
        This method should save the current state of self.conversation_index 
        to the conversations.json file in the storage directory.
        Ensure the JSON is human-readable by using proper formatting.
        Hint: Use json.dump() with the 'indent' parameter for readable formatting.
        """
        index_file = os.path.join(self.storage_dir, "conversations.json")
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(self.conversation_index, f, indent=4)

    def get_conversation(self, user_id: str, conversation_id: str) -> List[any]:
        """
        --- TODO 4: Retrieve a user's conversation ---
        1 - Find the filepath in the conversations index
            - If DNE return empty list []
        2 - Reads the conversation from the JSON file.
            - If the file exists, load the JSON data and return it.
            - If the file does not exist it should return an empty list `[]` without raising an error.
            Hint: Use a try-except block to handle error case.
        """
        if user_id not in self.conversation_index:
            return []

        if conversation_id not in self.conversation_index[user_id]:
            return []

        file_path = os.path.join(self.storage_dir, self.conversation_index[user_id][conversation_id])
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                conversation_data = json.load(f)
                return conversation_data
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_conversation(self, user_id: str, conversation_id: str, relative_filepath: str, messages: List[any]) -> None:
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
        if user_id not in self.conversation_index:
            self.conversation_index[user_id] = {}

        self.conversation_index[user_id][conversation_id] = relative_filepath

        self.save_index()

        conversation_path = os.path.join(self.storage_dir, relative_filepath)
        os.makedirs(os.path.dirname(conversation_path), exist_ok=True)
        with open(conversation_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=4)

    def list_threads(self, user_id: str) -> List[str]:
        """
        --- TODO 6: List all threads for a user ---
        Returns a list of conversation IDs (threads) for a given user_id.
        If the user has no threads, returns an empty list.
        """
        if user_id not in self.conversation_index:
            return []
        return list(self.conversation_index[user_id].keys())

    def run_tests(self):
        print("Testing FlatFileManager._ensure_storage_exists()")
        # manually check that file exists
        if not os.path.isdir(self.storage_dir):
            print("Failed to create directory!")
            return

        print("Testing FlatFileManager.save_conversation()")
        messages = [{"role": "user", "content": "hello world"}]
        conversation_id = "test_user"
        relative_filepath = "test_user.json"
        user_id = "test_user"
        self.save_conversation(user_id, conversation_id, relative_filepath, messages)
        filepath = os.path.join(self.storage_dir, relative_filepath)
        if not os.path.exists(filepath):
            print("Failed to save conversation!")
            return
        print("Successfully saved conversation!")

        print("Testing FlatFileManager.get_conversation()")
        read_messages = self.get_conversation(user_id, conversation_id)
        if not read_messages:
            print("Failed to get conversation!")
            return
        print("Successfully retrieved conversation!")

        print("Testing FlatFileManager.list_threads()")
        threads = self.list_threads(user_id)
        if not threads:
            print("Failed to list threads!")
            return
        print(f"Threads for user {user_id}: {threads}")

        try:
            shutil.rmtree(self.storage_dir)
            print("Deleted storage directory")
        except OSError as e:
            print(f"Failed to delete storage directory: {e}")

        print("All tests passed!")

if __name__ == "__main__":
    print("Testing FlatFileManager")
    manager = FlatFileManager(storage_dir="data_test")
    manager.run_tests()
