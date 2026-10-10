"""FastAPI server for the scene logger web app."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Path as PathParam
from fastapi.responses import FileResponse, Response

from flower.scene_table import SceneTable, ValidationError

STATIC_DIR = Path(__file__).parent / "static"
DEFAULT_DATA_DIR = Path("data")
NAME_PATTERN = r"^[A-Za-z0-9_-]+$"


def create_app(data_dir: str | Path = DEFAULT_DATA_DIR) -> FastAPI:
    """Create the scene logger app.

    Args:
        data_dir: Directory holding scene tables as '<name>.json' files.
            Created on first save if it does not exist.

    Returns:
        The configured FastAPI application.
    """
    data_dir = Path(data_dir)
    app = FastAPI(title="Flower scene logger")
    name_param = PathParam(pattern=NAME_PATTERN, max_length=100)

    def table_path(name: str) -> Path:
        return data_dir / f"{name}.json"

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/tables")
    def list_tables() -> list[str]:
        if not data_dir.is_dir():
            return []
        return sorted(p.stem for p in data_dir.glob("*.json"))

    @app.get("/api/tables/{name}")
    def get_table(name: str = name_param) -> dict:
        path = table_path(name)
        if not path.is_file():
            raise HTTPException(404, f"no table named {name!r}")
        try:
            return SceneTable.load_json(path).to_dict()
        except ValidationError as e:
            raise HTTPException(422, str(e)) from e

    @app.put("/api/tables/{name}")
    def put_table(body: dict, name: str = name_param) -> dict:
        try:
            table = SceneTable.from_dict(body)
        except ValidationError as e:
            raise HTTPException(422, str(e)) from e
        except (TypeError, ValueError, AttributeError) as e:
            raise HTTPException(422, f"malformed scene table: {e}") from e
        data_dir.mkdir(parents=True, exist_ok=True)
        table.save_json(table_path(name))
        return table.to_dict()

    @app.get("/api/tables/{name}/csv")
    def export_csv(name: str = name_param) -> Response:
        path = table_path(name)
        if not path.is_file():
            raise HTTPException(404, f"no table named {name!r}")
        table = SceneTable.load_json(path)
        csv_path = data_dir / f"{name}.csv"
        table.export_csv(csv_path)
        return Response(
            csv_path.read_text(),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{name}.csv"'},
        )

    return app


def main() -> None:
    """Run the server, storing tables in ./data.

    Binds to the HOST environment variable (default 127.0.0.1, localhost only)
    and listens on PORT (default 8000). Set HOST=0.0.0.0 to be reachable from
    outside a container; the app has no authentication, so only do this on a
    trusted network.
    """
    import uvicorn

    uvicorn.run(
        create_app(),
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8000")),
    )


if __name__ == "__main__":
    main()
