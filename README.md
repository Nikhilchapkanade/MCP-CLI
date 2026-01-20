# MCP-CLI 🤖

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![OpenRouter](https://img.shields.io/badge/AI-OpenRouter-purple)

> **My personal CLI tool for chatting with AI Agents and giving them file access.** > *Built because I needed a way to bypass firewalls and run "Thinking Models" locally without the bloat.*

---

## 🤷‍♂️ Why I Built This

I wanted to experiment with the **Model Context Protocol (MCP)** and Agentic AI, but I kept hitting two problems:
1.  **Firewalls:** Corporate/University networks block direct API connections.
2.  **Complexity:** Most existing tools were too heavy or hard to configure.

So I wrote this lightweight Python client. It routes everything through **OpenRouter** (to bypass blocks) and lets me run powerful models like **Gemini 2.0 Flash** and **DeepSeek R1** directly in my terminal.

---

## ✨ Cool Stuff It Does

* **🔥 Beats the Firewall:** Uses OpenRouter as a gateway, so it works on restricted networks where standard API calls fail.
* **🧠 "Enough Thinking!":** Supports the new Reasoning Models (like DeepSeek R1). You can watch the AI's internal thought process in real-time. If it gets stuck looping? You can actually tell it **"Enough thinking"** to force it to stop analyzing and give you the answer.
* **📂 It Sees My Files:** I hooked up the `filesystem` MCP server. This means I can ask the AI to "Read `main.py` and explain the bugs," and it actually opens the file.
* **⚡ Free Tier First:** I configured the default settings to use **Free** models (Gemini Flash, Phi-3, Llama 3). It handles rate limits automatically so I don't burn cash while testing.

---

## 🚀 How to Run It

I tried to keep the setup dead simple.

### 1. Clone the repo
```bash
git clone [https://github.com/Nikhilchapkanade/MCP-Playground-CLI.git](https://github.com/Nikhilchapkanade/MCP-Playground-CLI.git)
cd MCP-Playground-CLI

2. Install the basics
You'll need Python and Node.js (for the MCP server).

Bash

pip install -r requirements.txt
npm install

3. Add your Key
Create a .env file and paste your OpenRouter key (it's free to get one).

Code snippet

OPENROUTER_API_KEY=sk-or-your-key-goes-here

4. Start Chatting
Bash

python src/main.py

How I Use It
Once you're in, it's just a chat window. But the magic happens when you ask for file help.

Me: "Hey, list the files in this directory."

Agent: Thinking... [Calling tool: list_directory]

Agent: "Okay, I see main.py and requirements.txt."

Me: "Read main.py and rewrite the connection function to be async."

Agent: "On it." [Writes code]

⚙️ Configuration
I didn't want to hardcode everything. If you want to swap models, just check config/settings.json.

I set up a priority list—if the main model is busy (Error 429), it automatically suggests the backup.

"llm_profiles": [
  {
    "name": "Gemini 2.0 Flash (My Daily Driver)",
    "model_name": "google/gemini-2.0-flash-exp:free"
  },
  {
    "name": "Microsoft Phi-3 (Backup)",
    "model_name": "microsoft/phi-3-mini-128k-instruct:free"
  }
]

🛠️ Troubleshooting
"Error 401 Unauthorized": You probably put a space in your .env file. Make sure it's KEY=value, not KEY = value.

"Gemini is busy": Yeah, the free tier gets hammered. Just hit Up Arrow + Enter to try again, or switch to the Microsoft model in settings.



