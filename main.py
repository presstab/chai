import time
import os
from db_wrappers.mongodb_manager import MongoDBManager


def main():
    """
    Main function to run the Chai AI chat application with MongoDB.
    """
    print("Welcome to Chai (MongoDB Edition)!")

    # --- TODO 1: Configure MongoDB Connection ---
    # Update this connection string for your MongoDB setup
    # For local: "mongodb://localhost:27017/"
    # For Atlas: "mongodb+srv://username:password@cluster.mongodb.net/"
    connection_string = None  # fixme!

    db_manager = MongoDBManager(connection_string=connection_string, database_name="chai_db")

    user_id = input("Please enter your user ID to begin: ")

    # --- TODO 2: List existing threads and let user choose ---
    # Steps:
    # 1. Get list of existing threads for this user using list_user_threads()
    # 2. If threads exist:
    #    - Print them out with numbers (e.g., "1. work_project")
    #    - Print an option to create a new thread (e.g., "N. Create new thread")
    #    - Get user's choice
    # 3. If no threads exist or user chooses new:
    #    - Prompt for a new thread name
    # 4. Store the selected/new thread_name

    threads = None  # fixme!
    thread_name = None  # fixme!

    # Your code here...

    run_chat(db_manager, user_id, thread_name)

    # Don't forget to close the connection when done!
    db_manager.close()


def run_chat(db_manager: MongoDBManager, user_id: str, thread_name: str) -> None:
    """
    Runs the chat loop for a specific conversation thread.
    """
    # --- TODO 3: Load and display existing conversation ---
    # Time how long it takes to load the conversation
    start_time = time.perf_counter()
    messages = None  # fixme! Use get_conversation
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

        # --- TODO 4: Append messages using the efficient append_message() method ---
        # Steps:
        # 1. Start performance timer
        # 2. Append user message using append_message()
        # 3. Create mock AI response
        # 4. Append AI response using append_message()
        # 5. Stop timer and calculate duration
        #
        # Note: We're calling append_message() TWICE (once for user, once for AI)
        # This is different from Lab 1 where we did one big write!

        start_time = None  # fixme!

        # Append user message
        user_message = {"role": "user", "content": user_input}
        # fixme! Use append_message

        # Create and append AI response
        ai_response = "This is a mock response from the AI."
        ai_message = {"role": "assistant", "content": ai_response}
        # fixme! Use append_message

        end_time = None  # fixme!
        duration = None  # fixme!

        print(f"AI: {ai_response}")
        print(f"(Operation took {duration:.4f} seconds)")


if __name__ == "__main__":
    main()