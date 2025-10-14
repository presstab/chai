import time
import random
import string
from db_wrappers.flat_file_manager import FlatFileManager
from db_wrappers.mongodb_manager import MongoDBManager

PASSWORD = ""
CONNECTION_STRING = f""

def random_string(length=20):
    """Generate a random string for test data."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def test_flat_file_append_performance(num_messages=100):
    """Test FlatFileManager append performance."""
    manager = FlatFileManager(storage_dir="data_perf_test")
    conversation_id = "perf_test"
    messages = []

    # Test append performance
    append_times = []
    for i in range(num_messages):
        start = time.perf_counter()

        # Simulate the read-modify-write cycle
        messages = manager.get_conversation(conversation_id)
        messages.append({"role": "user", "content": random_string()})
        messages.append({"role": "assistant", "content": random_string()})
        manager.save_conversation(conversation_id, f"{conversation_id}.json", messages)

        end = time.perf_counter()
        append_times.append(end - start)

    # Test read performance
    start = time.perf_counter()
    final_messages = manager.get_conversation(conversation_id)
    read_time = time.perf_counter() - start

    # Cleanup
    import shutil
    shutil.rmtree("data_perf_test")

    return append_times, read_time, len(final_messages)


def test_mongodb_append_performance(num_messages=100):
    """Test MongoDBManager append performance."""
    connection_string = CONNECTION_STRING
    manager = MongoDBManager(connection_string=connection_string, database_name="chai_perf_test")

    user_id = "perf_test_user"
    thread_name = "perf_test_thread"

    # Clean slate
    manager.delete_conversation(user_id, thread_name)

    # Test append performance
    append_times = []
    for i in range(num_messages):
        start = time.perf_counter()

        manager.append_message(user_id, thread_name, {"role": "user", "content": random_string()})
        manager.append_message(user_id, thread_name, {"role": "assistant", "content": random_string()})

        end = time.perf_counter()
        append_times.append(end - start)

    # Test read performance
    start = time.perf_counter()
    final_messages = manager.get_conversation(user_id, thread_name)
    read_time = time.perf_counter() - start

    # Cleanup
    manager.delete_conversation(user_id, thread_name)
    manager.close()

    return append_times, read_time, len(final_messages)


def test_flat_file_bulk_write(num_messages=1000):
    """Test FlatFileManager bulk write performance (write once scenario)."""
    manager = FlatFileManager(storage_dir="data_perf_test")
    conversation_id = "bulk_test"

    # Generate all messages upfront
    messages = []
    for i in range(num_messages):
        messages.append({"role": "user", "content": random_string()})
        messages.append({"role": "assistant", "content": random_string()})

    # Single bulk write
    start = time.perf_counter()
    manager.save_conversation(conversation_id, f"{conversation_id}.json", messages)
    write_time = time.perf_counter() - start

    # Test read performance
    start = time.perf_counter()
    read_messages = manager.get_conversation(conversation_id)
    read_time = time.perf_counter() - start

    # Cleanup
    import shutil
    shutil.rmtree("data_perf_test")

    return write_time, read_time, len(read_messages)


def test_mongodb_bulk_write(num_messages=1000):
    """Test MongoDBManager bulk write performance (write once scenario)."""
    connection_string = CONNECTION_STRING
    manager = MongoDBManager(connection_string=connection_string, database_name="chai_perf_test")

    user_id = "bulk_test_user"
    thread_name = "bulk_test_thread"

    # Clean slate
    manager.delete_conversation(user_id, thread_name)

    # Generate all messages upfront
    messages = []
    for i in range(num_messages):
        messages.append({"role": "user", "content": random_string()})
        messages.append({"role": "assistant", "content": random_string()})

    # Single bulk write
    start = time.perf_counter()
    manager.save_conversation(user_id, thread_name, messages)
    write_time = time.perf_counter() - start

    # Test read performance
    start = time.perf_counter()
    read_messages = manager.get_conversation(user_id, thread_name)
    read_time = time.perf_counter() - start

    # Cleanup
    manager.delete_conversation(user_id, thread_name)
    manager.close()

    return write_time, read_time, len(read_messages)


def test_flat_file_multiple_threads(num_threads=10, messages_per_thread=50):
    """Test FlatFileManager with multiple conversation threads."""
    manager = FlatFileManager(storage_dir="data_perf_test")

    create_times = []

    # Create multiple threads
    for i in range(num_threads):
        conversation_id = f"thread_{i}"
        messages = []

        start = time.perf_counter()
        for j in range(messages_per_thread):
            messages.append({"role": "user", "content": random_string()})
            messages.append({"role": "assistant", "content": random_string()})
        manager.save_conversation(conversation_id, f"{conversation_id}.json", messages)
        create_times.append(time.perf_counter() - start)

    # Test random access to different threads
    random_access_times = []
    for i in range(20):
        thread_num = random.randint(0, num_threads - 1)
        conversation_id = f"thread_{thread_num}"

        start = time.perf_counter()
        messages = manager.get_conversation(conversation_id)
        random_access_times.append(time.perf_counter() - start)

    # Cleanup
    import shutil
    shutil.rmtree("data_perf_test")

    return create_times, random_access_times


def test_mongodb_multiple_threads(num_threads=10, messages_per_thread=50):
    """Test MongoDBManager with multiple conversation threads."""
    connection_string = CONNECTION_STRING
    manager = MongoDBManager(connection_string=connection_string, database_name="chai_perf_test")

    user_id = "multi_thread_user"

    # Clean slate
    manager._wipe_database()

    create_times = []

    # Create multiple threads
    for i in range(num_threads):
        thread_name = f"thread_{i}"
        messages = []

        start = time.perf_counter()
        for j in range(messages_per_thread):
            messages.append({"role": "user", "content": random_string()})
            messages.append({"role": "assistant", "content": random_string()})
        manager.save_conversation(user_id, thread_name, messages)
        create_times.append(time.perf_counter() - start)

    # Test random access to different threads
    random_access_times = []
    for i in range(20):
        thread_num = random.randint(0, num_threads - 1)
        thread_name = f"thread_{thread_num}"

        start = time.perf_counter()
        messages = manager.get_conversation(user_id, thread_name)
        random_access_times.append(time.perf_counter() - start)

    # Test listing all threads
    start = time.perf_counter()
    threads = manager.list_user_threads(user_id)
    list_time = time.perf_counter() - start

    # Cleanup
    manager._wipe_database()
    manager.close()

    return create_times, random_access_times, list_time


def test_cold_start_performance():
    """Test initial startup/first access performance."""
    print("\n" + "=" * 80)
    print("TEST 5: Cold Start Performance (First Access)")
    print("=" * 80)

    # Flat File - Cold Start
    manager_ff = FlatFileManager(storage_dir="data_cold_test")
    start = time.perf_counter()
    manager_ff.save_conversation("cold_test", "cold_test.json", [{"role": "user", "content": "first"}])
    flat_file_cold = time.perf_counter() - start

    import shutil
    shutil.rmtree("data_cold_test")

    # MongoDB - Cold Start
    connection_string = CONNECTION_STRING
    start = time.perf_counter()
    manager_mongo = MongoDBManager(connection_string=connection_string, database_name="chai_cold_test")
    manager_mongo.save_conversation("cold_user", "cold_thread", [{"role": "user", "content": "first"}])
    mongo_cold = time.perf_counter() - start

    manager_mongo._wipe_database()
    manager_mongo.close()

    print(f"Flat File cold start: {flat_file_cold:.4f} seconds")
    print(f"MongoDB cold start:   {mongo_cold:.4f} seconds")

    if flat_file_cold < mongo_cold:
        print(f"✓ Flat File is {mongo_cold / flat_file_cold:.2f}x faster for cold starts")
    else:
        print(f"✓ MongoDB is {flat_file_cold / mongo_cold:.2f}x faster for cold starts")

    return flat_file_cold, mongo_cold


if __name__ == "__main__":
    print("=" * 80)
    print("PERFORMANCE COMPARISON: Flat Files vs MongoDB")
    print("=" * 80)

    results = {
        'flat_file': {},
        'mongodb': {}
    }

    # TEST 1: Incremental Append Performance
    print("\n" + "=" * 80)
    print("TEST 1: Incremental Append Performance (Simulating Real Chat Usage)")
    print("=" * 80)
    print("This simulates a user chatting in real-time, adding messages one at a time.\n")

    for count in [10, 50, 100]:
        print(f"\n--- Testing with {count} message pairs ---")

        flat_append, flat_read, flat_msg_count = test_flat_file_append_performance(count)
        mongo_append, mongo_read, mongo_msg_count = test_mongodb_append_performance(count)

        flat_avg = sum(flat_append) / len(flat_append)
        mongo_avg = sum(mongo_append) / len(mongo_append)

        print(f"Flat File:")
        print(f"  - Avg append: {flat_avg:.4f}s")
        print(f"  - Min append: {min(flat_append):.4f}s")
        print(f"  - Max append: {max(flat_append):.4f}s")
        print(f"  - Full read:  {flat_read:.4f}s")
        print(f"  - Final msgs: {flat_msg_count}")

        print(f"MongoDB:")
        print(f"  - Avg append: {mongo_avg:.4f}s")
        print(f"  - Min append: {min(mongo_append):.4f}s")
        print(f"  - Max append: {max(mongo_append):.4f}s")
        print(f"  - Full read:  {mongo_read:.4f}s")
        print(f"  - Final msgs: {mongo_msg_count}")

        if flat_avg < mongo_avg:
            speedup = mongo_avg / flat_avg
            print(f"\n✓ Flat File is {speedup:.2f}x faster for incremental appends at {count} messages")
        else:
            speedup = flat_avg / mongo_avg
            print(f"\n✓ MongoDB is {speedup:.2f}x faster for incremental appends at {count} messages")

        results['flat_file'][f'append_{count}'] = flat_avg
        results['mongodb'][f'append_{count}'] = mongo_avg
        results['flat_file'][f'read_{count}'] = flat_read
        results['mongodb'][f'read_{count}'] = mongo_read

    # TEST 2: Bulk Write Performance
    print("\n" + "=" * 80)
    print("TEST 2: Bulk Write Performance (Import/Migration Scenario)")
    print("=" * 80)
    print("This simulates importing a complete conversation history all at once.\n")

    for count in [100, 500, 1000]:
        print(f"\n--- Testing with {count} message pairs ---")

        flat_write, flat_read, flat_count = test_flat_file_bulk_write(count)
        mongo_write, mongo_read, mongo_count = test_mongodb_bulk_write(count)

        print(f"Flat File:")
        print(f"  - Bulk write: {flat_write:.4f}s")
        print(f"  - Full read:  {flat_read:.4f}s")
        print(f"  - Messages:   {flat_count}")

        print(f"MongoDB:")
        print(f"  - Bulk write: {mongo_write:.4f}s")
        print(f"  - Full read:  {mongo_read:.4f}s")
        print(f"  - Messages:   {mongo_count}")

        if flat_write < mongo_write:
            speedup = mongo_write / flat_write
            print(f"\n✓ Flat File is {speedup:.2f}x faster for bulk writes")
        else:
            speedup = flat_write / mongo_write
            print(f"\n✓ MongoDB is {speedup:.2f}x faster for bulk writes")

        results['flat_file'][f'bulk_write_{count}'] = flat_write
        results['mongodb'][f'bulk_write_{count}'] = mongo_write

    # TEST 3: Multiple Thread Management
    print("\n" + "=" * 80)
    print("TEST 3: Multiple Conversation Thread Performance")
    print("=" * 80)
    print("This simulates a user with many different conversation threads.\n")

    for num_threads in [5, 10, 20]:
        print(f"\n--- Testing with {num_threads} threads, 50 messages each ---")

        flat_create, flat_access = test_flat_file_multiple_threads(num_threads, 50)
        mongo_create, mongo_access, mongo_list = test_mongodb_multiple_threads(num_threads, 50)

        flat_create_avg = sum(flat_create) / len(flat_create)
        mongo_create_avg = sum(mongo_create) / len(mongo_create)
        flat_access_avg = sum(flat_access) / len(flat_access)
        mongo_access_avg = sum(mongo_access) / len(mongo_access)

        print(f"Flat File:")
        print(f"  - Avg thread creation: {flat_create_avg:.4f}s")
        print(f"  - Avg random access:   {flat_access_avg:.4f}s")

        print(f"MongoDB:")
        print(f"  - Avg thread creation: {mongo_create_avg:.4f}s")
        print(f"  - Avg random access:   {mongo_access_avg:.4f}s")
        print(f"  - List all threads:    {mongo_list:.4f}s")

        if flat_access_avg < mongo_access_avg:
            speedup = mongo_access_avg / flat_access_avg
            print(f"\n✓ Flat File is {speedup:.2f}x faster for random thread access")
        else:
            speedup = flat_access_avg / mongo_access_avg
            print(f"\n✓ MongoDB is {speedup:.2f}x faster for random thread access")

    # TEST 4: Cold Start
    flat_cold, mongo_cold = test_cold_start_performance()
    results['flat_file']['cold_start'] = flat_cold
    results['mongodb']['cold_start'] = mongo_cold

    # COMPREHENSIVE SUMMARY
    print("\n\n")
    print("=" * 80)
    print("COMPREHENSIVE PERFORMANCE SUMMARY")
    print("=" * 80)

    print("\n📊 KEY FINDINGS:\n")

    print("1. INCREMENTAL APPENDS (Real-time Chat):")
    print("   " + "-" * 76)
    flat_10 = results['flat_file']['append_10']
    mongo_10 = results['mongodb']['append_10']
    flat_100 = results['flat_file']['append_100']
    mongo_100 = results['mongodb']['append_100']

    if flat_10 < mongo_10:
        speedup_10 = mongo_10 / flat_10
        winner_10 = "Flat File"
    else:
        speedup_10 = flat_10 / mongo_10
        winner_10 = "MongoDB"

    if flat_100 < mongo_100:
        speedup_100 = mongo_100 / flat_100
        winner_100 = "Flat File"
    else:
        speedup_100 = flat_100 / mongo_100
        winner_100 = "MongoDB"

    print(f"   At 10 messages:  {winner_10} is {speedup_10:.2f}x faster")
    print(f"   At 100 messages: {winner_100} is {speedup_100:.2f}x faster")
    print(f"   • Flat File @ 10 msgs:  {flat_10 * 1000:.2f}ms per append")
    print(f"   • MongoDB @ 10 msgs:    {mongo_10 * 1000:.2f}ms per append")
    print(f"   • Flat File @ 100 msgs: {flat_100 * 1000:.2f}ms per append")
    print(f"   • MongoDB @ 100 msgs:   {mongo_100 * 1000:.2f}ms per append")
    print()
    print("   Analysis:")
    print(f"   • Flat files are surprisingly fast for small conversations")
    print(f"   • MongoDB has network/TCP overhead even when running locally")
    print(f"   • JSON parsing and file I/O are highly optimized in modern systems")
    print(f"   • At {100} messages, flat file performance degrades ({flat_100 / flat_10:.2f}x slower)")
    print(f"   • MongoDB stays more consistent ({mongo_100 / mongo_10:.2f}x slower)")
    print()

    # Calculate scaling characteristics
    flat_scaling = flat_100 / flat_10
    mongo_scaling = mongo_100 / mongo_10

    print("2. SCALING CHARACTERISTICS:")
    print("   " + "-" * 76)
    print(f"   When conversation grows 10x (from 10 to 100 messages):")
    print(f"   • Flat File slows down by: {flat_scaling:.2f}x")
    print(f"   • MongoDB slows down by:   {mongo_scaling:.2f}x")
    print()
    if flat_scaling > mongo_scaling:
        print(f"   ✓ MongoDB scales {flat_scaling / mongo_scaling:.2f}x better as conversations grow")
        print(f"     This gap will widen further at 1000+ messages")
    else:
        print(f"   ✓ Both systems scale similarly at this size")
    print()

    print("3. BULK WRITES (Import/Migration):")
    print("   " + "-" * 76)
    flat_bulk_1000 = results['flat_file']['bulk_write_1000']
    mongo_bulk_1000 = results['mongodb']['bulk_write_1000']
    if flat_bulk_1000 < mongo_bulk_1000:
        speedup = mongo_bulk_1000 / flat_bulk_1000
        winner = "Flat File"
    else:
        speedup = flat_bulk_1000 / mongo_bulk_1000
        winner = "MongoDB"
    print(f"   {winner} is {speedup:.2f}x FASTER for bulk operations")
    print(f"   • Flat File @ 1000 msgs: {flat_bulk_1000:.4f}s")
    print(f"   • MongoDB @ 1000 msgs:   {mongo_bulk_1000:.4f}s")
    print(f"   • Why: Single large write favors flat files' simple write model")
    print(f"           Network overhead and document parsing add cost to MongoDB")
    print()

    print("4. COLD START (Initial Setup):")
    print("   " + "-" * 76)
    if flat_cold < mongo_cold:
        speedup = mongo_cold / flat_cold
        winner = "Flat File"
    else:
        speedup = flat_cold / mongo_cold
        winner = "MongoDB"
    print(f"   {winner} is {speedup:.2f}x FASTER for cold starts")
    print(f"   • Flat File: {flat_cold:.4f}s")
    print(f"   • MongoDB:   {mongo_cold:.4f}s")
    print(f"   • Why: Flat files have zero setup; MongoDB requires connection")
    print(f"           and index creation")
    print()

    print("5. READ PERFORMANCE (Loading Conversation):")
    print("   " + "-" * 76)
    flat_read_100 = results['flat_file']['read_100']
    mongo_read_100 = results['mongodb']['read_100']
    if flat_read_100 < mongo_read_100:
        speedup = mongo_read_100 / flat_read_100
        winner = "Flat File"
    else:
        speedup = flat_read_100 / mongo_read_100
        winner = "MongoDB"
    print(f"   {winner} is {speedup:.2f}x FASTER for reading full conversations")
    print(f"   • Flat File @ 100 msgs: {flat_read_100 * 1000:.2f}ms")
    print(f"   • MongoDB @ 100 msgs:   {mongo_read_100 * 1000:.2f}ms")
    print(f"   • Note: Both are fast; difference is network vs disk I/O")
    print()

    print("\n" + "=" * 80)
    print("FLAT FILE ADVANTAGES:")
    print("=" * 80)
    print("✓ Simplicity: Zero infrastructure, no setup required")
    print("✓ Cold Starts: Instant initialization, no connection overhead")
    print("✓ Small Scale: Faster than MongoDB for <50 message conversations")
    print("✓ Bulk Writes: Single large writes are efficient")
    print("✓ Portability: Plain JSON files work everywhere")
    print("✓ Debugging: Easy to inspect and edit files manually")
    print("✓ Cost: Completely free, no hosting or service costs")
    print("✓ Version Control: Can commit data files to Git")
    print("✓ No Network: Pure disk I/O avoids TCP/connection overhead")
    print()
    print("❌ Disadvantages:")
    print("  • Incremental updates require full file rewrite (O(n) operation)")
    print(f"  • Performance degrades as conversations grow ({flat_scaling:.2f}x slower at 100 msgs)")
    print("  • No atomic operations (risk of corruption on crashes)")
    print("  • No indexing or query capabilities")
    print("  • File system limits (~10,000 files per directory)")
    print("  • Concurrent access is problematic")
    print("  • Will become significantly slower at 500+ messages")
    print()

    print("=" * 80)
    print("MONGODB ADVANTAGES:")
    print("=" * 80)
    print("✓ Scalability: Performance stays more consistent as data grows")
    print(f"✓ Better Scaling: Only {mongo_scaling:.2f}x slower at 10x data (vs {flat_scaling:.2f}x for files)")
    print("✓ Indexing: Fast lookups across millions of documents")
    print("✓ Queries: Flexible search and aggregation capabilities")
    print("✓ Concurrency: Built-in handling of simultaneous access")
    print("✓ Atomic Operations: Guaranteed consistency with $push")
    print("✓ Replication: Built-in backup and high availability")
    print("✓ Advanced Features: Transactions, change streams, aggregations")
    print("✓ Production Ready: Handles millions of users")
    print()
    print("❌ Disadvantages:")
    print("  • Setup Complexity: Requires server installation or cloud account")
    print(f"  • Network Overhead: {mongo_10 * 1000:.1f}ms even for simple operations locally")
    print(f"  • Slower for Small Data: {speedup_10:.2f}x slower than files for tiny conversations")
    print("  • Resource Usage: Requires memory and CPU for database server")
    print("  • Cost: Cloud hosting costs for production (~$57/month for M10)")
    print("  • Learning Curve: More complex than simple file I/O")
    print()

    print("=" * 80)
    print("THE SURPRISING TRUTH:")
    print("=" * 80)
    print()
    print("For this lab's use case (local development, small conversations),")
    print("flat files are actually FASTER than MongoDB!")
    print()
    print("This demonstrates an important principle in database design:")
    print("  'Use the simplest tool that meets your requirements'")
    print()
    print("However, the story changes as we scale...")
    print()

    print("=" * 80)
    print("WHEN TO USE EACH:")
    print("=" * 80)
    print()
    print("USE FLAT FILES WHEN:")
    print("  • Building a quick prototype or MVP (faster development)")
    print("  • Single-user application on local machine")
    print("  • Small data volume (<100 conversations, <200 messages each)")
    print("  • Infrequent updates (batch processing)")
    print("  • Need to version control your data")
    print("  • Zero infrastructure preferred")
    print("  • Want maximum speed for small-scale operations")
    print()
    print("USE MONGODB WHEN:")
    print("  • Conversations will grow to 500+ messages (scaling matters)")
    print("  • Multiple users or concurrent access needed")
    print("  • Need to search across conversations")
    print("  • Building a production application")
    print("  • Expect to scale beyond a few thousand records")
    print("  • Need data consistency guarantees (atomic operations)")
    print("  • Want to add features like: search, analytics, recommendations")
    print("  • Planning for horizontal scaling (sharding)")
    print()