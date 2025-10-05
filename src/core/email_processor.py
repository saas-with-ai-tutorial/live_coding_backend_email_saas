from litellm import completion
from pydantic import BaseModel
from typing import Optional

class ActionItem(BaseModel):
    is_action_item: bool
    action_item: Optional[str] = None
    due_date: Optional[str] = None

system_prompt = """
You are a helpful assistant that can process emails and create action items.
You will be given an email and you will need to create an action item based on the email.

if the email does not have an action item, you should return the following:
{
    "is_action_item": False,
    "action_item": None,
    "due_date": None
}
"""

example_email = """
Subject: Meeting with the team
From: John Doe <john.doe@example.com>
To: Jane Doe <jane.doe@example.com>
Date: 2021-01-01
Body: We need to discuss the project and the team.
"""


messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": example_email}
]

response = completion(
    model="openai/gpt-4o-mini",
    messages=messages,
    response_format=ActionItem
)

print(response.choices[0].message.content)