# Contributing

## Testing

Schema tests use `jsonschema` in an isolated `uv` environment:

```sh
uv run --with jsonschema python -B -m unittest discover -s tests -t . -v
```

Tests are offline and require no API key. They validate the schema and policy
examples; they do not establish that a particular harness loaded the persona,
made an API request, or has model access. Review Markdown links, request examples,
and registration claims when changing the persona. Keep test inputs synthetic.

Tests load the repository's [decision.schema.json](decision.schema.json)
directly. They do not download the schema URL in policy examples.

## Debugging decisions

Inspect the selected policy, question names, ticket evidence, configured endpoint
and model, and actual request and response. Use the harness's request preview to
check the payload without making an API call; mark it as unevaluated. Keep
credentials out of previews, logs, and fixtures. Check errors, refusals, and any
fields normalized or omitted by a native harness integration before interpreting
the result.

## Schema structure and publishing

The root [decision.schema.json](decision.schema.json) uses three distinct fields:

| Field | Meaning in this repository |
| --- | --- |
| Schema's `$schema` | `https://json-schema.org/draft/2020-12/schema` declares the JSON Schema dialect used to interpret this file. |
| Schema's `$id` | `https://github.com/fbxai/decision-schema/decision.schema.json` identifies this project's schema. Policy examples use the same URL in their `$schema` field. |
| Schema's `$ref` entries | Paths such as `#/$defs/nativeConfig` reuse definitions within the same JSON file. |

Every current `$ref` is local to the file; there are no separate project schema
components to publish alongside it. The dialect and identifier URLs above do not
change that structure. The schema can therefore be distributed as one file.
Publishing that file is separate from validating the local checkout; a matching
identifier does not establish that the URL is already serving schema JSON.
Update `$id` and policy references together if adopting a release-specific
identifier later, and retain the dialect URL in the schema's own `$schema` field.
