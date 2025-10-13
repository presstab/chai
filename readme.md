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
