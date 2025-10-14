# Project: Chai (Chat + AI)

This repository contains the source code for the "Chai" command-line AI chat application, developed as part of the DBT230 course.

## Author

**Name:** Trentin Brundige

## Lab 1: Flat-File Persistence

This lab focuses on building the foundational persistence layer using a simple flat-file (JSON) system. The goal is to establish a performance baseline for file I/O operations, which will serve as a benchmark for subsequent labs involving more advanced database technologies.

# Questions

1. What are two different designs you contemplated for your multiple conversations implementation?
A- A single JSON file per user including all threads within.
A- A single JSON file per thread that included name by user and thread.

2. A vibe coder wants to make a quick MVP (minimum viable product) over the weekend that handles chat threads with AI models. Do you recommend using JSON files for persistence? Why?
A- Yes as its simple and quick to implement at the cost of its lack of scalability 

3. You are interviewing at OpenAI. The interviewer asks if you would use raw JSON files to store user chats or if you would use a database or other form of persistence and to explain your choice. How would you reply?
A- I would use a database to promote concurrency and performance. JSON is great as a prototype but do to its lack of scalability, JSON proves to be far slower when handling large amounts of data.

4. What did you notice about performance using this file storage method?
A- JSON can handle small conversations well but begins to slow down as messages grow to full read/write
