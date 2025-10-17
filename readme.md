# Project: Chai (Chat + AI)

This repository contains the source code for the "Chai" command-line AI chat application, developed as part of the DBT230 course.

## Author

**Name:** Amanda Hezekiah

## Lab 1: Flat-File Persistence

This lab focuses on building the foundational persistence layer using a simple flat-file (JSON) system. The goal is to establish a performance baseline for file I/O operations, which will serve as a benchmark for subsequent labs involving more advanced database technologies.

## Questions
1. What are two different designs you contemplated for your multiple conversations implementation?
    - One design used a single JSON file per user that stored all conversation threads together. 
    This was simple but inefficient because every small change required rewriting the entire file. 
    The second design, which I chose, created a folder for each user with a separate JSON file for each thread. 
    This approach was more organized, faster, and reduced the risk of file corruption.
2. A vibe coder wants to make a quick MVP (minimum viable product) over the weekend that handles chat threads with AI models. Do you recommend using JSON files for persistence? Why?
    - Yes, JSON files are perfect for a quick MVP because they’re lightweight, easy to set up, and require no external database. 
    They let developers focus on core features instead of backend setup. 
    However, they’re not suitable for large-scale or multi-user systems due to performance and concurrency limitations.
3. You are interviewing at OpenAI. The interviewer asks if you would use raw JSON files to store user chats or if you would use a database or other form of persistence and to explain your choice. How would you reply?
    - I’d explain that JSON files work well for quick prototypes but not for production systems. 
    A database is the better choice for chat storage because it provides scalability, concurrent access, and efficient querying. 
    For chat data, I’d likely use a document-oriented database like MongoDB since it naturally fits JSON-like structures.
4. What did you notice about performance using this file storage method?
    - Performance was good for small conversations but slowed down as data grew. 
    Each write required reloading and saving the entire file, which became inefficient over time. 
    It was fine for simple testing but not ideal for frequent or large-scale chat operations.


## Lab 2: MongoDB Integration & Performance Analysis

## Questions
1. Performance Analysis
Run performance_test.py and record the results. What did you observe about:
    - 
    How append times changed as the number of messages grew for flat files vs MongoDB?
        - 
    The difference in read times for retrieving the full conversation?
        - 
Explain why you see these performance characteristics.
    - 
2. Atomic Operations
In MongoDBManager, we use the $push operator in append_message(). Research what "atomic operations" means in the context of databases. Why is this important for a chat application where multiple messages might be added rapidly?
    - 
3. Scalability
Imagine your chat application goes viral and now has 1 million users, each with an average of 10 conversation threads containing 500 messages each.
Compare how FlatFileManager and MongoDBManager would handle:
    Finding all threads for a specific user
        - 
    Loading a specific conversation
        - 
    Storage organization and file system limits
        - 
4. Data Modeling Design Challenge
Currently, each conversation is stored as a single document with an embedded array of messages:
{
  "_id": "user_123_work",
  "messages": [...]
}
An alternative design would be to store each message as its own document:
{
  "_id": "msg_001",
  "conversation_id": "user_123_work",
  "role": "user",
  "content": "Hello!",
  "timestamp": "..."
}
Describe:
    One advantage of the embedded messages design (what we currently use)
        - 
    One advantage of the separate message documents design
        - 
    A scenario where you would choose the separate messages design instead
        - 
