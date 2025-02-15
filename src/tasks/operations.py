import os
import json
import subprocess
import sqlite3
from datetime import datetime
import glob
from pathlib import Path
import requests
from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class OperationsTasks:
    def __init__(self):
        self.data_dir = "/data"

    async def execute(self, task_type: str, task_description: str):
        task_map = {
            'A1': self._task_a1,
            'A2': self._task_a2,
            'A3': self._task_a3,
            'A4': self._task_a4,
            'A5': self._task_a5,
            'A6': self._task_a6,
            'A7': self._task_a7,
            'A8': self._task_a8,
            'A9': self._task_a9,
            'A10': self._task_a10
        }
        
        if task_type not in task_map:
            raise ValueError(f"Unknown task type: {task_type}")
            
        return await task_map[task_type](task_description)

    async def _task_a1(self, description):
        # Install uv if not present
        try:
            subprocess.run(['uv', '--version'], check=True)
        except:
            subprocess.run(['pip', 'install', 'uv'], check=True)
        
        # Download and run datagen.py
        url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
        email = os.environ.get("USER_EMAIL", "default@example.com")
        
        response = requests.get(url)
        with open("datagen.py", "w") as f:
            f.write(response.text)
            
        subprocess.run(['python', 'datagen.py', email], check=True)
        return "Data generation complete"

    async def _task_a2(self, description):
        input_file = f"{self.data_dir}/format.md"
        subprocess.run(['npx', 'prettier@3.4.2', '--write', input_file], check=True)
        return "File formatted"

    async def _task_a3(self, description):
        dates_file = f"{self.data_dir}/dates.txt"
        output_file = f"{self.data_dir}/dates-wednesdays.txt"
        
        wednesday_count = 0
        with open(dates_file, 'r') as f:
            for line in f:
                date = datetime.strptime(line.strip(), '%Y-%m-%d')
                if date.weekday() == 2:  # Wednesday is 2
                    wednesday_count += 1
                    
        with open(output_file, 'w') as f:
            f.write(str(wednesday_count))
        return f"Found {wednesday_count} Wednesdays"

    async def _task_a4(self, description):
        input_file = f"{self.data_dir}/contacts.json"
        output_file = f"{self.data_dir}/contacts-sorted.json"
        
        with open(input_file, 'r') as f:
            contacts = json.load(f)
            
        sorted_contacts = sorted(
            contacts,
            key=lambda x: (x['last_name'], x['first_name'])
        )
        
        with open(output_file, 'w') as f:
            json.dump(sorted_contacts, f, indent=2)
        return "Contacts sorted"

    async def _task_a5(self, description):
        log_dir = f"{self.data_dir}/logs"
        output_file = f"{self.data_dir}/logs-recent.txt"
        
        log_files = glob.glob(f"{log_dir}/*.log")
        log_files.sort(key=os.path.getmtime, reverse=True)
        recent_logs = log_files[:10]
        
        with open(output_file, 'w') as out:
            for log_file in recent_logs:
                with open(log_file, 'r') as f:
                    first_line = f.readline().strip()
                    out.write(first_line + '\n')
        return "Recent logs extracted"

    async def _task_a6(self, description):
        docs_dir = f"{self.data_dir}/docs"
        output_file = f"{self.data_dir}/docs/index.json"
        
        index = {}
        for md_file in Path(docs_dir).glob('**/*.md'):
            relative_path = str(md_file.relative_to(docs_dir))
            with open(md_file, 'r') as f:
                for line in f:
                    if line.startswith('# '):
                        index[relative_path] = line[2:].strip()
                        break
                        
        with open(output_file, 'w') as f:
            json.dump(index, f, indent=2)
        return "Index created"

    async def _task_a7(self, description):
        email_file = f"{self.data_dir}/email.txt"
        output_file = f"{self.data_dir}/email-sender.txt"
        
        with open(email_file, 'r') as f:
            content = f.read()
            
        system_prompt = "Extract the sender's email address from this email message. Respond with just the email address."
        email_address = await self._call_llm(system_prompt, content)
        
        with open(output_file, 'w') as f:
            f.write(email_address.strip())
        return "Email extracted"

    async def _task_a8(self, description):
        image_file = f"{self.data_dir}/credit-card.png"
        output_file = f"{self.data_dir}/credit-card.txt"
        
        # Convert image to base64 for LLM
        with open(image_file, 'rb') as f:
            image_bytes = f.read()
            
        system_prompt = "Extract the credit card number from this image. Respond with just the number, no spaces."
        card_number = await self._call_llm(system_prompt, image_bytes)
        
        with open(output_file, 'w') as f:
            f.write(card_number.strip())
        return "Card number extracted"

    async def _task_a9(self, description):
        comments_file = f"{self.data_dir}/comments.txt"
        output_file = f"{self.data_dir}/comments-similar.txt"
        
        with open(comments_file, 'r') as f:
            comments = [line.strip() for line in f]
            
        # Get embeddings using the LLM
        embeddings = []
        for comment in comments:
            system_prompt = "Generate a numerical embedding for this text. Return as JSON array."
            embedding = json.loads(await self._call_llm(system_prompt, comment))
            embeddings.append(embedding)
            
        # Find most similar pair
        similarities = cosine_similarity(embeddings)
        np.fill_diagonal(similarities, -1)
        i, j = np.unravel_index(similarities.argmax(), similarities.shape)
        
        with open(output_file, 'w') as f:
            f.write(f"{comments[i]}\n{comments[j]}")
        return "Similar comments found"

    async def _task_a10(self, description):
        db_file = f"{self.data_dir}/ticket-sales.db"
        output_file = f"{self.data_dir}/ticket-sales-gold.txt"
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT SUM(units * price)
            FROM tickets
            WHERE type = 'Gold'
        """)
        
        total_sales = cursor.fetchone()[0]
        conn.close()
        
        with open(output_file, 'w') as f:
            f.write(str(total_sales))
        return f"Total Gold ticket sales: {total_sales}"

    async def _call_llm(self, system_prompt, user_content):
        # This should be implemented similar to TaskAgent._call_llm
        pass