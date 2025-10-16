import time
import os
from db_wrappers.flat_file_manager import FlatFileManager
from db_wrappers.threaded_flat_file_manager import ThreadedFlatFileManager
from datetime import datetime
import random
from db_wrappers.mongodb_manager import MongoDBManager

# Generate AI Mock Responses
def generated_ai_response(user_input: str) -> str:
    """A mock AI response based on user input."""
    responses_question = [
        "Hmm, that's an interesting question!",
        "Let me think about that for a second...",
        "What do *you* think?",
        "That's a tough one. What's your take?"
    ]
    responses_greeting = [
        "Hey there!",
        "Hi! How are you feeling today?",
        "Yo! What's up?",
        "Hello again, friend!"
    ]
    responses_statement = [
        "Got it. Sounds cool!",
        "Oh wow, that's pretty neat.",
        "I totally get what you mean.",
        "Okay, tell me more about that!"
    ]
    responses_emotional = [
        "That sounds exciting!",
        "That must be tough.",
        "Aww, I'm here for you.",
        "That's awesome! Keep going!"
    ]
    text = user_input.lower()
    if any(greet in text for greet in ["hello", "hi", "hey", "yo"]):
        return random.choice(responses_greeting)
    elif any(emo in text for emo in ["happy", "sad", "excited", "angry", "tired"]):
        return random.choice(responses_emotional)
    elif text.endswith("?"):
        return random.choice(responses_question)
    else:
        return random.choice(responses_statement)

# For Lab 1, Flat File Edition
def main():
    """
    Main function to run the Chai AI chat application.
    Handles the REPL (Read-Eval-Print Loop) for user interaction.
    """
    print("Welcome to Chai!")
    user_id = input("Please enter your user ID to begin: ").strip().lower()
    if not user_id:
        print("User ID cannot be empty. Exiting.")
        return

    # --- TODO 1: Instantiate the Database Wrapper ---
    # Create an instance of the FlatFileManager,
    # This object will handle all our file reading and writing.
    # Specify the storage directory as "data"
    db_manager = FlatFileManager(storage_dir="data")
    
    # --- TODO 6 (do this last): Create a way for a user_id to have multiple conversation threads
    # Requirements:
    #   - If user already exists, then have the user select which thread (conversation_id) they want to use
    #       - Give the option to use a new thread
    #   - Proceed to run_chat() with the correct conversation_id
    #   Hint: This is not a "clean" addition, you may need to restructure how data is stored and indexed
    #         There are many ways to do this. Devise a plan and implement your own solution.
    
    # Thread Selection
    thread_manager = ThreadedFlatFileManager(base_dir="conversations")
    
    threads = thread_manager.get_threads(user_id)
    if threads:
        print("\nAvailable threads:")
        for idx, name in enumerate(threads, start=1):
            print(f"{idx} - {name}")
        print(f"{len(threads)+1} - Start a new thread")
        choice = input("Select a thread number or press Enter to create new: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(threads):
            thread_name = threads[int(choice)-1]
        else:
            thread_name = input("Enter a name for the new thread: ").strip()
            if not thread_name:
                thread_name = "untitled"
            # create empty file for clarity
            thread_manager.save_thread(user_id, thread_name, [])
    else:
        print("No existing threads found.")
        thread_name = input("Enter a name for your new thread: ").strip()
        if not thread_name:
            thread_name = "untitled"
        thread_manager.save_thread(user_id, thread_name, [])

    # conversation id must match user+thread so things stay synced
    conversation_id = f"{user_id}_{thread_name}"
    
    # Coversation Selection
    print(f"\nHello, {user_id.capitalize()}!")
    print("What would you like to do?")
    print("1 - Start a new conversation")
    print("2 - Continue an existing conversation")
    choice = input("Enter 1 or 2: ").strip()
    if choice == "2":
        # legacy conversation listing; if your FlatFileManager has an index use it, otherwise just continue
        existing_conversations = []
        try:
            existing_conversations = [cid for cid in db_manager.conversations_index.keys() if cid.startswith(f"{user_id}_")]
        except Exception:
            existing_conversations = []
        if existing_conversations:
            print("\nExisting conversations:")
            for idx, cid in enumerate(existing_conversations, start=1):
                print(f"{idx} - {cid}")
            sel = input("Select (or press Enter to use current thread): ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(existing_conversations):
                conversation_id = existing_conversations[int(sel)-1]
        else:
            print("No existing conversations found. Starting a new conversation.")
            # conversation_id remains tied to thread

    print(f"\nUsing conversation ID: {conversation_id}\n")
    run_chat(db_manager, thread_manager, user_id, thread_name, conversation_id)

def run_chat(db_manager: FlatFileManager, thread_manager: ThreadedFlatFileManager, user_id: str, thread_name: str, conversation_id: str) -> None:
    # --- TODO 2: Check if conversation already exists, printout conversation if so ---
    #   - Add a timer that times how long it took to use get_conversation and print the results after
    start_time = time.perf_counter()
    messages = thread_manager.load_thread(user_id, thread_name)
    if not messages:
        try:
            messages = db_manager.get_conversation(conversation_id)
        except Exception:
            messages = []
    end_time = time.perf_counter()
    duration = end_time - start_time
    print(f"Load time: {duration:.4f} seconds\n")
    
    # --- TODO 4: Implement the Read-Append-Write Cycle ---
    # 1. Get the entire conversation history from the file.
    if messages:
        print(f"Loaded {len(messages)} previous messages:")
        for msg in messages:
            ts = msg.get("timestamp", "")
            role = msg.get("role", "user").capitalize()
            content = msg.get("content", "")
            if ts:
                print(f"[{ts}] {role}: {content}")
            else:
                print(f"{role}: {content}")
    else:
        print("Starting a new conversation.\n")
    
    print(f"Conversation: '{thread_name}' (User ID: '{user_id}')")
    print("Type 'exit' to quit.\n")
    
    while True:
        user_input = input("> ").strip()
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        if not user_input.strip():
            print("Please enter a valid message.")
            continue
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- TODO 3: Start the performance timer ---
        # Record the start time before performing the database operations.
        # Use time.perf_counter() for high precision.
        start_time = time.perf_counter()

        # 2. Append the new user message to the list of messages using messages.append()
        #    Each message should be a dictionary, e.g., {"role": "user", "content": user_input}
        user_message = {"role": "user", "content": user_input, "timestamp": timestamp}
        messages.append(user_message)
        print(f"You: ({timestamp}): {user_input}")

        # 3. Create a mock AI response and append it to the list.
        #    The AI response should also be a dictionary using format: {"role": "assistant", "content": ai_response}
        ai_response = generated_ai_response(user_input)
        ai_message = {"role": "assistant", "content": ai_response, "timestamp": timestamp}
        messages.append(ai_message)
        print(f"AI: {ai_response}")

        # 4. Save the *entire*, updated list of messages back to the file.
        #    Call your db_manager's save method.
        try:
            # fixme! use db manager save method here
            db_manager.save_conversation(conversation_id, f"{conversation_id}.json", messages)
        except Exception:
            pass
        thread_manager.save_thread(user_id, thread_name, messages)
        # ----------------------------------------------------

        # --- TODO 5: Stop the timer and calculate duration ---
        # Record the end time and calculate the difference to see how long the
        # entire read-append-write cycle took.
        end_time = time.perf_counter()
        
        # ---------------------------------------------------
        print(f"(Operation took {duration:.4f} seconds)\n")
    

# For Lab 2, MongoDB Edition
def main():
    """
    Main function to run the Chai AI chat application with MongoDB.
    """
    print("Welcome to Chai (MongoDB Edition)!")

    # --- TODO 1: Configure MongoDB Connection ---
    # Update this connection string for your MongoDB setup
    # For local: "mongodb://localhost:27017/"
    # For Atlas: "mongodb+srv://username:password@cluster.mongodb.net/"

    # example for Mongo Atlas
    # **IMPORTANT** You must set the environment variable MONGO_KEY from your terminal if you are using Atlas
    # This is something that does not persist from one terminal session to another, so remember to do it!
    # For Windows Command Prompt: set MONGO_KEY=password_here
    # For Windows PowerShell: $env:MONGO_KEY = "lab2mongodb"
    # For Mac/Linux: export MONGO_KEY="password_here"
    user = os.getenv("MONGO_USER") # replace with your username in Atlas
    password = os.getenv("MONGO_PASSWORD")
    srv = os.getenv("MONGO_SRV")
    cluster = os.getenv("MONGO_CLUSTER")
    requirements = os.getenv("MONGO_REQURIREMENTS")
    # Edit the url to use the url it gives you - remember to enter username and password as is done below
    connection_string = f"{srv}://{user}:{password}@{cluster}/{requirements}"
    # mongodb+srv://ahezekiah_db_mongo:lab2mongodb@cluster0.ew8zh8g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
    database_name = "chai_db"

    # example for Local mongodb
    # connection_string = "mongodb://localhost:27017/"

    db_manager = MongoDBManager(connection_string=connection_string, database_name=database_name)

    user_id = input("Please enter your user ID to begin: ")

    # --- TODO 2: List existing threads and let user choose ---
    # Steps:
    # 1. Get list of existing threads for this user using list_user_threads()
    # 2. If threads exist (Step 2 already done for you, understand the flow, then skip to 3):
    #    - Print them out with numbers (e.g., "1. work_project")
    #    - Print an option to create a new thread (e.g., "N. Create new thread")
    #    - Get user's choice
    # 3. If no threads exist or user chooses new:
    #    - Prompt for a new thread name (already done for you, skip to next)
    #    - Store the new thread_name

    threads = None  # fixme!

    for i, thread_name in enumerate(threads):
        print(f"{i}. {thread_name}")
    print(f"{len(threads)}. Create new thread")
    user_selection = input("Enter a thread number:")

    if not user_selection.isdigit():
        print("Not a number, exiting")
        return

    choice = int(user_selection)

    if choice > len(threads):
        print("Selection is too large of a number")
        return

    thread_name = ""
    if not threads or choice == len(threads):
        # prompt for thread name
        thread_name = input("Enter thread name:")
        # Store new thread name
        # fixme!
        # db_manager.save_conversation
    else:
        thread_name = threads[choice]

    run_chat(db_manager, user_id, thread_name)

    # Don't forget to close the connection when done!
    db_manager.close()

def run_chat(db_manager: MongoDBManager, thread_manager: ThreadedFlatFileManager, user_id: str, thread_name: str, conversation_id: str) -> None:
    """
    Runs the chat loop for a specific conversation thread.
    """
    # --- TODO 3: Load and display existing conversation ---
    # Time how long it takes to load the conversation
    start_time = time.perf_counter()
    messages = thread_manager.load_thread(user_id, thread_name)
    if not messages:
        try:
            messages = db_manager.get_conversation(conversation_id)
        except Exception:
            messages = []
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
        if not user_input.strip():
            print("Please enter a valid message.")
            continue
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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

        start_time = time.perf_counter()

        # Append user message
        user_message = {"role": "user", "content": user_input, "timestamp": timestamp}
        # fixme! Use append_message
        messages.append(user_message)
        print(f"You: ({timestamp}): {user_input}")
        # db_manager.
        try:
            db_manager.save_conversation(conversation_id, f"{conversation_id}.json", messages)
        except Exception:
            pass
        thread_manager.save_thread(user_id, thread_name, messages)
        
        # Create and append AI response
        ai_response = generated_ai_response(user_input)
        ai_message = {"role": "assistant", "content": ai_response, "timestamp": timestamp}
        # fixme! Use append_message
        messages.append(ai_message)
        print(f"AI: {ai_response}")
        #db_manager.
        try:
            db_manager.save_conversation(conversation_id, f"{conversation_id}.json", messages)
        except Exception:
            pass
        thread_manager.save_thread(user_id, thread_name, messages)

        end_time = time.perf_counter()
        duration = end_time - start_time
        print(f"(Operation took {duration:.4f} seconds)\n")


if __name__ == "__main__":
    main()