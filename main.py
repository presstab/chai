import time
import os
from db_wrappers.flat_file_manager import FlatFileManager
    

def main():
    
    """
    Main function to run the Chai AI chat application.
    Handles the REPL (Read-Eval-Print Loop) for user interaction.
    """
    print("Welcome to Chai!")
    user_id = input("Please enter your user ID to begin: ").strip()

    db_manager = FlatFileManager(storage_dir="data")

    user_dir = os.path.join("data", user_id)
    os.makedirs(user_dir, exist_ok=True)

    threads = [f.replace(".json", "") for f in os.listdir(user_dir) if f.endswith(".json")]
    if threads:
        print("\nAvailable conversation threads:")
        for t in threads:
            print(f" - {t}")
    else:
        print("\nNo existing conversations found for this user.")

    thread_name = input("\nEnter thread name (existing or new): ").strip()
    if not thread_name:
        thread_name = "default"

    run_chat(db_manager, user_id, thread_name)


def run_chat(db_manager: FlatFileManager, user_id: str, thread_name: str):
    start_time = time.perf_counter()
    messages = db_manager.get_conversation(user_id, thread_name)
    end_time = time.perf_counter()
    print(f"\nLoaded thread '{thread_name}' in {end_time - start_time:.4f} seconds.")

    if messages:
        print("\nPrevious messages:")
        for message in messages:
            print(f"{message['role']}: {message['content']}")

    print("\nType your message below (or type 'exit' to quit):\n")

    while True:
        user_input = input("> ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        start_time = time.perf_counter()

        messages.append({"role": "user", "content": user_input})
        ai_response = "This is a mock response from the AI."
        messages.append({"role": "assistant", "content": ai_response})

        db_manager.save_conversation(user_id, thread_name, messages)

        end_time = time.perf_counter()
        print(f"AI: {ai_response}")
        print(f"(Operation took {end_time - start_time:.4f} seconds)\n")

if __name__ == "__main__":
    main()

