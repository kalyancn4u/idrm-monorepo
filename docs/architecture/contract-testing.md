# Contract Testing

## What this document is

How we prove that the backend honours the OpenAPI contract, and how we detect
breaking changes before they reach users.

## The two levels

Contract testing happens at two levels.

Level 1 - Is the OpenAPI file itself well-formed?
Level 2 - Does the live API actually behave as the contract says?

Both matter. A well-formed contract the API ignores is useless. A compliant
API with no contract is undocumented.

## Level 1 - Validate the spec

Tools: Redocly CLI, openapi-spec-validator, jest-expect-openapi.

    make contracts-validate

Fails if the spec has syntax errors, missing references, or invalid schemas.

## Level 2 - Python conformance (Schemathesis)

Schemathesis is a property-based testing framework for OpenAPI. It generates
test cases from the schema and validates that live responses conform.

    import schemathesis

    schema = schemathesis.from_path("shared/contracts/v1/openapi.json")

    @schema.parametrize()
    def test_api_conforms_to_contract(case):
        response = case.call()
        case.validate_response(response)

One test exercises every endpoint. It fails if the API returns a response
that violates the schema.

## Level 2 - JavaScript conformance (oasprey)

oasprey provides Jest matchers that assert HTTP responses satisfy an OpenAPI
spec.

    import { loadSpec } from 'oasprey';
    loadSpec('shared/contracts/v1/openapi.json');

    describe('GET /api/incidents', () => {
      it('satisfies the OpenAPI spec', async () => {
        const res = await axios.get('http://localhost:8000/api/incidents');
        expect(res).toSatisfyApiSpec();
      });
    });

## Cross-version compatibility (apidiffx)

apidiffx compares two API versions and classifies changes as breaking or
non-breaking. A removed endpoint is breaking. An added optional field is not.

    from apidiffx import assert_compatible

    def test_users_api(client):
        response = client.get("/api/users")
        assert_compatible(response, "snapshots/users.json")

A breaking change returns a non-zero exit code, which fails CI.

## Where each test lives

| Test type | Location | Framework |
|---|---|---|
| Spec validity | shared/contracts/v1/ | Redocly CLI |
| Backend conformance | services/monolith/tests/contract/ | Schemathesis + pytest |
| Backward compatibility | CI pipeline | apidiffx or oasdiff |
| Frontend client compatibility | apps/*/tests/contract/ | oasprey + Jest |

## How it fits in CI

The contract workflow (.github/workflows/contract.yml) runs on every change
to shared/contracts/.

    1. Lint the spec.
    2. Regenerate the typed client.
    3. Fail if the regenerated client differs from the committed one.

Step 3 ensures no one forgets to regenerate after a contract change.

## The rule

Never merge a contract change without regenerating the client. The CI check
exists to catch this. If it fails, run:

    make contracts-sync

and commit the result.

## Next steps

- The client itself: ./typed-api-clients.md
- The contract source: ../../shared/contracts/README.md
