import assert from "node:assert/strict";
import { test } from "node:test";
import { ChatOpenAI, OpenAIEmbeddings } from "@langchain/openai";
import { ChatAnthropic } from "@langchain/anthropic";
import { checkEnvironment } from "./check-env.mjs";

test("direct modes validate only the selected provider", () => {
  for (const flag of [undefined, "", "false", "FALSE", "0", "no"]) {
    const result = checkEnvironment(["OPENAI_API_KEY"], [], {
      LANGSMITH_GATEWAY: flag,
    });
    assert.deepEqual(result.gatewayKeys, []);
    assert.match(result.issues[0], /OPENAI_API_KEY/);
    assert.equal(
      checkEnvironment(["ANTHROPIC_API_KEY"], [], {
        ANTHROPIC_API_KEY: "direct-secret",
      }).issues.length,
      0,
    );
  }
});

test("gateway modes accept workspace or override keys without provider keys", () => {
  for (const flag of [
    "true",
    "TRUE",
    "1",
    "yes",
    "https://eu.gateway.smith.langchain.com",
  ]) {
    for (const key of ["LANGSMITH_API_KEY", "LANGSMITH_GATEWAY_API_KEY"]) {
      const result = checkEnvironment(
        ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"],
        [],
        { LANGSMITH_GATEWAY: flag, [key]: "gateway-secret" },
      );
      assert.equal(result.gatewayKeys.length, 2);
      assert.deepEqual(result.issues, []);
    }
  }
});

test("empty, missing, and placeholder credentials fail with override precedence", () => {
  for (const value of [undefined, "", " ", "your_key", "<key>", "changeme"]) {
    assert.equal(
      checkEnvironment(["OPENAI_API_KEY"], [], { OPENAI_API_KEY: value }).issues
        .length,
      1,
    );
    assert.equal(
      checkEnvironment(["OPENAI_API_KEY"], [], {
        LANGSMITH_GATEWAY: "true",
        LANGSMITH_API_KEY: value,
      }).issues.length,
      1,
    );
  }
  assert.match(
    checkEnvironment(["OPENAI_API_KEY"], [], {
      LANGSMITH_GATEWAY: "true",
      LANGSMITH_API_KEY: "valid-secret",
      LANGSMITH_GATEWAY_API_KEY: "your_key",
    }).issues[0],
    /LANGSMITH_GATEWAY_API_KEY/,
  );
});

test("direct tools, embeddings, unsupported providers, and base URLs are not exempt", () => {
  const env = {
    LANGSMITH_GATEWAY: "true",
    LANGSMITH_API_KEY: "gateway-secret",
  };
  assert.equal(
    checkEnvironment(
      ["OPENAI_API_KEY"],
      ["OPENAI_API_KEY", "TAVILY_API_KEY"],
      env,
    ).issues.length,
    2,
  );
  assert.match(
    checkEnvironment(["OTHER_API_KEY"], [], env).issues[0],
    /OTHER_API_KEY/,
  );
  assert.match(
    checkEnvironment(["OPENAI_API_KEY"], [], {
      ...env,
      OPENAI_BASE_URL: "https://other.example/v1",
    }).issues[0],
    /OPENAI_API_KEY/,
  );
});

test("locked chat integrations route gateway requests without changing embeddings", () => {
  const original = { ...process.env };
  try {
    for (const key of [
      "OPENAI_API_KEY",
      "ANTHROPIC_API_KEY",
      "OPENAI_API_BASE",
      "OPENAI_BASE_URL",
      "ANTHROPIC_API_URL",
      "ANTHROPIC_BASE_URL",
      "LANGSMITH_GATEWAY_API_KEY",
    ])
      delete process.env[key];
    process.env.LANGSMITH_GATEWAY = "https://eu.gateway.smith.langchain.com";
    process.env.LANGSMITH_API_KEY = "workspace-secret";
    process.env.LANGSMITH_TRACING = "false";
    const openai = new ChatOpenAI({ model: "gpt-5-mini" });
    const anthropic = new ChatAnthropic({ model: "claude-sonnet-4-6" });
    assert.equal(
      openai.clientConfig.baseURL,
      "https://eu.gateway.smith.langchain.com/openai/v1",
    );
    assert.equal(openai.apiKey, "workspace-secret");
    assert.equal(
      anthropic.apiUrl,
      "https://eu.gateway.smith.langchain.com/anthropic",
    );
    assert.equal(anthropic.apiKey, "workspace-secret");
    process.env.LANGSMITH_GATEWAY_API_KEY = "override-secret";
    assert.equal(
      new ChatOpenAI({ model: "gpt-5-mini" }).apiKey,
      "override-secret",
    );
    const embeddings = new OpenAIEmbeddings({ apiKey: "embedding-secret" });
    assert.equal(embeddings.clientConfig.apiKey, "embedding-secret");
    assert.notEqual(
      embeddings.clientConfig.baseURL,
      openai.clientConfig.baseURL,
    );
    process.env.LANGSMITH_GATEWAY = "false";
    process.env.OPENAI_API_KEY = "provider-secret";
    assert.equal(
      new ChatOpenAI({ model: "gpt-5-mini" }).apiKey,
      "provider-secret",
    );
  } finally {
    for (const key of Object.keys(process.env))
      if (!(key in original)) delete process.env[key];
    Object.assign(process.env, original);
  }
});

test("tracing credentials remain independent of gateway authentication", () => {
  const env = {
    LANGSMITH_GATEWAY: "true",
    LANGSMITH_GATEWAY_API_KEY: "gateway-secret",
  };
  for (const name of [
    "LANGSMITH_TRACING",
    "LANGSMITH_TRACING_V2",
    "LANGCHAIN_TRACING_V2",
  ]) {
    assert.match(
      checkEnvironment(["OPENAI_API_KEY"], [], { ...env, [name]: "true" })
        .issues[0],
      /LANGSMITH_API_KEY/,
    );
    assert.deepEqual(
      checkEnvironment(["OPENAI_API_KEY"], [], { ...env, [name]: "false" })
        .issues,
      [],
    );
  }
  for (const value of ["your-key", "****", "lsv2_..."]) {
    assert.match(
      checkEnvironment(["OPENAI_API_KEY"], [], {
        ...env,
        LANGSMITH_GATEWAY_API_KEY: value,
      }).issues[0],
      /LANGSMITH_GATEWAY_API_KEY/,
    );
  }
});
