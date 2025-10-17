import os
import json
import shutil
from typing import List

class ThreadedFlatFileManager:
    """
        Extends FlatFileManager to handle multiple conversation threads per user.
        Each user has a folder, each thread has its own JSON file.
    """
    def __init__(self, base_dir: str = "conversations") -> None:
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        
    def _get_user_dir(self, user_id: str) -> str:
        """Return the directory path for a specific user."""
        user_dir = os.path.join(self.base_dir, str(user_id))
        os.makedirs(user_dir, exist_ok=True)
        return user_dir
    
    def get_threads(self, user_id: str) -> List[str]:
        """Return a list of thread names for this user."""
        user_dir = self._get_user_dir(user_id)
        if not os.path.exists(user_dir):
            return []
        return [f[:-5] for f in os.listdir(user_dir) if f.endswith(".json")]

    def _get_thread_path(self, user_id: str, thread_name: str) -> str:
        """Return full file path for a user's thread file."""
        user_dir = self._get_user_dir(user_id)
        file_name = f"{thread_name}.json"
        return os.path.join(user_dir, file_name)
    
    def load_thread(self, user_id: str, thread_name: str) -> List[dict]:
        """Load the conversation thread if it exists, else return empty list."""
        path = self._get_thread_path(user_id, thread_name)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def save_thread(self, user_id: str, thread_name: str, messages: List[dict]) -> None:
        """Save a conversation thread (list of messages)."""
        path = self._get_thread_path(user_id, thread_name)
        try:
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(messages, file, indent=2)
        except IOError as e:
            print(f"Error saving thread file: {e}")

    def append_message(self, user_id: str, thread_name: str, message: dict) -> None:
        """Add a new message to the thread and save."""
        messages = self.load_thread(user_id, thread_name)
        messages.append(message)
        self.save_thread(user_id, thread_name, messages)
        
        # Not implemented in project
    def delete_thread(self, user_id: str, thread_name: str) -> bool:
        """Delete a specific thread for a user. Return True if successful."""
        path = self._get_thread_path(user_id, thread_name)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False
        
    def run_tests(self):
        print("Testing ThreadedFlatFileManager")
        user_id = "test_user"
        thread_name = "test_thread"
        messages = [{"role": "user", "content": "Hello from thread!"}]
        
        print("Testing save_thread()")
        self.save_thread(user_id, thread_name, messages)
        path = self._get_thread_path(user_id, thread_name)
        if not os.path.exists(path):
            print("Failed to save thread!")
            return
        print("Successfully saved thread!")
        
        print("Testing load_thread()")
        loaded_messages = self.load_thread(user_id, thread_name)
        if not loaded_messages:
            print("Failed to load thread!")
            return
        print("Successfully loaded thread!")
        
        print("Testing append_message()")
        new_message = {"role": "assistant", "content": "This is a response."}
        self.append_message(user_id, thread_name, new_message)
        updated_messages = self.load_thread(user_id, thread_name)
        if len(updated_messages) != 2:
            print("Failed to append message!")
            return
        print("Successfully appended message!")
        
        try:
            shutil.rmtree(os.path.join(self.base_dir, user_id))
            print("Deleted user directory")
        except OSError as e:
            print(f"Failed to delete user directory: {e}")
        
        print("All tests passed!")
        
if __name__ == "__main__":
    print("Testing ThreadedFlatFileManager")
    threaded_manager = ThreadedFlatFileManager(base_dir="conversations_test")
    threaded_manager.run_tests()  