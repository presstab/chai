import time
import os
import asyncio
import sys
from typing import List, Dict, Optional, Callable
from db_wrappers.flat_file_manager import FlatFileManager

try:
    # Optional: async OpenAI client
    from openai import AsyncOpenAI  # type: ignore
except Exception:  # ImportError or other
    AsyncOpenAI = None  # type: ignore


def load_env_from_dotenv(dotenv_path: str = ".env") -> None:
    """
    Minimal .env loader. Loads KEY=VALUE pairs into os.environ if not already set.
    Comments (# ...) and blank lines are ignored.
    """
    if not os.path.exists(dotenv_path):
        return
    try:
        with open(dotenv_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
    except OSError:
        pass


async def generate_ai_response(messages: List[Dict[str, str]], *, model: Optional[str] = None) -> str:
    """
    Generate an AI response using OpenAI's async client.
    Expects messages in Chat Completions format: [{"role": "user"|"assistant"|"system", "content": str}, ...]
    """
    if AsyncOpenAI is None:
        return "[OpenAI client not installed. Install 'openai' package to enable AI.]"

    api_key = os.getenv("OPENAI_KEY")
    if not api_key:
        return "[OPENAI_KEY not set. Add it to a .env file in this directory.]"

    base_url = os.getenv("BASE_URL")
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    use_model = model or os.getenv("MODEL") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Prepend a light system prompt
    prompt_messages = [{"role": "system", "content": "You are Chai, a concise, helpful assistant."}] + messages

    try:
        resp = await client.chat.completions.create(
            model=use_model,
            messages=prompt_messages,  # type: ignore[arg-type]
            temperature=0.7,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        return f"[OpenAI error: {e}]"


async def stream_ai_response(
    messages: List[Dict[str, str]],
    *,
    model: Optional[str] = None,
    on_delta: Optional[Callable[[str], None]] = None,
) -> str:
    """
    Stream an AI response token-by-token. Returns the full response text.
    Prints deltas via `on_delta` if provided; defaults to writing to stdout.
    """
    if AsyncOpenAI is None:
        # Fallback to non-streaming placeholder
        text = "[OpenAI client not installed. Install 'openai' to enable streaming.]"
        if on_delta:
            on_delta(text)
        else:
            sys.stdout.write(text)
            sys.stdout.flush()
        return text

    api_key = os.getenv("OPENAI_KEY")
    if not api_key:
        text = "[OPENAI_KEY not set. Add it to a .env file in this directory.]"
        if on_delta:
            on_delta(text)
        else:
            sys.stdout.write(text)
            sys.stdout.flush()
        return text

    base_url = os.getenv("BASE_URL")
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    use_model = model or os.getenv("MODEL") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Prepend a light system prompt
    prompt_messages = [{"role": "system", "content": "You are Chai, a concise, helpful assistant."}] + messages

    buffer: List[str] = []

    def emit(text: str) -> None:
        buffer.append(text)
        if on_delta:
            on_delta(text)
        else:
            sys.stdout.write(text)
            sys.stdout.flush()

    try:
        stream = await client.chat.completions.create(
            model=use_model,
            messages=prompt_messages,  # type: ignore[arg-type]
            temperature=0.7,
            stream=True,
        )
        async for chunk in stream:
            try:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if delta and getattr(delta, "content", None):
                    emit(delta.content)
            except Exception:
                # Swallow per-chunk parsing errors but continue streaming
                continue
    except Exception as e:
        err = f"[OpenAI stream error: {e}]"
        emit(err)

    return "".join(buffer).strip()


def main():
    """
    Main function to run the Chai AI chat application using flat files.
    """
    print("Welcome to Chai!")

    # Load .env for OPENAI_KEY, etc.
    load_env_from_dotenv()

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

        # Create and append AI response via OpenAI with streaming
        print("AI: ", end="", flush=True)
        ai_response = asyncio.run(
            stream_ai_response(messages)
        )
        print()  # newline after streamed content
        ai_message = {"role": "assistant", "content": ai_response}
        messages.append(ai_message)

        # Save updated conversation
        relative_filepath = db_manager.conversations_index.get(
            conversation_id, f"{user_id}__{thread_name}.json"
        )
        db_manager.save_conversation(conversation_id, relative_filepath, messages)

        end_time = time.perf_counter()
        duration = end_time - start_time

        print(f"(Operation took {duration:.4f} seconds)")


if __name__ == "__main__":
    main()
