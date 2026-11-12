import json
from pathlib import Path
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("notes_mcp_server")

NOTES_FILE = Path.home() / "my_notes.json"


# ---------- Utility functions ----------
def load_notes() -> dict:
    if NOTES_FILE.exists():
        return json.loads(NOTES_FILE.read_text())
    else:
        return {}


def save_notes(notes: dict):
    NOTES_FILE.write_text(json.dumps(notes, indent=2))


# ---------- Tools ----------
@mcp.tool()
def add_note(name: str, content: str) -> str:
    notes = load_notes()
    notes[name] = content
    save_notes(notes)
    return f"Note '{name}' was added successfully"


@mcp.tool()
def delete_note(name: str) -> str:
    notes = load_notes()
    if name in notes:
        del notes[name]
        save_notes(notes)
        return f"Note '{name}' was deleted successfully"
    else:
        return f"Note '{name}' was not found"


@mcp.tool()
def get_note(name: str) -> str:
    notes = load_notes()
    if name in notes:
        return notes[name]
    else:
        return f"Note '{name}' was not found"


@mcp.tool()
def list_notes() -> str:
    notes = load_notes()
    if not notes:
        return "No notes were found"
    else:
        return f"Notes: {', '.join(notes.keys())}"


# ---------- Resource ----------
@mcp.resource("note://{name}")
def get_note_resource(name: str) -> str:
    notes = load_notes()
    if name in notes:
        return notes[name]
    else:
        return f"Note '{name}' was not found"


# ---------- Prompt ----------
@mcp.prompt()
def summarize_note(name: str) -> str:
    notes = load_notes()
    if name not in notes:
        return f"Note '{name}' was not found"

    return f"""Here is a note titled '{name}':

{notes[name]}

Please summarize it in a concise manner. Keep the summary 100 words or less."""


if __name__ == "__main__":
    mcp.run()