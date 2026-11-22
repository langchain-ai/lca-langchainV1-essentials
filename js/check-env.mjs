import { existsSync } from "node:fs";
import { pathToFileURL } from "node:url";

const baseOverrides = {
  OPENAI_API_KEY: ["OPENAI_API_BASE", "OPENAI_BASE_URL"],
  ANTHROPIC_API_KEY: ["ANTHROPIC_API_URL", "ANTHROPIC_BASE_URL"],
};

export function checkEnvironment(
  chatProviderKeys = ["OPENAI_API_KEY"],
  directApiKeys = [],
  env = process.env,
) {
  const gateway = env.LANGSMITH_GATEWAY;
  const enabled =
    gateway && !["false", "0", "no"].includes(gateway.toLowerCase());
  const gatewayKeys = chatProviderKeys.filter(
    (key) =>
      enabled &&
      baseOverrides[key] &&
      !baseOverrides[key].some((name) => env[name]),
  );
  const required = new Set([
    ...chatProviderKeys.filter((key) => !gatewayKeys.includes(key)),
    ...directApiKeys,
  ]);
  if (gatewayKeys.length) {
    required.add(
      env.LANGSMITH_GATEWAY_API_KEY
        ? "LANGSMITH_GATEWAY_API_KEY"
        : "LANGSMITH_API_KEY",
    );
  }
  const tracingEnabled = ["TRACING_V2", "TRACING"].some(
    (name) => (env[`LANGSMITH_${name}`] ?? env[`LANGCHAIN_${name}`]) === "true",
  );
  if (tracingEnabled)
    required.add(
      env.LANGSMITH_API_KEY
        ? "LANGSMITH_API_KEY"
        : env.LANGCHAIN_API_KEY
          ? "LANGCHAIN_API_KEY"
          : "LANGSMITH_API_KEY",
    );
  const issues = [...required]
    .filter((key) => {
      const value = env[key]?.trim();
      return (
        !value ||
        /^(your[_-]|<|replace[_-]|\*{4})/i.test(value) ||
        value.includes("...") ||
        ["changeme", "placeholder", "..."].includes(value.toLowerCase())
      );
    })
    .map((key) => `${key} is missing, empty, or a placeholder`);
  return { gatewayKeys, issues };
}

if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(process.argv[1]).href
) {
  if (existsSync(".env")) process.loadEnvFile(".env");
  const keys = process.argv.slice(2);
  const { gatewayKeys, issues } = checkEnvironment(
    keys.length ? keys : undefined,
  );
  if (gatewayKeys.length) {
    console.log(
      "LangSmith Gateway enabled for supported chat models; those calls do not need local provider keys.",
    );
    console.log(
      "Tools, embeddings, and evaluators keep direct credentials. Tracing is independent.",
    );
  }
  for (const issue of issues) console.error(issue);
  if (!issues.length)
    console.log(
      "Selected model credentials are configured (not a network authentication test).",
    );
  process.exitCode = issues.length ? 1 : 0;
}
