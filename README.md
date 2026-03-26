# Gradescope MCP Server

An MCP (Model Context Protocol) server for interacting with your Gradescope account directly from Claude Desktop. This extension allows Claude to fetch your courses, read assignment submissions, and draft regrade requests based on rubric criteria.

## Requirements

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) (Extremely fast Python package installer and resolver)
- Claude Desktop App

## Installation & Setup

### 1. Install `uv`

If you don't have `uv` installed, install it based on your operating system:

**macOS:**
```bash
brew install uv
```

**Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and Setup the Project

Clone this repository and verify the project structure:

```bash
git clone https://github.com/BASHER-91/gradescope-mcp.git
cd gradescope-mcp
```

Install the necessary dependencies using `uv`:

```bash
uv add mcp gradescopeapi python-dotenv pymupdf beautifulsoup4
```

### 3. Configure Environment Variables

Create a `.env` file in the root of the project to store your Gradescope credentials.

```bash
# macOS/Linux
touch .env

# Windows (Command Prompt)
echo. > .env
```

Open `.env` in a text editor and add your Gradescope email and password:

```env
GRADESCOPE_EMAIL=your_email@example.com
GRADESCOPE_PASSWORD=your_password
```

*(Note: Your credentials are used locally by the MCP server to authenticate with Gradescope's API.)*

### 4. Determine your `uv` Path

Claude Desktop needs the absolute path to your `uv` executable. Run the appropriate command for your OS to find it:

**macOS/Linux:**
```bash
which uv
```
*(Example output: `/Users/username/.local/bin/uv`)*

**Windows (Command Prompt):**
```cmd
where uv
```
**Windows (PowerShell):**
```powershell
Get-Command uv | Select-Object -ExpandProperty Definition
```
*(Example output: `C:\Users\username\.cargo\bin\uv.exe`)*

### 5. Configure Claude Desktop

You need to add the Gradescope MCP server to Claude Desktop's configuration file.

1. Open the Claude Desktop config file:
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

2. Add or update the `"mcpServers"` block to include the `gradescope` server. Use the absolute path to your `uv` executable, and the absolute path to your `gradescope-mcp` directory.

Here is an example configuration:

```json
{
  "mcpServers": {
    "gradescope": {
      "command": "/ABSOLUTE/PATH/TO/uv",
      "args": [
        "run",
        "--directory",
        "/ABSOLUTE/PATH/TO/gradescope-mcp",
        "server.py"
      ]
    }
  }
}
```
**Important:** 
- Replace `/ABSOLUTE/PATH/TO/uv` with the path you got in Step 4.
- Replace `/ABSOLUTE/PATH/TO/gradescope-mcp` with the path where you cloned this repo.
- On **Windows**, make sure to escape your slashes in the JSON string (e.g., `C:\\Users\\username\\.cargo\\bin\\uv.exe`).

### 6. Restart Claude Desktop

Quit Claude Desktop completely (Cmd+Q on Mac, or exiting from the system tray on Windows) and restart it. 

You should now see the Gradescope tools available in Claude Desktop (look for the hammer icon in the prompt bar).

## Available Tools

- **`get_courses`**: Fetch all active courses for the logged-in user.
- **`get_assignments(course_id)`**: Fetch all assignments for a specific course ID.
- **`read_submission_page(course_id, assignment_id, page_number)`**: Read a specific page of an evaluated submission PDF. Returns the page image and total page count.
- **`draft_regrade_request(grader_comment, rubric_criteria, student_solution)`**: Draft a strictly formatted regrade request (in LaTeX/Markdown) based on grading comments and rubrics.
