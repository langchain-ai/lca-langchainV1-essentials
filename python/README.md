# 🔗 LangChain Essentials - Python

## Introduction

Welcome to LangChain Academy’s LangChain Essentials - Python course!

---

## 🚀 Setup 

### Quick Start Verification

After completing the Setup section, run this command to verify your environment:

```bash
python3 env_utils.py
```

### Prerequisites

- Ensure you're using Python 3.11 - 3.13. [More info](#virtual-environments-and-python)
- [uv](https://docs.astral.sh/uv/) package manager or [pip](https://pypi.org/project/pip/)
- OpenAI API key [More info](#model-providers)
- Node.js and npx (required for MCP server in notebook 3):

```bash
# Install Node.js (includes npx)
# On macOS with Homebrew:
brew install node

# On Ubuntu/Debian:
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation:
node --version
npx --version
```

### Installation

Download the course repository

```bash
# Clone the repo, cd to 'python' directory
git clone https://github.com/langchain-ai/lca-langchainV1-essentials.git
cd ./lca-langchainV1-essentials/python
```

Make a copy of example.env

```bash
# Create .env file
cp example.env .env
```

Edit the .env file to include the keys below. [More info](#environment-variables)
An OpenAI key is suggested and a [LangSmith](#getting-started-with-langsmith) key is optional.

```bash
# Add OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
# The course is written with OpenAI models, but you can choose others if you prefer. 
# Be sure to add the key and modify the code to call your preferred model
#ANTHROPIC_API_KEY=your_anthropic_api_key_here_if_you_prefer

# Optional API key for LangSmith tracing
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=langgraph-py-essentials
# If you are on the EU instance:
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
```

Make a virtual environment and install dependencies
```bash
# Create virtual environment and install dependencies
uv sync
```

## 💡 Development Environment

Run Notebooks

```bash
# Run Jupyter notebooks directly with uv
uv run jupyter lab

# Or activate the virtual environment first, if preferred
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
jupyter lab
```

Optional: Run LangSmith Studio

```bash
# copy the .env file you created above to the studio directory
cp .env ./studio/.

cd studio
#to run with uv
uv run langgraph dev

#to run with virtual env
langgraph dev
```

## 📚 Lessons
This repository contains nine short notebooks that serve as brief introductions to many of the most-used features in LangChain, starting with the new **Create Agent**.

---

### `L1_fast_agent.ipynb` - 🤖 Create Agent 🤖
- In this notebook, you will use LangChain’s `create_agent` to build an SQL agent in just a few lines of code.  
- It demonstrates how quick and easy it is to build a powerful agent. You can easily take this agent and apply it to your own project. 
- You will also use **LangSmith Studio**, a handy visual debugger to run, host, and explore agents.

---

### `L2-7.ipynb` - 🧱 Building Blocks 🧱
In Lessons 2–7, you will learn how to use some of the fundamental building blocks in LangChain. These lessons explain and complement `create_agent`, and you’ll find them useful when creating your own agents. Each lesson is concise and focused.

- **L2_messages.ipynb**: Learn how messages convey information between agent components.  
- **L3_streaming.ipynb**: Learn how to reduce user-perceived latency using streaming.  
- **L4_tools.ipynb**: Learn basic tool use to enhance your model with custom or prebuilt tools.  
- **L5_tools_with_mcp.ipynb**: Learn to use the LangChain MCP adapter to access the world of MCP tools.  
- **L6_memory.ipynb**: Learn how to give your agent the ability to maintain state between invocations.  
- **L7_structuredOutput.ipynb**: Learn how to produce structured output from your agent.  

---

### `L8-9.ipynb` - 🪛 Customize Your Agent 🤖
Lessons 2–7 covered out-of-the-box features. However, `create_agent` also supports both prebuilt and user-defined customization through **Middleware**. This section describes middleware and includes two lessons highlighting specific use cases.

- **L8_dynamic.ipynb**: Learn how to dynamically modify the agent’s system prompt to react to changing contexts.  
- **L9_HITL.ipynb**: Learn how to use Interrupts to enable Human-in-the-Loop interactions.

## 📖 Related Resources

### Virtual Environments and Python

Managing your Python version is frequently best done using virtual environments.  This allows you to select a Python version for the course independent of the system Python version. There are many ways to do this. Two popular approaches use `uv` or `pyenv` to select which version to install and use in your virtual environment.

For example, you can select and install the Python version when creating the virtual environment with uv. After you activate the environment, you can proceed with uv sync to install the necessary packages. For additional information, please see [uv](https://docs.astral.sh/uv/).

````bash
uv venv --python 3.11
source .venv/bin/activate
uv sync
````

If you are using pip instead of uv, you may prefer using pyenv to manage your Python versions.  For additional information, please see  [pyenv](https://github.com/pyenv/pyenv).

### Model Providers

If you don’t have an OpenAI API key, you can sign up [here](https://openai.com/index/openai-api/).

This course has been created using a particular model provider.  It is possible to use another provider, but you will need to update the .env file with any required identification (API key), and some code changes will be necessary. See more about this [here](https://docs.langchain.com/oss/python/integrations/providers/all_providers).

### Getting Started with LangSmith

- Create a [LangSmith](https://smith.langchain.com/) account
- Create a LangSmith API key

<img width="600" alt="LangSmith Dashboard" src="https://github.com/user-attachments/assets/e39b8364-c3e3-4c75-a287-d9d4685caad5" />

<img width="600" alt="LangSmith API Keys" src="https://github.com/user-attachments/assets/2e916b2d-e3b0-4c59-a178-c5818604b8fe" />

- Update your .env file you created with your new LangSmith API Key.

For more information on LangSmith see our docs [here](https://docs.langchain.com/oss/python/langchain/studio).

### Environment Variables

This course makes use of the module dotenv which reads key-value pairs from a .env file rather then relying on preset system environment variables.  This is much more convienient for the student taking mulitiple courses, as it is easy to support distinct values for keys such as LANGSMITH_PROJECT per course.
