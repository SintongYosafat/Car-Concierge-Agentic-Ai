import os
from typing import Optional

from langchain.tools import tool

# Get the path to the markdown file
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
terms_file_path = os.path.join(current_dir, "app", "tool", "data", "olx_booking_terms.md")

@tool
def get_olx_booking_terms(
    section: Optional[str] = None, format_type: str = "full"
) -> str:
    """
    Retrieve OLX booking process terms & conditions from documentation Knowledge Base as part of Help Center Activity.

    This tool provides comprehensive information about OLX booking policies,
    payment terms, cancellation rules, and dispute resolution procedures
    for vehicle transactions.

    Args:
        section (str, optional): Specific section to retrieve (currently unused - returns full content)
        format_type (str): Output format (currently unused - returns full content)

    Returns:
        str: Markdown-formatted terms and conditions content

    Examples:
        - Get all terms: get_olx_booking_terms()
        - Get payment info: get_olx_booking_terms(section="payment")
        - Get summary format: get_olx_booking_terms(format_type="summary")
    """
    try:
        # Read and return the markdown content as-is
        with open(terms_file_path, "r", encoding="utf-8") as file:
            return file.read()

    except FileNotFoundError:
        return "Error: OLX booking terms file not found. Please ensure the documentation is available."
    except Exception as e:
        return f"Error retrieving booking terms: {str(e)}"