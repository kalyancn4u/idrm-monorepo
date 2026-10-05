"""Contract tests: assert live API responses match the OpenAPI spec."""
import schemathesis
from pathlib import Path

SPEC = Path(__file__).resolve().parents[4] / "shared" / "contracts" / "v1" / "openapi.json"

if SPEC.exists():
    schema = schemathesis.from_path(str(SPEC))

    @schema.parametrize()
    def test_api_conforms_to_contract(case):
        response = case.call()
        case.validate_response(response)
