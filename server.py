from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
import os
import subprocess
from dice_roller import DiceRoller

load_dotenv()

mcp = FastMCP("mcp-server")
client = TavilyClient(os.getenv("TAVILY_API_KEY"))

@mcp.tool()
def web_search(query: str) -> str:
    """Search the web for information about the given query"""
    search_results = client.get_search_context(query=query)
    return search_results

@mcp.tool()
def roll_dice(notation: str, num_rolls: int = 1) -> str:
    """Roll the dice with the given notation"""
    roller = DiceRoller(notation, num_rolls)
    return str(roller)

"""
Add your own tool here, and then use it through Cursor!
"""
@mcp.tool()
def send_gmail(to: str, subject: str, body: str) -> str:
    """Send an email using Gmail API. Requires GMAIL_USER and GMAIL_APP_PASSWORD environment variables."""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Get Gmail credentials from environment variables
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        
        if not gmail_user or not gmail_password:
            return "❌ Gmail credentials not configured. Please set GMAIL_USER and GMAIL_APP_PASSWORD environment variables."
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        text = msg.as_string()
        server.sendmail(gmail_user, to, text)
        server.quit()
        
        return f"✅ Email sent successfully to {to} with subject: {subject}"
        
    except Exception as e:
        return f"❌ Failed to send email: {str(e)}"

@mcp.tool()
def read_clipboard() -> str:
    """Read and return the current clipboard text (macOS). Uses `pbpaste`."""
    try:
        completed = subprocess.run([
            "pbpaste"
        ], check=False, capture_output=True, text=True)
        if completed.returncode != 0:
            return f"❌ Failed to read clipboard (pbpaste exited {completed.returncode})."
        return (completed.stdout or "").strip()
    except Exception as e:
        return f"❌ Error reading clipboard: {str(e)}"

@mcp.tool()
def write_clipboard(text: str) -> str:
    """Write the given text to the clipboard (macOS). Uses `pbcopy`."""
    try:
        completed = subprocess.run([
            "bash", "-lc", "pbcopy"
        ], input=text, text=True, capture_output=True)
        if completed.returncode != 0:
            return f"❌ Failed to write clipboard (pbcopy exited {completed.returncode})."
        return "✅ Clipboard updated"
    except Exception as e:
        return f"❌ Error writing clipboard: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")