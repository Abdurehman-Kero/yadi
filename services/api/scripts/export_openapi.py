"""Write the API's OpenAPI document to a file (deterministic, for type generation)."""

import json
import sys
from pathlib import Path

from yadi.config import Settings
from yadi.main import create_app


def main(out: Path) -> None:
    # Dummy URL: nothing connects while building the schema.
    settings = Settings(
        _env_file=None, environment="test", database_url="postgresql+psycopg://u:p@127.0.0.1/x"
    )
    schema = create_app(settings).openapi()
    out.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
