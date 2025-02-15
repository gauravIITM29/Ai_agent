import re
import os
import sys
import glob
import json
import base64
import shutil
import requests
import subprocess
from dateutil import parser  
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.post("/run")
async def run_task(task: str):
    try:
        # Task parsing with GPT-4o-mini
        task_info = await parse_task(task)
        
        # Execute task based on type
        if task_info['task_type'] == 'A1':
            result = await execute_task_a1(task_info['email'])
        elif task_info['task_type'] == 'A2':
            result = await execute_task_a2()
        elif task_info['task_type'] == 'A3':
            result = await execute_task_a3(task)
        elif task_info['task_type'] == 'A4':
            result = await execute_task_a4(task)
        elif task_info['task_type'] == 'A5':
            result = await execute_task_a5(task)
        elif task_info['task_type'] == 'A6':
            result = await execute_task_a6(task)
        elif task_info['task_type'] == 'A7':
            result = await execute_task_a7(task)
        elif task_info['task_type'] == 'A8':
            result = await execute_task_a8(task)
        elif task_info['task_type'] == 'A9':
            result = await execute_task_a9(task)
        elif task_info['task_type'] == 'A10':
            result = await execute_task_a10(task)
        else:
            raise ValueError(f"Task type {task_info['task_type']} not implemented yet")
            
        return {"status": "success", "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.get("/read")
async def read_file(path: str):
    try:
        if not path.startswith("/data/"):
            raise HTTPException(status_code=400, detail="Can only access files in /data directory")
        
        # Map /data to ./data
        local_path = os.path.join(os.getcwd(), "data", os.path.relpath(path, "/data"))
        
        if not os.path.exists(local_path):
            raise HTTPException(status_code=404)
            
        with open(local_path, 'r') as f:
            content = f.read()
        return PlainTextResponse(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def parse_task(task_description: str) -> dict:
    """Parse task using GPT-4o-mini"""
    api_key = os.environ.get("AIPROXY_TOKEN")
    if not api_key:
        raise ValueError("AIPROXY_TOKEN environment variable not set")
        
    base_url = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Handle both A1 and A2 tasks
    system_prompt = """
    Identify which task type (A1, A2 or A3, A4 ... and so on) this request matches:

    Task A1 examples (data generation):
    - "Install uv and run datagen.py with email@example.com"
    - "Run the data generation script with email"
    - "Execute datagen.py using email"
    For Task A1: {"task_type": "A1", "email": "the_email_address"}

    Task A2 examples (markdown formatting):
    - "Format /data/format.md using prettier@3.4.2"
    - "Use prettier to format the markdown file"
    - "Run prettier on format.md"
    For Task A2: {"task_type": "A2", "email": null}

    Task A3 examples (counting weekdays):
    - The file /data/dates.txt contains a list of dates, one per line. Count the number of Wednesdays in the list, and write just the number to /data/dates-wednesdays.txt
    - Write the # of Thursdays in /data/extracts.txt into /data/extracts-count.txt
    - /data/contents.log में कितने रविवार हैं? गिनो और /data/contents.dates में लिखो
    - /data/contents.logல எத்தனை ஞாயிறு இருக்குனு கணக்கு போட்டு, அதை /data/contents.datesல எழுது
    - "Count the number of Wednesdays in /data/dates.txt"
    - "How many Thursdays are in the dates file?"
    - "Write the number of Wednesdays to dates-wednesdays.txt"
    - "/data/contents.log में कितने रविवार हैं?"
    - In this task there are 
    For Task A3 : {"task_type": "A3"}

    Return ONLY a JSON object with these keys:
    
    Return ONLY a JSON object with:

    Task A4 examples (sorting contacts):
    - "Sort contacts.json by last_name and first_name"
    - "Sort the contacts by surname then given name"
    - "Order the contacts list alphabetically by family name"
    - "Arrange the contact list by last name first, then first name"

    Task A5 examples (getting recent log lines):
    - "Write the first line of the 10 most recent .log files"
    - "Get first lines from newest log files"
    - "Extract first line from recent logs"
    - "Show me the beginning of the latest log files"
    Return ONLY a JSON object with:
    {"task_type": "A5"}

    Task A6 examples (markdown indexing):
    - "Create an index of H1 headers from markdown files"
    - "Find titles in .md files"
    - "Extract first # heading from each markdown file"
    - "Make a JSON index of markdown titles"
    Return ONLY a JSON object with:
    {"task_type": "A6"}

    Task A7 examples (email extraction):
    - "Get the sender's email from email.txt"
    - "Extract email address from the message"
    - "Who sent the email? Write their address to file"
    - "Find the from address in the email"
    Return ONLY a JSON object with:
    {"task_type": "A7"}

    Task A8 examples (credit card extraction):
    - "Get the card number from the image"
    - "Extract credit card number from PNG"
    - "What's the number on the credit card?"
    - "Read the card number and save it"
    Return ONLY a JSON object with:
    {"task_type": "A8"}

    Task A9 examples (finding similar comments):
    - "Find most similar comments using embeddings"
    - "Which comments are most alike?"
    - "Use embeddings to find similar comment pairs"
    - "Find comments that are closest in meaning"
    Return ONLY a JSON object with:
    {"task_type": "A9"}

    Task A10 exam[les (calculating ticket sales):
    - "Calculate total sales for Gold tickets"
    - "Sum up Gold ticket type sales"
    - "What's the total value of Gold tickets?"
    - "Add up all Gold ticket sales"
    Return ONLY a JSON object with:
    {"task_type": "A10"}

    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task_description}
    ]
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages
    }
    
    response = requests.post(
        url=base_url,
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"LLM API error: {response.text}")
        
    result = response.json()
    parsed = json.loads(result["choices"][0]["message"]["content"])
    print(f"Task identified as: {parsed}")
    return parsed

async def execute_task_a1(email: str) -> str:
    """Handle Task A1: Install uv and run datagen.py"""
    # Create both /data and ./data directories
    local_data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(local_data_dir, exist_ok=True)
    os.makedirs("/data", exist_ok=True)
    print(f"Data directories created/checked: {local_data_dir} and /data")
    
    # First check for UV installation
    try:
        subprocess.run(['uv', '--version'], check=True)
        print("UV is already installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Installing uv...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'uv'], check=True)
    
    # Download datagen.py
    url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
    print(f"Downloading script from: {url}")
    response = requests.get(url)
    response.raise_for_status()
    print("Script content:", response.text[:200])
    
    # Save to a file in the current directory
    script_path = os.path.join(os.getcwd(), "datagen.py")
    with open(script_path, "w") as f:
        f.write(response.text)
    print(f"Saved script to: {script_path}")
    
    try:
        print(f"Running datagen.py with email: {email}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Contents of local data directory before: {os.listdir(local_data_dir)}")
        
        # Run the script with output capture
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = os.getcwd()
            result = subprocess.run(
                ['uv', 'run', script_path, email],
                check=True,
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
                env=env
            )
            print("Script stdout:", result.stdout)
            print("Script stderr:", result.stderr)
            
            # Copy files from /data to ./data if they exist
            if os.path.exists("/data"):
                for file in os.listdir("/data"):
                    src = os.path.join("/data", file)
                    dst = os.path.join(local_data_dir, file)
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
                        print(f"Copied {src} to {dst}")
            
            print(f"Contents of local data directory after: {os.listdir(local_data_dir)}")
            return f"datagen.py executed successfully. Files created in {local_data_dir}"
            
        except subprocess.CalledProcessError as e:
            print("Script failed with error:")
            print("stdout:", e.stdout)
            print("stderr:", e.stderr)
            raise ValueError(f"Script failed: {e.stderr}")
            
    finally:
        # Clean up script file
        if os.path.exists(script_path):
            os.unlink(script_path)


async def execute_task_a2():
    """Handle Task A2: Format markdown with prettier"""
    local_data_dir = os.path.join(os.getcwd(), "data")
    input_file = os.path.join(local_data_dir, "format.md")
    
    print(f"Formatting file: {input_file}")
    
    # Install prettier if not already installed
    try:
        subprocess.run(['npx', 'prettier', '--version'], check=True, capture_output=True)
        print("Prettier is already installed")
    except subprocess.CalledProcessError:
        print("Installing prettier@3.4.2...")
        subprocess.run(['npm', 'install', '--no-save', 'prettier@3.4.2'], check=True)
    
    # Format the file in-place
    try:
        result = subprocess.run(
            ['npx', 'prettier@3.4.2', '--write', input_file],
            check=True,
            capture_output=True,
            text=True
        )
        print("Prettier stdout:", result.stdout)
        print("Prettier stderr:", result.stderr)
        
        # Copy file back to /data if needed
        if os.path.exists("/data"):
            shutil.copy2(input_file, "/data/format.md")
            print("Copied formatted file back to /data directory")
        
        return "File formatted successfully"
        
    except subprocess.CalledProcessError as e:
        print("Prettier failed with error:")
        print("stdout:", e.stdout)
        print("stderr:", e.stderr)
        raise ValueError(f"Prettier failed: {e.stderr}")
    


async def execute_task_a3(task_description: str) -> str:
    """
    Handle Task A3: Count weekdays in dates file
    Args:
        task_description (str): The task description that may contain input/output file paths
    Returns:
        str: Success message
    """
    try:
        # Default file paths
        input_file = "/data/dates.txt"
        output_file = "/data/dates-wednesdays.txt"

        # Read the input file
        local_data_dir = os.path.join(os.getcwd(), "data")
        local_input = os.path.join(local_data_dir, os.path.basename(input_file))
        
        with open(local_input, 'r') as f:
            dates = f.read().splitlines()

        # Count the Wednesdays
        wednesday_count = 0
        for date_str in dates:
            try:
                # Use dateutil.parser to handle various date formats
                date_obj = parser.parse(date_str.strip())
                
                # Check if it's a Wednesday (weekday() returns 2 for Wednesday)
                if date_obj.weekday() == 2:
                    wednesday_count += 1
            except Exception as e:
                print(f"Warning: Couldn't parse date '{date_str}': {e}")
                continue

        # Write the result to both local and /data directories
        # First write to local directory
        local_output = os.path.join(local_data_dir, os.path.basename(output_file))
        with open(local_output, 'w') as f:
            f.write(str(wednesday_count))

        # Then write to /data directory if it exists
        if os.path.exists("/data"):
            os.makedirs("/data", exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(str(wednesday_count))

        return f"Successfully counted {wednesday_count} Wednesdays and wrote to {output_file}"

    except Exception as e:
        raise ValueError(f"Error in date counting task: {str(e)}")


async def execute_task_a4(task_description: str) -> str:
    """
    Handle Task A4: Sort contacts JSON by last_name, first_name
    Args:
        task_description (str): The task description
    Returns:
        str: Success message
    """
    try:
        # Define input and output paths
        input_file = "/data/contacts.json"
        output_file = "/data/contacts-sorted.json"
        
        # Read from local data directory
        local_data_dir = os.path.join(os.getcwd(), "data")
        local_input = os.path.join(local_data_dir, os.path.basename(input_file))
        
        # Read and parse JSON
        with open(local_input, 'r') as f:
            contacts = json.load(f)
            
        # Ensure we have a list of contacts
        if not isinstance(contacts, list):
            raise ValueError("Input JSON must be an array of contacts")
            
        # Sort contacts by last_name, then first_name
        sorted_contacts = sorted(
            contacts,
            key=lambda x: (x.get('last_name', '').lower(), x.get('first_name', '').lower())
        )
        
        # Write to local directory
        local_output = os.path.join(local_data_dir, os.path.basename(output_file))
        with open(local_output, 'w') as f:
            json.dump(sorted_contacts, f, indent=2)
            
        # Write to /data directory if it exists
        if os.path.exists("/data"):
            os.makedirs("/data", exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(sorted_contacts, f, indent=2)
                
        return f"Successfully sorted {len(contacts)} contacts and wrote to {output_file}"
        
    except FileNotFoundError:
        raise ValueError(f"Input file not found: {input_file}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in input file: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error in contact sorting task: {str(e)}")



async def execute_task_a5(task_description: str) -> str:
    """
    Handle Task A5: Get first lines of recent log files
    Args:
        task_description (str): The task description
    Returns:
        str: Success message
    """
    try:
        # First try the absolute /data path
        if os.path.exists("/data/logs"):
            logs_dir = "/data/logs"
        else:
            # Fallback to local data directory
            local_data_dir = os.path.join(os.getcwd(), "data")
            logs_dir = os.path.join(local_data_dir, "logs")

        output_file = "/data/logs-recent.txt"
        
        print(f"Looking for log files in: {logs_dir}")
        
        # Get all .log files with their modification times
        log_files = []
        for log_file in glob.glob(os.path.join(logs_dir, "*.log")):
            try:
                mtime = os.path.getmtime(log_file)
                log_files.append((mtime, log_file))
                print(f"Found log file: {log_file}")
            except Exception as e:
                print(f"Warning: Could not get mtime for {log_file}: {e}")
                continue
            
        if not log_files:
            raise ValueError(f"No .log files found in the logs directory: {logs_dir}")
            
        # Sort by modification time (most recent first) and take top 10
        recent_logs = sorted(log_files, reverse=True)[:10]
        
        # Extract first line from each file
        first_lines = []
        for _, log_path in recent_logs:
            try:
                with open(log_path, 'r') as f:
                    first_line = f.readline().strip()
                    if first_line:  # Only add non-empty lines
                        # Add filename and first line
                        filename = os.path.basename(log_path)
                        first_lines.append(f"{filename}: {first_line}")
                        print(f"Processed {filename}")
            except Exception as e:
                print(f"Warning: Could not read {log_path}: {e}")
                continue
                
        # Write results to output file
        # First write to local directory
        local_data_dir = os.path.join(os.getcwd(), "data")
        local_output = os.path.join(local_data_dir, "logs-recent.txt")
        os.makedirs(os.path.dirname(local_output), exist_ok=True)
        
        with open(local_output, 'w') as f:
            f.write('\n'.join(first_lines))
            
        # Then write to /data directory if it exists
        if os.path.exists("/data"):
            os.makedirs("/data", exist_ok=True)
            with open(output_file, 'w') as f:
                f.write('\n'.join(first_lines))
                
        return f"Successfully wrote first lines of {len(first_lines)} recent log files to {output_file}"
        
    except Exception as e:
        raise ValueError(f"Error in log processing task: {str(e)}")
    

async def execute_task_a6(task_description: str) -> str:
    """
    Handle Task A6: Create index of markdown H1 headers using regex
    Args:
        task_description (str): The task description
    Returns:
        str: Success message
    """
    try:
        # Define paths
        if os.path.exists("/data/docs"):
            docs_dir = "/data/docs"
        else:
            local_data_dir = os.path.join(os.getcwd(), "data")
            docs_dir = os.path.join(local_data_dir, "docs")
            
        output_file = "/data/docs/index.json"
        print(f"Looking for markdown files in: {docs_dir}")
        
        # Find all .md files recursively
        md_files = []
        for root, _, files in os.walk(docs_dir):
            for file in files:
                if file.endswith('.md'):
                    full_path = os.path.join(root, file)
                    # Get path relative to docs directory
                    rel_path = os.path.relpath(full_path, docs_dir)
                    md_files.append((full_path, rel_path))
                    print(f"Found markdown file: {rel_path}")
                    
        if not md_files:
            raise ValueError(f"No markdown files found in {docs_dir}")
            
        # Process each file and extract H1 headers
        index = {}
        h1_pattern = re.compile(r'^\s*#\s+(.+)$', re.MULTILINE)
        
        for full_path, rel_path in md_files:
            try:
                with open(full_path, 'r') as f:
                    content = f.read()
                    
                # Find first H1 header
                match = h1_pattern.search(content)
                if match:
                    title = match.group(1).strip()
                    index[rel_path] = title
                    print(f"Extracted title from {rel_path}: {title}")
                else:
                    print(f"No H1 header found in {rel_path}")
                    # Use filename as fallback title
                    title = os.path.splitext(os.path.basename(rel_path))[0]
                    index[rel_path] = title
                    
            except Exception as e:
                print(f"Warning: Could not process {rel_path}: {e}")
                continue
                
        # Write index to both local and /data directories
        local_data_dir = os.path.join(os.getcwd(), "data")
        local_docs_dir = os.path.join(local_data_dir, "docs")
        os.makedirs(local_docs_dir, exist_ok=True)
        local_output = os.path.join(local_docs_dir, "index.json")
        
        with open(local_output, 'w') as f:
            json.dump(index, f, indent=2)
            
        # Then write to /data directory if it exists
        if os.path.exists("/data"):
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(index, f, indent=2)
                
        return f"Successfully created index for {len(index)} markdown files in {output_file}"
        
    except Exception as e:
        raise ValueError(f"Error in markdown indexing task: {str(e)}")
    

async def _extract_email_with_gpt(content: str, api_key: str) -> str:
    """
    Use GPT model to extract sender's email address from email content
    """
    base_url = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    system_prompt = """
    Extract ONLY the sender's email address from the given email message.
    Return just the email address, nothing else.
    Example response: "john.doe@example.com"
    If no email address is found, return an empty string.
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ]
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages
    }
    
    response = requests.post(
        url=base_url,
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"LLM API error: {response.text}")
        
    result = response.json()
    return result["choices"][0]["message"]["content"].strip()

async def execute_task_a7(task_description: str) -> str:
    """
    Handle Task A7: Extract sender's email from email.txt
    Args:
        task_description (str): The task description
    Returns:
        str: Success message
    """
    try:
        # Get API key
        api_key = os.environ.get("AIPROXY_TOKEN")
        if not api_key:
            raise ValueError("AIPROXY_TOKEN environment variable not set")
        
        # Define input and output paths
        input_file = "/data/email.txt"
        output_file = "/data/email-sender.txt"
        
        # Read from local data directory
        local_data_dir = os.path.join(os.getcwd(), "data")
        local_input = os.path.join(local_data_dir, "email.txt")
        
        # Read the email content
        try:
            with open(local_input, 'r') as f:
                email_content = f.read()
        except FileNotFoundError:
            raise ValueError(f"Email file not found: {input_file}")
        
        # Extract email using GPT
        email_address = await _extract_email_with_gpt(email_content, api_key)
        
        if not email_address:
            raise ValueError("No email address found in the content")
            
        print(f"Extracted email address: {email_address}")
        
        # Write to local directory
        local_output = os.path.join(local_data_dir, "email-sender.txt")
        with open(local_output, 'w') as f:
            f.write(email_address)
            
        # Write to /data directory if it exists
        if os.path.exists("/data"):
            os.makedirs("/data", exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(email_address)
                
        return f"Successfully extracted sender's email address to {output_file}"
        
    except Exception as e:
        raise ValueError(f"Error in email extraction task: {str(e)}")



async def _find_image_file(directory: str, possible_names: list) -> str:
    """
    Try to find the image file with different possible names
    Returns the full path if found, raises ValueError if not found
    """
    for name in possible_names:
        file_path = os.path.join(directory, name)
        if os.path.exists(file_path):
            print(f"Found image file: {file_path}")
            return file_path
    
    # If no file is found, raise error with attempted paths
    raise ValueError(f"Could not find credit card image. Tried: {', '.join(possible_names)}")


async def _extract_card_number_with_gpt(image_path: str, api_key: str) -> str:
    """
    Use GPT model to extract credit card number from image using correct image_url format
    """
    base_url = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    
    print(f"Reading image from: {image_path}")
    
    # Read and encode image
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # More specific prompt focusing on white text on blue background
    messages = [
        {
            "role": "system",
            "content": "You are a credit card number reader. Look for large white digits on a blue background. The number should be 16 digits. Return ONLY the digits with no spaces."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What is the 16-digit number shown in white text on the blue background?"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_data}"
                    }
                }
            ]
        }
    ]
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0  # Set to 0 for more precise extraction
    }
    
    print("Sending request to API...")
    response = requests.post(
        url=base_url,
        headers=headers,
        json=payload
    )
    
    print(f"API Response status: {response.status_code}")
    if response.status_code != 200:
        print(f"API Error response: {response.text}")
        raise Exception(f"LLM API error: {response.text}")
        
    result = response.json()
    raw_text = result["choices"][0]["message"]["content"]
    print(f"Raw GPT response: {raw_text}")
    
    # Clean the response to get only digits
    card_number = ''.join(filter(str.isdigit, raw_text))
    print(f"Extracted digits: {card_number}")
    
    if len(card_number) != 16:
        print(f"Warning: Expected 16 digits, got {len(card_number)} digits")
        # Additional attempt to find 16 consecutive digits in the response
        import re
        matches = re.findall(r'\d{16}', raw_text)
        if matches:
            card_number = matches[0]
            print(f"Found 16-digit sequence: {card_number}")
    
    return card_number

async def execute_task_a8(task_description: str) -> str:
    """
    Handle Task A8: Extract credit card number from image
    Args:
        task_description (str): The task description
    Returns:
        str: Success message
    """
    try:
        api_key = os.environ.get("AIPROXY_TOKEN")
        if not api_key:
            raise ValueError("AIPROXY_TOKEN environment variable not set")
        
        # Define possible file names
        possible_names = [
            "credit-card.png",
            "credit_card.png",
            "creditcard.png",
            "card.png"
        ]
        
        # Try both /data and local data directory
        local_data_dir = os.path.join(os.getcwd(), "data")
        found_file = None
        
        # First try /data directory
        if os.path.exists("/data"):
            for name in possible_names:
                path = os.path.join("/data", name)
                if os.path.exists(path):
                    found_file = path
                    break
        
        # Try local directory if not found
        if not found_file:
            for name in possible_names:
                path = os.path.join(local_data_dir, name)
                if os.path.exists(path):
                    found_file = path
                    break
        
        if not found_file:
            raise ValueError(f"Could not find credit card image. Tried: {', '.join(possible_names)}")
        
        print(f"Found image file: {found_file}")
        
        # Extract card number using GPT
        card_number = await _extract_card_number_with_gpt(found_file, api_key)
        
        if not card_number:
            raise ValueError("No card number extracted from the image")
        
        if len(card_number) != 16:
            raise ValueError(f"Extracted number has invalid length: {len(card_number)} digits")
        
        print(f"Successfully extracted card number: {card_number}")
        
        # Write outputs
        output_filename = "credit-card.txt"
        
        # Write to both directories
        for output_dir in [local_data_dir, "/data"]:
            if os.path.exists(output_dir):
                output_path = os.path.join(output_dir, output_filename)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w') as f:
                    f.write(card_number)
                print(f"Wrote result to: {output_path}")
        
        return f"Successfully extracted credit card number and saved to files"
        
    except Exception as e:
        raise ValueError(f"Error in card number extraction task: {str(e)}")
    


import requests
import numpy as np
from typing import List, Tuple

async def _get_embedding(text: str, api_key: str) -> List[float]:
    """Get embedding for text using GPT-4o-mini"""
    base_url = "http://aiproxy.sanand.workers.dev/openai/v1/embeddings"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "input": text
    }
    
    response = requests.post(
        url=base_url,
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.text}")
        
    result = response.json()
    return result["data"][0]["embedding"]

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    v1 = np.array(v1)
    v2 = np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

import os
import requests
from itertools import combinations

async def _compare_comments(comment1: str, comment2: str, api_key: str) -> float:
    """Compare two comments using GPT to get similarity score"""
    base_url = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    system_prompt = """
    You are a similarity scorer. Given two comments, return ONLY a number between 0 and 1 
    indicating how similar they are in meaning, where 1 means identical meaning and 0 means 
    completely different. Return just the number, nothing else.
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Comment 1: {comment1}\nComment 2: {comment2}"}
    ]
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0
    }
    
    response = requests.post(
        url=base_url,
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.text}")
        
    result = response.json()
    try:
        # Extract and convert the similarity score
        score = float(result["choices"][0]["message"]["content"].strip())
        return min(max(score, 0), 1)  # Ensure score is between 0 and 1
    except (ValueError, KeyError) as e:
        print(f"Error parsing response: {e}")
        return 0

async def execute_task_a9(task_description: str) -> str:
    """
    Handle Task A9: Find most similar comments using GPT
    Args:
        task_description (str): The task description
    Returns:
        str: Success message
    """
    try:
        # Get API key
        api_key = os.environ.get("AIPROXY_TOKEN")
        if not api_key:
            raise ValueError("AIPROXY_TOKEN environment variable not set")
        
        # Define input and output paths
        input_file = "/data/comments.txt"
        output_file = "/data/comments-similar.txt"
        
        # Read from local data directory
        local_data_dir = os.path.join(os.getcwd(), "data")
        local_input = os.path.join(local_data_dir, "comments.txt")
        
        # Read comments
        try:
            with open(local_input, 'r') as f:
                comments = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            raise ValueError(f"Comments file not found: {input_file}")
            
        if len(comments) < 2:
            raise ValueError("Need at least 2 comments to find similar pairs")
            
        print(f"Processing {len(comments)} comments...")
        
        # Find most similar pair
        max_similarity = -1
        most_similar_pair = None
        
        # Process comment pairs
        for comment1, comment2 in combinations(comments, 2):
            print(f"Comparing comments:\n1: {comment1[:50]}...\n2: {comment2[:50]}...")
            similarity = await _compare_comments(comment1, comment2, api_key)
            print(f"Similarity score: {similarity:.3f}")
            
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_pair = (comment1, comment2)
                print(f"New most similar pair found (similarity: {similarity:.3f})")
        
        if not most_similar_pair:
            raise ValueError("Could not find similar comments")
            
        print(f"Most similar comments have similarity: {max_similarity:.3f}")
        
        # Write to local directory
        local_output = os.path.join(local_data_dir, "comments-similar.txt")
        os.makedirs(os.path.dirname(local_output), exist_ok=True)
        with open(local_output, 'w') as f:
            f.write('\n'.join(most_similar_pair))
            
        # Write to /data directory if it exists
        if os.path.exists("/data"):
            os.makedirs("/data", exist_ok=True)
            with open(output_file, 'w') as f:
                f.write('\n'.join(most_similar_pair))
                
        return f"Successfully found most similar comments and wrote to {output_file}"
        
    except Exception as e:
        raise ValueError(f"Error in comment similarity task: {str(e)}")
    

import os
import sqlite3

async def execute_task_a10(task_description: str) -> str:
    """
    Handle Task A10: Calculate total Gold ticket sales
    Args:
        task_description (str): The task description
    Returns:
        str: Success message
    """
    try:
        # Define input and output paths
        input_file = "/data/ticket-sales.db"
        output_file = "/data/ticket-sales-gold.txt"
        
        # Read from local data directory
        local_data_dir = os.path.join(os.getcwd(), "data")
        local_input = os.path.join(local_data_dir, "ticket-sales.db")
        
        # Check if database exists
        if not os.path.exists(local_input):
            raise ValueError(f"Database file not found: {input_file}")
            
        print(f"Processing database: {local_input}")
        
        # Connect to SQLite database
        conn = sqlite3.connect(local_input)
        cursor = conn.cursor()
        
        try:
            # Calculate total sales for Gold tickets (price * units)
            query = """
            SELECT SUM(price * units) as total_sales
            FROM tickets
            WHERE type = 'Gold'
            """
            
            cursor.execute(query)
            result = cursor.fetchone()
            
            if result[0] is None:
                raise ValueError("No Gold tickets found in database")
                
            total_sales = float(result[0])
            print(f"Total Gold ticket sales: {total_sales}")
            
            # Format the number with 2 decimal places
            formatted_total = "{:.2f}".format(total_sales)
            
            # Write to local directory
            local_output = os.path.join(local_data_dir, "ticket-sales-gold.txt")
            os.makedirs(os.path.dirname(local_output), exist_ok=True)
            with open(local_output, 'w') as f:
                f.write(formatted_total)
                
            # Write to /data directory if it exists
            if os.path.exists("/data"):
                os.makedirs("/data", exist_ok=True)
                with open(output_file, 'w') as f:
                    f.write(formatted_total)
                    
            return f"Successfully calculated Gold ticket sales and wrote to {output_file}"
            
        finally:
            cursor.close()
            conn.close()
            
    except sqlite3.Error as e:
        raise ValueError(f"Database error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error in ticket sales calculation: {str(e)}")