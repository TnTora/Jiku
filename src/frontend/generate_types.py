from pathlib import Path  # noqa: INP001
from pydantic2ts import generate_typescript_defs

schemas_dir = Path(__file__).parent.parent / Path("api/schemas")
output_dir = Path(__file__).parent / Path("src/lib/api_types")

for f in schemas_dir.iterdir():
    if f.name.startswith("_"):
        continue
    print("generating Typescript types for:", f.stem)

    generate_typescript_defs(
        module=f"api.schemas.{f.stem}",
        output=str( output_dir / f"{f.stem}.ts"),
        json2ts_cmd="npx json2ts"
    )


