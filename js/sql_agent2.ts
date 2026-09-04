// Sql agent
import "dotenv/config";
import { createAgent, tool } from "langchain";
import { ChatOpenAI } from "@langchain/openai";
import { ChatAnthropic } from "@langchain/anthropic";
import { DataSource } from "typeorm";
import { SqlDatabase } from "@langchain/classic/sql_db";
import { MemorySaver } from "@langchain/langgraph";
import { z } from "zod";

const key = process.env.ANTHROPIC_API_KEY;
if (key === undefined) {
  console.error("ANTHROPIC_API_KEY is not set");
  process.exit(1);
}

/**
 * Model
 * - Uses your Anthropic key from .env if needed
 */
// const llm = new ChatOpenAI({ model: "gpt-5" });
const llm = new ChatAnthropic({ model: "claude-sonnet-4-6" });

/**
 * Database
 * - Make sure ./Chinook.db exists (you already have it in this repo)
 * - TypeORM DataSource + SqlDatabase (matches L1/L6 patterns)
 */
const datasource = new DataSource({
  type: "sqlite",
  database: "./Chinook.db",
});
const db = await SqlDatabase.fromDataSourceParams({ appDataSource: datasource });

/**
 * Schema (included in the prompt to ground the model)
 */
const SCHEMA = await db.getTableInfo();


/**
 * Tool (function-first signature; matches LangChain umbrella API)
 * - No runtime context required; closes over `db`
 */
export const execute_sql = tool(
  async ({ query }: { query: string }) => {
    try {
      return await db.run(query);
    } catch (e: any) {
      return `Error: ${e?.message ?? String(e)}`;
    }
  },
  {
    name: "execute_sql",
    description: "Execute a READ-ONLY SQLite SELECT query and return results.",
    schema: z.object({ query: z.string() }),
  }
);


/**
 * System prompt (includes schema + rules)
 */
const SYSTEM_PROMPT = `
You are a careful SQLite analyst.

Rules:
- Think step-by-step.
- When you need data, call the tool \`execute_sql\` with ONE SELECT query.
- Read-only only; no INSERT/UPDATE/DELETE/ALTER/DROP/CREATE/REPLACE/TRUNCATE.
- Limit to 5 rows unless user explicitly asks otherwise.
- If the tool returns 'Error:', revise the SQL and try again.
- Limit the number of attempts to 5.
- Prefer explicit column lists; avoid SELECT *.
`;

/**
 * Checkpointer (enables Studio thread history)
 * - Studio supplies thread_id automatically
 */
const checkpointer = new MemorySaver();

/**
 * Agent (default export for langgraph.json "<file>:default")
 */
const agent = createAgent({
  model: llm,
  tools: [execute_sql],
  systemPrompt: SYSTEM_PROMPT,
  checkpointer,
});

export default agent;

