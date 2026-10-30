# Examples

Given that OpenAI & Jev decision schemas are different, this is an attempt to support both.

- OpenAI GPT6-luna example [[decisions.example.json]]
- TypeSafe Jev example [[decisions.jev.example.json]]

## Inspect a Jira ticket

With the content of a potential ticket in [[jira/ticket-123.txt]], and a pre-defined decision schema [[jira/decisions.json]] installed in the repo's `.agents/` folder, a user may ask:

> Launch my decision agent to inspect Jira ticket-123.

The harness loads the Decision Schema persona. The agent reads the folder's `.agents/decisions.json`, fetches the requested ticket through the authorized Jira connector, and submits its selected evidence and questions to the configured decision endpoint.
The actual response returns to the harness, which displays the category, confidence, and probabilities and retains the full JSON result. The agent does not assign or modify the ticket unless the calling workflow
separately requests that action.

The [[jira/decisions.json]] defines one choice, with 3 different values:

| Choice           | Work needed                                                    |
| ---------------- | -------------------------------------------------------------- |
| `infrastructure` | Compute, networking, storage, deployment, or CI infrastructure |
| `software`       | Application or library behavior, bugs, or features             |
| `docs`           | Documentation, guides, examples, or reference material         |

To use this example, run from the caller's project folder and replace the source
path with your checkout location:

```sh
mkdir -p .agents
cp "/path/to/decision-schema/examples/jira/decisions.json" .agents/decisions.json
```

The user supplies the ticket reference; no evidence file or helper-script command
is required. If the harness lacks Jira access, report that limitation instead of
inventing ticket content. A preview constructs the request without credentials
or network access and is explicitly unevaluated.
