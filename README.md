# Decision Schema

<img src="images/decision-schema.svg" alt="Decision Schema logo" width="200" height="200" align="left">

A portable Markdown agent and one JSON Schema for folder-defined decisions.
The harness loads the persona, reads explicitly selected evidence, calls OpenAI
Decisions or Jev, and presents the returned decision. There is no bundled API
client or separate decision engine.

<br clear="left">

## Inspect a Jira ticket

A user asks:

> Launch my decision agent to inspect Jira ticket EXAMPLE-123.

The harness loads the Decision Schema persona. The agent reads the folder's
`.agents/decisions.json`, fetches the requested ticket through the authorized Jira
connector, and submits its selected evidence and questions to the configured
decision endpoint. The actual response returns to the harness, which displays
the category, confidence, and probabilities and retains the full JSON result.
The agent does not assign or modify the ticket unless the calling workflow
separately requests that action.

The [Jira triage policy](examples/jira-triage.decisions.json) defines one choice:

| Choice | Work needed |
| --- | --- |
| `infrastructure` | Compute, networking, storage, deployment, or CI infrastructure |
| `software` | Application or library behavior, bugs, or features |
| `docs` | Documentation, guides, examples, or reference material |

To use this example, run from the caller's project folder and replace the source
path with your checkout location:

```sh
mkdir -p .agents
cp "/path/to/decision-schema/examples/jira-triage.decisions.json" .agents/decisions.json
```

The user supplies the ticket reference; no evidence file or helper-script command
is required. If the harness lacks Jira access, report that limitation instead of
inventing ticket content. A preview constructs the request without credentials
or network access and is explicitly unevaluated.

## Install the persona

Copy `agents/decisions/` into your harness's `agents/` directory:

```sh
mkdir -p "/path/to/harness/agents"
cp -R agents/decisions "/path/to/harness/agents/"
```

The portable bundle contains:

| File | Purpose |
| --- | --- |
| [AGENTS.md](agents/decisions/AGENTS.md) | Policy discovery, endpoint requests, and result handling |
| [IDENTITY.md](agents/decisions/IDENTITY.md) | Decision specialist persona |

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

| Policy | Endpoint | Request fields | Native answer structure |
| --- | --- | --- | --- |
| Version 1 | OpenAI `POST /v1/decisions` | `model: gpt-6-luna`, text `input`, `questions` array | `answers` array, matched by `name` |
| Version 2 | TypeSafe `POST /v1/systemone` | Harness-selected Jev `model`, `state`, named `questions` | `answers` object keyed by question name |

Both use JSON and bearer authentication. Direct OpenAI requests use
`OPENAI_API_KEY`; direct Jev requests use `TYPESAFE_API_KEY`. Native integrations
may use the corresponding harness-managed API-key secret. A host login is not a
substitute for endpoint credentials. Preserve native results, including values,
probabilities, confidence, model metadata, refusals, and usage. Never invent
thresholds or take actions selected by an answer.

See the [OpenAI Decisions reference](https://developers.openai.com/api/reference/resources/decisions/methods/create)
and [TypeSafe System One reference](https://docs.typesafe.ai/api/system-one).

## Harness cross-check

Primary documentation and source reviewed on 2026-10-29 show these integration
paths. These are documented capabilities, not live verification of an installed
harness or account.

| Harness | Existing decision integration |
| --- | --- |
| Hermes | An optional community plugin exposes [`jev_evaluate`](https://hermes-agent.nousresearch.com/docs/plugins/jev). It is separate from the host chat provider. |
| OMP | Native [`typesafe` and `openai-decisions` judgment APIs](https://github.com/can1357/oh-my-pi/blob/main/docs/models.md) use the `judge` model role. |
| Pi | Native [`models.classify()`](https://pi.dev/docs/latest/models#use-classifier-models) supports Jev and GPT-6 Luna through enabled codemode; extensions can use the model registry. |
| OpenCode | The v2 plugin API exposes experimental [`ctx.experimental.generate.decisions()`](https://opencode.ai/v2/docs/build/plugins/server/). This is a plugin API, not automatic execution from Markdown. |

Use a native interface when its semantics and returned data meet the contract.
For example, [Pi's documented classifier types](https://pi.dev/docs/latest/codemode#classify)
use `bool` rather than `noul`, normalize usage, and omit score distributions.
Do not pass the policy through blindly or claim that normalized output preserves
the complete upstream response. Use direct HTTP through an authorized runtime
when the native path cannot retain required fields. Choose the invocation path
before evaluation; do not retry failures through another provider.

Registration also differs: Hermes uses [context files and SOUL.md](https://hermes-agent.nousresearch.com/docs/user-guide/configuration#context-files-soulmd-agentsmd),
OMP has [Markdown subagent definitions](https://omp.sh/docs/subagent-authoring),
Pi loads [context files and prompt resources](https://pi.dev/docs/latest/configuration),
and OpenCode has [its own Markdown agent locations](https://opencode.ai/docs/agents/#markdown).
The `agents/decisions/` folder is our portable source bundle, not a universal
native registration convention.

## Policy definitions

The single schema validates authoring policies, not API responses, and provides
no executable runtime. A harness must perform the described validation and API
invocation. Its `$schema` reference helps editors; it does not select a provider.

Version 1 has 1–400 entries in a `questions` array, each with a unique `name`,
`type`, and nonempty `instructions`:

| Type | Definition | Answer |
| --- | --- | --- |
| `predicate` | A condition | Probability from 0 to 1 |
| `choice` | 2–255 typed values with descriptions | Selected value, probabilities, confidence |
| `score` | 2–10 ordered labels with descriptions | Weighted zero-based level index, probabilities, confidence |

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

## Development and publishing

Schema tests use `jsonschema` in an isolated `uv` environment:

```sh
uv run --with jsonschema python -B -m unittest discover -s tests -t . -v
```

Tests are offline and require no API key. They validate the schema and policy
examples; they do not establish that a particular harness loaded the persona,
made an API request, or has model access. Review Markdown links, request examples,
and registration claims when changing the persona. Keep test inputs synthetic.

The root schema uses Draft 2020-12 and internal references, so it can be published
as one file. Its `$id` matches the schema identifier in the policy examples.
The schema's own `$schema` remains the Draft 2020-12 meta-schema. Tests load the
root file directly and never fetch the identifier URL; publishing is separate
from local validation. Update `$id` and policy references together if adopting
a release-specific identifier later.
