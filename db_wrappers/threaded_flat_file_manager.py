import os
import json
import shutil

class ThreadedFlatFileManager:
    """
        Extends FlatFileManager to handle multiple conversation threads per user.
        Each user has a folder, each thread has its own JSON file.
    """
    def __init__(self, base_dir="converstions"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        
    def _get_user_dir(self, user_id):
        """Return the directory path for a specific user."""
        user_dir = os.path.join(self.base_dir, str(user_id))
        os.makedirs(user_dir, exist_ok=True)
        return user_dir
    
    def get_threads(self, user_id):
        """Return a list of thread names for this user."""
        user_dir = self._get_user_dir(user_id)
        threads = []
        for file in os.listdir(user_dir):
            if file.endswith('.json'):
                threads.append(file[:-5])
            return threads

    def _get_thread_path(self, user_id, thread_name):
        """Return full file path for a user's thread file."""
        return os.path.join(self._get_user_dir(user_id), f"{thread_name}.json")
    
    def load_thread(self, user_id, thread_name):
        """Load the conversation thread if it exists, else return empty list."""
        path = self._get_thread_path(user_id, thread_name)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def save_thread(self, user_id, thread_name, messages):
        """Save a conversation thread (list of messages)."""
        path = self._get_thread_path(user_id, thread_name)
        try:
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(messages, file, indent=2)
        except IOError as e:
            print(f"Error saving thread file: {e}")

    def append_message(self, user_id, thread_name, message):
        """Add a new message to the thread and save."""
        messages = self.load_thread(user_id, thread_name)
        messages.append(message)
        self.save_thread(user_id, thread_name, messages)
        
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
    threaded_manager = ThreadedFlatFileManager(base_dir="conversations")
    threaded_manager.run_tests()  