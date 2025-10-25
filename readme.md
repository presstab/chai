# Project: Chai (Chat + AI)

This repository contains the source code for the "Chai" command-line AI chat application, developed as part of the DBT230 course.

## Author

**Name:Geo Gardener**

## Lab 1: Flat-File Persistence

This lab focuses on building the foundational persistence layer using a simple flat-file (JSON) system. The goal is to establish a performance baseline for file I/O operations, which will serve as a benchmark for subsequent labs involving more advanced database technologies.

## Questions

### What are two different designs you contemplated for your multiple conversations implementation?

The first idea I had was to just keep a single `conversations.json` file that stores everything inside one big nested dictionary like  
`{ user_id: { thread_name: [messages] } }`.  
It’s simple and works for a while, but it gets messy fast since every single save rewrites the whole file.  

The second design (the one I actually used) makes a folder for each user inside the `data/` directory, and then every conversation thread is it’s own `.json` file.  
That setup ended up being way cleaner and way easier to manage. I can delete or load just one thread without touching all the other ones.

---

### A vibe coder wants to make a quick MVP that handles chat threads with AI models. Do you recommend using JSON files for persistence? Why?

Yeah honestly, for a fast MVP JSON is perfect.  
It’s built into Python already, easy to read, and doesn’t need any setup like a database does.  
But if the project grows or starts having tons of users, it’ll slow down fast. Every time you save something, it rewrites the whole file again which kinda sucks.  
So JSON is fine for prototyping, but not something I’d wanna use longterm.

---

### You’re interviewing at OpenAI. The interviewer asks if you’d use raw JSON files or a database to store user chats—how do you reply?

I’d definitely say a database.  
JSON files can’t handle stuff like multiple users saving at the same time or doing quick searches.  
A database like PostgreSQL or MongoDB can manage that no problem. JSON’s cool for testing things out fast, but it’s not meant to scale or keep things consistent long term.

---

### What did you notice about performance using this file-storage method?

It was fine for short conversations, but once the file started getting bigger, the speed drop was noticeable.  
Each read-append-write cycle rewrites the entire conversation, which isn’t super efficient.  
The timing measurements with `time.perf_counter()` showed how each operation still takes a bit even when it’s small, and it only gets slower as the chat grows.  
That’s kinda the whole reason databases exist, so you don’t have to keep rewriting the same file over and over.
