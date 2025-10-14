import time
import os
from db_wrappers.flat_file_manager import FlatFileManager

# test commit

def main():
    """
    Main function to run the Chai AI chat application.
    Handles the REPL (Read-Eval-Print Loop) for user interaction.
    """
    print("Welcome to Chai!")
    user_id = input("Please enter your user ID to begin: ")

    # Instantiate the FlatFileManager
    db_manager = FlatFileManager(storage_dir="data")

    # --- Multiple threads ---
    threads = db_manager.list_threads(user_id)

    if threads:
        print("Existing threads:")
        for i, t in enumerate(threads, start=1):
            print(f"{i}. {t}")
        print(f"{len(threads)+1}. Start a new thread")

        choice = input("Select a thread number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(threads):
            conversation_id = threads[int(choice) - 1]
        else:
            conversation_id = input("Enter a name for your new thread: ")
    else:
        conversation_id = input("No threads found. Enter a name for your new thread: ")

    run_chat(db_manager, user_id, conversation_id)


def run_chat(db_manager: FlatFileManager, user_id: str, conversation_id: str):
    """
    The main REPL chat loop.
    """
    # Load existing conversation
    start_time = time.time()
    messages = db_manager.get_conversation(user_id, conversation_id)
    end_time = time.time()
    duration = end_time - start_time

    if messages:
        print("Previous conversation:")
        for msg in messages:
            print(f"{msg['role'].capitalize()}: {msg['content']}")
        print(f"(Load time: {duration:.4f} seconds)")

    print(f"Conversation: '{conversation_id}'. Type 'exit' to quit.")

    while True:
        user_input = input("> ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        start_time = time.perf_counter()

        # Load conversation if empty
        if not messages:
            messages = db_manager.get_conversation(user_id, conversation_id)

        # Append user message
        messages.append({"role": "user", "content": user_input})

        # Mock AI response
        ai_response = "This is a mock response from the AI."
        messages.append({"role": "assistant", "content": ai_response})

        # Save the conversation
        relative_filepath = f"{conversation_id}.json"
        db_manager.save_conversation(user_id, conversation_id, relative_filepath, messages)

        # End timer
        end_time = time.perf_counter()
        duration = end_time - start_time

        print(f"AI: {ai_response}")
        print(f"(Operation took {duration:.4f} seconds)\n")


if __name__ == "__main__":
    main()
