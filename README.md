# Decision Schema

<img src="images/decision-schema.svg" alt="Decision Schema logo" width="200" height="200" align="left">

A portable Markdown agent and one JSON Schema for folder-defined decisions.
The harness loads the persona, reads explicitly selected evidence, calls OpenAI
Decisions or Jev, and presents the returned decision. There is no bundled API
client or separate decision engine.

<br clear="left">

## Install the persona

Ask your agent:

> Install the decision agent by following the instructions in https://github.com/fbxai/decision-schema.

The [installation workflow in AGENTS.md](AGENTS.md#install-into-the-current-harness)
guides the agent to identify its active harness, install and register the persona,
preserve existing settings, and report verification results and prerequisites.
The instructions are harness-agnostic; this repository does not provide a
verified harness compatibility list. Your agent needs repository access and
permission to change the harness configuration. Registration and endpoint access
depend on that harness's capabilities.

Or manually copy `agents/decisions/` into your harness's `agents/` directory.

The portable bundle contains:

| File                                        | Purpose                                                  |
| ------------------------------------------- | -------------------------------------------------------- |
| [AGENTS.md](agents/decisions/AGENTS.md)     | Policy discovery, endpoint requests, and result handling |
| [IDENTITY.md](agents/decisions/IDENTITY.md) | Decision specialist persona                              |

Register or load both Markdown files using your harness's supported mechanism;
copying this folder alone does not register an agent in every harness.
`IDENTITY.md` is explicitly loaded by the operating instructions. Keep the schema
at the repository root as [decision.schema.json](decision.schema.json). Supply
that file to the harness for local or offline validation. The persona and policy
examples reference its intended published identifier:

```json
{
  "$schema": "https://github.com/fbxai/decision-schema/decision.schema.json"
}
```

The host model and decision backend are separate choices. The default backend is
OpenAI Decisions with `gpt-6-luna`; a harness can explicitly bind Jev instead.
Policies and evidence cannot override that binding. The harness needs authorized
source access and an invocation facility for the selected endpoint, such as an
existing native API, plugin, or approved HTTP execution. Chat-provider settings
alone do not establish support for decision requests.

## Endpoint contracts

The bundle's [operating instructions](agents/decisions/AGENTS.md) contain full
request examples and response handling rules. Use the selected policy questions
and caller-selected evidence, without sending `version` or `$schema` metadata.

| Policy    | Endpoint                      | Request fields                                           | Native answer structure                 |
| --------- | ----------------------------- | -------------------------------------------------------- | --------------------------------------- |
| Version 1 | OpenAI `POST /v1/decisions`   | `model: gpt-6-luna`, text `input`, `questions` array     | `answers` array, matched by `name`      |
| Version 2 | TypeSafe `POST /v1/systemone` | Harness-selected Jev `model`, `state`, named `questions` | `answers` object keyed by question name |

Both use JSON and bearer authentication. Direct OpenAI requests use
`OPENAI_API_KEY`; direct Jev requests use `TYPESAFE_API_KEY`. Native integrations
may use the corresponding harness-managed API-key secret. A host login is not a
substitute for endpoint credentials. Preserve native results, including values,
probabilities, confidence, model metadata, refusals, and usage. Never invent
thresholds or take actions selected by an answer.

See the [OpenAI Decisions reference](https://developers.openai.com/api/reference/resources/decisions/methods/create)
and [TypeSafe System One reference](https://docs.typesafe.ai/api/system-one).

## Policy definitions

The single schema validates authoring policies, not API responses, and provides
no executable runtime. A harness must perform the described validation and API
invocation. Its `$schema` reference helps editors; it does not select a provider.

Version 1 has 1–400 entries in a `questions` array, each with a unique `name`,
`type`, and nonempty `instructions`:

| Type        | Definition                            | Answer                                                     |
| ----------- | ------------------------------------- | ---------------------------------------------------------- |
| `predicate` | A condition                           | Probability from 0 to 1                                    |
| `choice`    | 2–255 typed values with descriptions  | Selected value, probabilities, confidence                  |
| `score`     | 2–10 ordered labels with descriptions | Weighted zero-based level index, probabilities, confidence |

Boolean `true` and string `"true"` are distinct choices. Scores may be fractional:
three levels produce a score in [0, 2]. The harness must check unique question
names, typed choice values, and score labels beyond schema validation, and reject
duplicate JSON object keys when loading policies.

Version 2 has a named `questions` object. `noul` uses instructions and optional
true/false criteria; `choice` uses a criteria mapping; `score` uses an ordered
criteria array. Instructions and descriptions may contain structured JSON.
The authoring schema accepts optional null content that may require omission or
normalization for the current endpoint. Schema validity is not wire compatibility.

See the [v1 example](examples/decisions.example.json),
[Jev example](examples/decisions.jev.example.json), and
[synthetic ticket](examples/ticket.txt). The policy examples use the configured
schema identifier above, independently of their local directory.

## Use Jev in a harness

A harness may replace the OpenAI binding in `agents/decisions/AGENTS.md` with an
explicit Jev model, endpoint invocation, and credential source. Keep policy
selection, evidence boundaries, result preservation, and failure handling intact.
The Markdown already documents both direct endpoint contracts; a separate Jev
client is not required when the harness can issue the request.

Migrate a policy only when requested: v1 names become question keys, predicates
become nouls, string choices become criteria mappings, and ordered score
descriptions become the criteria array. Preserve question meaning and score
order. Boolean choices need explicit string-key mappings, and score labels need
separate retention when callers use them. Never migrate policies as a side effect
of inspecting a ticket. Pin a model version when reproducibility matters; consult
the current [TypeSafe model reference](https://docs.typesafe.ai/models).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for testing, debugging, and schema publishing.

## References

- [OpenAI Decisions API](https://developers.openai.com/api/docs/guides/decisions)
- [TypeSafe Jev Primitives](https://docs.typesafe.ai/introduction)
