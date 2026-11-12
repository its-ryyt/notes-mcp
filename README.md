# Notes MCP Server (Python + uv + VS Code)

A lightweight notes app built as an **MCP (Model Context Protocol) server**. It exposes all three MCP primitives:

| Primitive | Name             | Description                                              |
| --------- | ---------------- | -------------------------------------------------------- |
| Tool      | `add_note`       | Add or overwrite a note                                  |
| Tool      | `delete_note`    | Delete a note by name                                    |
| Tool      | `get_note`       | Get a note's content by name                             |
| Tool      | `list_notes`     | List all note names                                      |
| Resource  | `note://{name}`  | Expose a single note as a resource                       |
| Prompt    | `summarize_note` | Template prompt to summarize a note in 100 words or less |

Notes are stored in one JSON file: `C:\Users\<your-username>\my_notes.json`

---

## Prerequisites

- Windows + PowerShell
- VS Code with the **Python** and **GitHub Copilot** extensions
- Python 3.12+
- Node.js (only for MCP Inspector)
- `uv` package manager

---

## Project Structure

```
notes-mcp/
├── .venv/
├── .vscode/
│   └── mcp.json
├── .python-version
├── pyproject.toml
├── README.md
├── server.py
└── uv.lock
```

---

## Setup Steps

### 1. Install uv (one-time)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart VS Code, then check that it installed:

```powershell
uv --version
```

### 2. Open the project folder

1. Create the folder `C:\Project\notes-mcp`.
2. In VS Code, go to **File → Open Folder** and select it.
3. Open the terminal with **Ctrl + `**.

### 3. Initialize the uv project

```powershell
uv init
```

### 4. Create and activate the virtual environment

```powershell
uv venv
.venv\Scripts\activate
```

### 5. Install the MCP package

```powershell
uv add "mcp[cli]"
```

### 6. Select the Python interpreter

1. Press **Ctrl + Shift + P** and choose **Python: Select Interpreter**.
2. Pick `.venv\Scripts\python.exe`.
3. If imports are still underlined, press **Ctrl + Shift + P** and choose **Developer: Reload Window**.

### 7. Create `server.py` in the project root

```python
import json
from pathlib import Path
from mcp.server.mcpserver import MCPServer   # MCP SDK v2.x

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
```

> **Using MCP SDK v1.x?** Use `from mcp.server.fastmcp import FastMCP` and `mcp = FastMCP("notes_mcp_server")` instead.

### 8. Run the server

```powershell
uv run server.py
```

If the terminal waits with no errors, the server is running and listening over stdio. Press **Ctrl + C** to stop it.

---

## Testing with MCP Inspector

```powershell
uv run mcp dev server.py
```

The browser opens MCP Inspector. Check that the server shows **Connected**, then:

| Tab       | Action                                                         | Expected Result                           |
| --------- | -------------------------------------------------------------- | ----------------------------------------- |
| Tools     | `add_note` with name `meeting`, content `discuss sprint goals` | `Note 'meeting' was added successfully`   |
| Tools     | `list_notes`                                                   | `Notes: meeting`                          |
| Tools     | `get_note` with name `meeting`                                 | `discuss sprint goals`                    |
| Resources | Resource Templates → `note://{name}` with `meeting`            | Note content                              |
| Prompts   | `summarize_note` with name `meeting`                           | Filled-in summary prompt                  |
| Tools     | `delete_note` with name `meeting`                              | `Note 'meeting' was deleted successfully` |
| Tools     | `get_note` with name `meeting`                                 | `Note 'meeting' was not found`            |

---

## Using with GitHub Copilot in VS Code

### 1. Create `.vscode/mcp.json`

```json
{
  "servers": {
    "notes_mcp_server": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "${workspaceFolder}", "server.py"]
    }
  }
}
```

### 2. Start the server

Click **Start** above `"notes_mcp_server"` in `mcp.json`. When it's connected, it shows **✓ Running | 4 tools**.

### 3. Enable the tools in Copilot Chat

1. Open Copilot Chat with **Ctrl + Alt + I**.
2. Switch the mode to **Agent**.
3. Click the **sliders icon** next to the model picker (**Auto**).
4. Check `notes_mcp_server` and its 4 tools, then click **OK**.

### 4. Test with prompts

```
Add a note called meeting with content: discuss sprint goals
List all my notes
Get the note called meeting
Delete the note called meeting
```

Click **Allow** when Copilot asks to run a tool.

- **Prompt:** type `/` and choose `summarize_note`.
- **Resource:** click **+**, choose **MCP Resources**, then `note://{name}`.

---

## Errors Encountered and Fixes

### 1. `uv` is not recognized

```
uv : The term 'uv' is not recognized as the name of a cmdlet...
```

**Cause:** uv isn't installed, or it isn't on PATH.

**Fix:**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart VS Code. If uv is still not found, add it to PATH for the current session:

```powershell
$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
```

If the installer is blocked, install with pip instead: `pip install uv`.

### 2. `Failed to spawn: server.py — program not found`

```
error: Failed to spawn: server.py
  cause: program not found
```

**Cause:** `server.py` was inside `src\notes_mcp\`, not in the project root.

**Fix:** Move `server.py` to the project root (next to `pyproject.toml`), or run it with its full path:

```powershell
uv run src\notes_mcp\server.py
```

### 3. `No module named 'mcp.server.fastmcp'`

```
ModuleNotFoundError: No module named 'mcp.server.fastmcp'. This is mcp 2.x,
where FastMCP was renamed to MCPServer...
```

**Cause:** MCP SDK 2.x renamed `FastMCP` to `MCPServer`. The tutorial uses v1 code.

**Fix (option A, recommended):** Update the import:

```python
from mcp.server.mcpserver import MCPServer
mcp = MCPServer("notes_mcp_server")
```

**Fix (option B):** Downgrade to v1:

```powershell
uv add "mcp[cli]<2"
```

Reference: https://py.sdk.modelcontextprotocol.io/migration/

### 4. MCP server in VS Code: `The system cannot find the path specified. (os error 3)`

```
[warning] [server stderr] error: The system cannot find the path specified. (os error 3)
[info] Connection state: Error Process exited with code 2
```

**Cause:** The `--directory` path in `mcp.json` was wrong (`C:\Projects\...` instead of `C:\Project\...`).

**Fix:** Use `${workspaceFolder}` so VS Code fills in the path:

```json
"args": ["run", "--directory", "${workspaceFolder}", "server.py"]
```

Then click **Restart** in `mcp.json`. To check that the file exists:

```powershell
Test-Path C:\Project\notes-mcp\server.py
```

### 5. No tools (🔧) icon in Copilot Chat

**Cause:** Newer VS Code versions replaced the 🔧 icon with a **sliders icon**.

**Fix:** Click the **sliders icon** next to **Auto** in the chat box and enable `notes_mcp_server`. If it isn't listed, start the server from `mcp.json` first.

### 6. PowerShell blocks `.venv\Scripts\activate`

**Fix:**

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

---

## Result

- ✅ MCP server built with tools, a resource, and a prompt
- ✅ Tested in MCP Inspector
- ✅ Connected to GitHub Copilot Agent mode in VS Code
- ✅ Notes saved to `~/my_notes.json`
