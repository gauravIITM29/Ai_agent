import os
import requests
import json
from .tasks.operations import OperationsTasks
from .tasks.business import BusinessTasks

class TaskAgent:
    def __init__(self):
        self.api_key = os.environ.get("AIPROXY_TOKEN")
        self.base_url = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
        self.operations = OperationsTasks()
        self.business = BusinessTasks()

    async def _call_llm(self, system_prompt, user_prompt):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": messages
        }
        
        response = requests.post(
            url=self.base_url,
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"LLM API error: {response.text}")
            
        result = response.json()
        return result["choices"][0]["message"]["content"]

    async def execute_task(self, task_description: str):
        # First, use LLM to classify the task
        system_prompt = """
        You are a task classifier. Given a task description, identify which category it belongs to:
        - A1: Install and run datagen.py
        - A2: Format markdown with prettier
        - A3: Count weekdays in dates file
        - A4: Sort contacts JSON
        - A5: Get recent log lines
        - A6: Create markdown index
        - A7: Extract email sender
        - A8: Extract credit card number
        - A9: Find similar comments
        - A10: Calculate ticket sales
        - B3-B10: Various business tasks
        
        Respond with just the category identifier (e.g., "A1", "A7", etc.)
        """
        
        task_type = await self._call_llm(system_prompt, task_description)
        task_type = task_type.strip()
        
        if task_type.startswith('A'):
            return await self.operations.execute(task_type, task_description)
        elif task_type.startswith('B'):
            return await self.business.execute(task_type, task_description)
        else:
            raise ValueError(f"Unknown task type: {task_type}")