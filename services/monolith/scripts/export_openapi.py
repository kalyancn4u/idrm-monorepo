"""Export the FastAPI OpenAPI schema to shared/contracts/v1/openapi.json."""
import json
from pathlib import Path
from app.main import app

def main() -> None:
    root = Path(__file__).resolve().parents[3]
    out = root / "shared" / "contracts" / "v1" / "openapi.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(app.openapi(), indent=2), encoding="utf-8")
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
