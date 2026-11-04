# 🔗 LangChain Essentials - TypeScript

## 🚀 Quickstart

### Prerequisites

Install Node.js 22 LTS (the locked toolchain requires Node >=20.16.0), npm/npx,
pnpm 10.28.1, and Deno. If Corepack is not bundled with your Node installation,
install it before running `corepack enable`. The MCP lesson launches `npx`.

Install the Deno Jupyter kernel:

```bash
# Install Deno
curl -fsSL https://deno.land/install.sh | sh
# Install Deno Jupyter Kernel
deno jupyter --install
# Activate Deno Jupyter Kernel
deno jupyter --unstable
```

You should be able to select the Deno kernel from the available kernels list.

### Installation

1. Clone the repository:

```bash
git clone https://github.com/langchain-ai/lca-langchainV1-essentials.git
cd ./lca-langchainV1-essentials/js
```

2. Install the package and dependencies:

```bash
corepack enable
pnpm install
```

3. Create a `.env` file in the project root with your API keys:

```bash
# Create .env file
cp example.env .env
```

Add your API keys to the `.env` file:

```env
# Required for model usage
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional: For evaluation and tracing
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_TRACING=false
LANGSMITH_AGENT_ID=lc-essentials
LANGSMITH_AGENT_ENVIRONMENT=local
# If you are on the EU instance:
# LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com

```

For optional tracing, create an agent in your LangSmith workspace and use its ID
in `LANGSMITH_AGENT_ID`. Set `LANGSMITH_AGENT_ENVIRONMENT=local`, add your API
key, and enable `LANGSMITH_TRACING=true`. Remove `LANGSMITH_PROJECT` and
`LANGCHAIN_PROJECT` from your environment before switching to agent-based
tracing, then restart the notebook kernel. Leave tracing disabled if you do not
configure LangSmith.

Lessons 4, 7, and 8 use OpenAI; the other model examples use Anthropic. Supply
both provider keys to run all lessons. For an official OpenAI model that requires
Responses, pass `new ChatOpenAI({ model: "gpt-5.6-luna", useResponsesApi: true })`
from `@langchain/openai` to `createAgent`.

### Running Jupyter Notebooks

If you don't have Jupyter installed, you can install it using pip or pipx:

```bash
# Using pip with a virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install jupyterlab
```

Once Jupyter is installed and the Deno kernel is set up (see Prerequisites), start Jupyter:

```bash
# Start Jupyter Lab 
jupyter lab
```

This will open Jupyter in your browser. When opening any of the `.ipynb` files in this directory, make sure to select the **Deno** kernel from the kernel selector in the top-right corner of the notebook interface.


5. Setup LangSmith Studio

```bash
#to run
pnpm langgraphjs dev
```
For more information on the LangSmith Studio, see the [documentation](https://docs.langchain.com/oss/python/langchain/studio)


## 📚 Tutorial Overview

This repository contains nine short notebooks that are brief introductions to many of the most-used features in LangChain, starting with the new Create Agent.

### `L1_fast_agent.ipynb` - 🤖 Create Agent 🤖
- In this notebook, you will build and use LangChain's `createAgent` to build an SQL agent in a few lines of code.
- This notebook demonstrates how quick and easy it is to build a very powerful agent.
- You will also use LangSmith Studio, a handy visual debugger to run, host, and explore agents.


### `L2-7.ipynb` - 🧱 Building blocks 🧱
In Lessons 2-7, you will learn to use some of the building blocks in LangChain. These explain and complement `createAgent`, and you will find them useful when creating your own agents. There are many lessons, but each is a quick look.

 - **L2_messages.ipynb**: Learn how messages convey information between components of the agent.
 - **L3_streaming.ipynb**: Learn to reduce user-perceived latency using streaming.
 - **L4_tools.ipyb**: Learn basic tool use to enhance your model with custom or prebuilt tools.
 - **L5_tools_with_mcp.ipynb**: Learn to use the Langchain mcp adaptor to access the world of mcp tools.
 - **L6_memory.ipynb**: Learn to give your agent the ability to maintain state between invocations.
 - **L7_structuredOutput.ipynb**: Learn to use your agent to produce structured output.
 - 
### L8-9.ipynb - 🪛 Customize Your Agent 🤖
Lessons 2-7 covered out-of-the-box features. However, `createAgent` supports pre-built and user-created customization by adding access to the agent via Middleware. This section describes middleware and has two lessons on particular instances of its use.

- **L8_dynamic.ipynb**: Learn to create and change the agents' system prompt on the fly to react to current situations.
- **L9_HITL.ipynb**: Learn to use Interrupts to gain Human in the Loop interactions.
