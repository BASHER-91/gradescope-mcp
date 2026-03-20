from mcp.server.fastmcp import FastMCP, Image
from gradescopeapi.classes.connection import GSConnection
import os
import sys
import tempfile
from pathlib import Path
from dotenv import load_dotenv
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Force Python to find the .env file in this exact directory
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# Initialize the server
mcp = FastMCP("Gradescope")

# Connect to Gradescope
connection = GSConnection()
try:
    email = os.getenv("GRADESCOPE_EMAIL")
    password = os.getenv("GRADESCOPE_PASSWORD")
    if not email or not password:
        raise ValueError("Email or password not found in .env file.")
    connection.login(email, password)
except Exception as e:
    print(f"Gradescope Login failed: {e}", file=sys.stderr)

@mcp.tool()
def get_courses() -> str:
    """Fetch all active courses for the logged-in Gradescope user."""
    try:
        courses = connection.account.get_courses()
        return str(courses)
    except Exception as e:
        return f"Failed to fetch courses. Error: {str(e)}"

@mcp.tool()
def get_assignments(course_id: str) -> str:
    """Fetch all assignments for a specific course ID to find assignment URLs."""
    try:
        assignments = connection.account.get_assignments(course_id)
        return str(assignments)
    except Exception as e:
        return f"Failed to fetch assignments for course {course_id}. Error: {str(e)}"

@mcp.tool()
def read_submission_page(course_id: str, assignment_id: str, page_number: int = 1) -> list:
    """
    Reads a SINGLE page of the student's evaluated submission PDF.
    Returns the image of the page and the total page count.
    To read an entire PDF, you MUST call this tool multiple times in a loop, 
    incrementing the page_number from 1 up to the total_pages.
    """
    try:
        temp_dir = tempfile.gettempdir()
        # Cache the file locally using the assignment ID so we don't redownload it for every page call
        cached_pdf_path = os.path.join(temp_dir, f"gradescope_{assignment_id}.pdf")
        
        # Only download if we haven't cached it yet
        if not os.path.exists(cached_pdf_path):
            base_url = f"https://www.gradescope.com/courses/{course_id}/assignments/{assignment_id}"
            response = connection.session.get(base_url)
            
            submission_url = response.url.split('#')[0]
            if not submission_url.endswith('.pdf'):
                pdf_url = f"{submission_url}.pdf"
            else:
                pdf_url = submission_url
                
            pdf_response = connection.session.get(pdf_url)
            
            if pdf_response.status_code != 200 or 'application/pdf' not in pdf_response.headers.get('Content-Type', ''):
                return [f"Failed to download PDF. Status: {pdf_response.status_code}. Attempted URL: {pdf_url}"]
                
            with open(cached_pdf_path, 'wb') as f:
                f.write(pdf_response.content)
        
        doc = fitz.open(cached_pdf_path)
        total_pages = len(doc)
        
        if page_number < 1 or page_number > total_pages:
            doc.close()
            return [f"Error: Page {page_number} does not exist. The document has {total_pages} pages."]
            
        # Convert from 1-indexed (user-facing) to 0-indexed (PyMuPDF)
        page = doc.load_page(page_number - 1)
        
        # SIGNIFICANT COMPRESSION APPLIED HERE:
        # 1. colorspace=fitz.csGRAY (Converts to grayscale, saving massive amounts of data)
        # 2. dpi=90 (Lowers resolution to standard web quality, still readable for AI vision)
        pix = page.get_pixmap(colorspace=fitz.csGRAY, dpi=90)
        
        # 3. jpeg quality=60 (Aggressive compression while maintaining text legibility)
        img_bytes = pix.tobytes("jpeg", 60)
        doc.close()
        
        return [
            f"Page {page_number} of {total_pages} for assignment {assignment_id}.",
            Image(data=img_bytes, format="jpeg")
        ]
        
    except Exception as e:
        return [f"Error processing submission: {str(e)}"]

@mcp.tool()
def draft_regrade_request(grader_comment: str, rubric_criteria: str, student_solution: str) -> str:
    """
    Pass the grader's comment, the rubric criteria, and the student's solution to this tool 
    to generate a strictly formatted regrade request.
    """
    instructions = f"""
    Draft a regrade request using the following data:
    
    Data:
    - Grader Comment: {grader_comment}
    - Rubric: {rubric_criteria}
    - Solution: {student_solution}
    
    Strict Execution Rules:
    - Output the response directly as markdown code.
    - Be highly concise and omit all formalities.
    - Use multiple paragraphs.
    - Use bold text strategically for easier reading.
    - Format all mathematical formulas and symbols using LaTeX ($ for inline, $$ for block).
    - Do not include any citations.
    - Structure the response in two distinct parts: 
      1. First, concisely answer the grader's comments.
      2. Second, argue for more marks by directly quoting the rubric and the solution.
    """
    return instructions

if __name__ == "__main__":
    mcp.run(transport="stdio")