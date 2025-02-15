import os
import json
import requests
import sqlite3
from pathlib import Path
import subprocess
from PIL import Image
import git

class BusinessTasks:
    def __init__(self):
        self.data_dir = "/data"

    async def execute(self, task_type: str, task_description: str):
        task_map = {
            'B3': self._task_b3,
            'B4': self._task_b4,
            'B5': self._task_b5,
            'B6': self._task_b6,
            'B7': self._task_b7,
            'B8': self._task_b8,
            'B9': self._task_b9,
            'B10': self._task_b10
        }
        
        if task_type not in task_map:
            raise ValueError(f"Unknown task type: {task_type}")
            
        return await task_map[task_type](task_description)

    async def _task_b3(self, description):
        """Fetch data from an API and save it"""
        # Extract API URL from task description using LLM
        api_url = "https://api.example.com/data"  # This should come from LLM
        output_file = f"{self.data_dir}/api_data.json"
        
        response = requests.get(api_url)
        response.raise_for_status()
        
        with open(output_file, 'w') as f:
            json.dump(response.json(), f, indent=2)
        return "API data saved"

    async def _task_b4(self, description):
        """Clone a git repo and make a commit"""
        repo_path = f"{self.data_dir}/repo"
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)
            
        # Initialize repo if it doesn't exist
        if not os.path.exists(f"{repo_path}/.git"):
            repo = git.Repo.init(repo_path)
        else:
            repo = git.Repo(repo_path)
            
        # Make changes (example)
        with open(f"{repo_path}/example.txt", 'w') as f:
            f.write("Example content")
            
        repo.index.add(['example.txt'])
        repo.index.commit("Add example file")
        return "Git operations completed"

    async def _task_b5(self, description):
        """Run a SQL query on SQLite/DuckDB database"""
        db_file = f"{self.data_dir}/database.db"
        output_file = f"{self.data_dir}/query_result.json"
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Query should come from LLM analysis of task description
        query = "SELECT * FROM example_table"
        cursor.execute(query)
        
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        data = [dict(zip(columns, row)) for row in results]
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        conn.close()
        return "Query executed and results saved"

    async def _task_b6(self, description):
        """Extract data from a website"""
        # URL should come from LLM analysis
        url = "https://example.com"
        output_file = f"{self.data_dir}/scraped_data.json"
        
        response = requests.get(url)
        response.raise_for_status()
        
        # Extract data (example)
        data = {"title": "Example", "content": "Sample content"}
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        return "Website data extracted"

    async def _task_b7(self, description):
        """Compress or resize an image"""
        input_file = f"{self.data_dir}/input.jpg"
        output_file = f"{self.data_dir}/output.jpg"
        
        with Image.open(input_file) as img:
            # Resize to 50% of original size
            new_size = tuple(d // 2 for d in img.size)
            resized = img.resize(new_size, Image.LANCZOS)
            resized.save(output_file, quality=85, optimize=True)
        return "Image processed"

    async def _task_b8(self, description):
        """Transcribe audio from MP3"""
        input_file = f"{self.data_dir}/audio.mp3"
        output_file = f"{self.data_dir}/transcript.txt"
        
        # This would typically use a transcription service
        # For now, we'll just create a placeholder
        with open(output_file, 'w') as f:
            f.write("Audio transcription placeholder")
        return "Audio transcribed"

    async def _task_b9(self, description):
        """Convert Markdown to HTML"""
        input_file = f"{self.data_dir}/input.md"
        output_file = f"{self.data_dir}/output.html"
        
        subprocess.run([
            'npx',
            'marked',
            input_file,
            '-o',
            output_file
        ], check=True)
        return "Markdown converted to HTML"

    async def _task_b10(self, description):
        """Filter CSV and return JSON"""
        input_file = f"{self.data_dir}/input.csv"
        output_file = f"{self.data_dir}/filtered.json"
        
        # Read CSV and filter (example)
        import pandas as pd
        df = pd.read_csv(input_file)
        
        # Filter criteria should come from LLM analysis
        filtered = df[df['column'] > 0]  # Example filter
        
        filtered.to_json(output_file, orient='records', indent=2)
        return "CSV filtered and converted to JSON"

    async def _call_llm(self, system_prompt, user_content):
        # This should be implemented similar to TaskAgent._call_llm
        pass