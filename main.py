import time
import os
from db_wrappers.flat_file_manager import FlatFileManager


def main():
    """
    Main function to run the Chai AI chat application using flat files.
    """
    print("Welcome to Chai!")

    # Configure flat-file storage directory
    storage_dir = "data"

    db_manager = FlatFileManager(storage_dir=storage_dir)

    user_id = input("Please enter your user ID to begin: ")

    # --- Thread selection (flat-file) ---
    # Naming scheme: conversation_id = f"{user_id}:{thread_name}"
    # Files stored as: f"{user_id}__{thread_name}.json"

    # Build list of existing thread names for this user from the index
    prefix = f"{user_id}:"
    threads = [cid.split(":", 1)[1] for cid in db_manager.conversations_index.keys() if cid.startswith(prefix)]

    thread_name = ""
    if threads:
        for i, t in enumerate(threads):
            print(f"{i}. {t}")
        print(f"{len(threads)}. Create new thread")

        user_selection = input("Enter a thread number: ")
        if not user_selection.isdigit():
            print("Not a number, exiting")
            return
        choice = int(user_selection)
        if choice > len(threads):
            print("Selection is too large of a number")
            return
        if choice == len(threads):
            thread_name = input("Enter thread name: ").strip() or "default"
        else:
            thread_name = threads[choice]
    else:
        # No threads yet; prompt for a new one and create an empty conversation record
        thread_name = input("Enter thread name: ").strip() or "default"

    # Ensure conversation exists in index (create empty if new)
    conversation_id = f"{user_id}:{thread_name}"
    if conversation_id not in db_manager.conversations_index:
        relative_filepath = f"{user_id}__{thread_name}.json"
        db_manager.save_conversation(conversation_id, relative_filepath, [])

    run_chat(db_manager, user_id, thread_name)


def run_chat(db_manager: FlatFileManager, user_id: str, thread_name: str) -> None:
    """
    Runs the chat loop for a specific conversation thread.
    """
    # Load and display existing conversation
    conversation_id = f"{user_id}:{thread_name}"
    start_time = time.perf_counter()
    messages = db_manager.get_conversation(conversation_id)
    end_time = time.perf_counter()
    duration = end_time - start_time

    if messages:
        print(f"\n--- Conversation History ({len(messages)} messages) ---")
        for message in messages:
            role = message['role'].capitalize()
            print(f"{role}: {message['content']}")
        print(f"Load time: {duration:.4f} seconds\n")

    print(f"Conversation: '{thread_name}'. Type 'exit' to quit.")

    while True:
        user_input = input("> ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        # Read-append-write using flat file manager
        start_time = time.perf_counter()

        # Ensure messages list is current
        if messages is None:
            messages = db_manager.get_conversation(conversation_id)

        # Append user message
        user_message = {"role": "user", "content": user_input}
        messages.append(user_message)

        # Create and append AI response
        ai_response = "This is a mock response from the AI."
        ai_message = {"role": "assistant", "content": ai_response}
        messages.append(ai_message)

        # Save updated conversation
        relative_filepath = db_manager.conversations_index.get(
            conversation_id, f"{user_id}__{thread_name}.json"
        )
        db_manager.save_conversation(conversation_id, relative_filepath, messages)

        end_time = time.perf_counter()
        duration = end_time - start_time

        print(f"AI: {ai_response}")
        print(f"(Operation took {duration:.4f} seconds)")


if __name__ == "__main__":
    main()
