# lca-langchainV1-essentials

**NOTE:** We have added the ./python_local directory for students who would prefer using locally stored LLMs. 

See the ./python, ./python_local or ./js directorys for their respective READMEs


### Choose model access

**Direct provider access is the default.** Copy `example.env` to `.env` in the
language directory and replace the key for the provider selected in the lesson.
OpenAI examples need `OPENAI_API_KEY`; Anthropic examples need `ANTHROPIC_API_KEY`.
You do not need a LangSmith account for direct model access or local Ollama models.

**LangSmith Gateway is opt-in.** Your workspace administrator must first
[configure provider secrets and model access](https://docs.langchain.com/langsmith/llm-gateway-admin-setup).
For supported OpenAI and Anthropic chat models, put these values in `.env`:

```dotenv
LANGSMITH_GATEWAY=true
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_TRACING=false
```

For shell configuration instead of `.env`:

```bash
export LANGSMITH_GATEWAY=true
export LANGSMITH_API_KEY=your_langsmith_api_key_here
export LANGSMITH_TRACING=false
```

Replace the placeholder with your workspace key. `LANGSMITH_GATEWAY_API_KEY`, if
set, overrides `LANGSMITH_API_KEY` for gateway model calls only. Leave it unset
unless you need separate authentication for model calls and tracing. Local
provider keys are not needed for these gateway chat calls; provider secrets live
in the workspace. Keep the lesson's model names unchanged and ensure your
workspace allows those models. Gateway access can incur usage charges.

The same settings can be exported in your shell before starting Jupyter or
Studio. Restart the kernel or process after changing them; existing shell
variables take precedence over `.env`. Unset `LANGSMITH_GATEWAY`, or set it to
`false`, `0`, or `no` to return to direct access. `true`, `1`, and `yes` enable the
default gateway (case-insensitive). A regional gateway base URL, such as
`https://eu.gateway.smith.langchain.com`, can replace `true`; the SDK appends each
provider's path. `LANGSMITH_ENDPOINT` configures tracing, not gateway routing.
Do not add whitespace to flag values: other nonempty values are treated as URLs.
Remove explicit model API keys, base URLs, and provider base-URL environment
overrides when opting in; these can take precedence over automatic routing.

Sync dependencies using the language README. Python requires
`langchain-openai>=1.4.2`, `langchain-anthropic>=1.5.1`, and
`langchain-core>=1.5.3` for the flag and workspace-key fallback. JavaScript uses
verified gateway-capable `@langchain/openai>=1.8.5`,
`@langchain/anthropic>=1.6.6`, and `@langchain/core>=1.5.0`. Both language lockfiles
are updated. See [direct model access](https://docs.langchain.com/langsmith/llm-gateway-direct-model-access)
for supported integrations and regional endpoints.

Gateway routing does **not** replace credentials for tools, search, embeddings,
or separately configured evaluator models. Keep their direct-provider keys.
Tracing remains optional and independent: leave it disabled without tracing
credentials, or enable it using the language README. Ollama examples stay local;
the gateway flag does not turn them into hosted OpenAI models.

Python notebooks run `doublecheck_env("example.env")` after `load_dotenv()`.
It checks the default chat provider listed in `example.env`; when changing
providers, pass `chat_provider_keys=("ANTHROPIC_API_KEY",)`. Pass
`direct_api_keys=("OPENAI_API_KEY",)` if an embedding or evaluator also needs that
key directly. In JavaScript, run `node check-env.mjs OPENAI_API_KEY` from `js/`
(or `ANTHROPIC_API_KEY`, or both names for all lessons). The check reads `.env`
and shell settings without contacting a provider or printing credentials.
