# PDF Query Agentic Project

Have lots of PDF? Notes? This is a basic (version 1) agent where you can give a query/topic which you want to search from your lecture notes and the agent will pin point open the exact page in the exact PDF where that topic is present in a new, navigable window.

## Project Structure
|   client.py
|   config.py
|   logs.log
|   pdf_handler.py
|   prompt.py
|   Readme.md
|   server.py
|
+---Notes
|       Lecture1.pdf
|       Lecture2.pdf
|       Lecture3.pdf
|       Lecture4.pdf
|       Lecture5.pdf


### Files and Directories:
- `client.py`: Contains the client-side code for interacting with the server and querying the Gemini API.
- `config.py`: Configuration file to store API keys and other settings. 
- `logs.log`: Log file for keeping track of system operations and any errors.
- `pdf_handler.py`: Responsible for handling the PDF file operations, including rendering and passing PDFs to the API.
- `prompt.py`: Contains predefined prompts used to query the Gemini API.
- `server.py`: The server-side code to manage the PDF file paths and make the necessary API calls.
- `Notes/`: Folder containing lecture PDF files used for query matching.

## Features

- PDF Query Matching: The system queries each PDF to find relevant content using the Gemini API.
- Navigable PDF Viewer: If content is found, the PDF is opened in a new window with navigation options (Next/Previous pages).

