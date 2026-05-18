from pydantic import BaseModel


class PhishingRequest(BaseModel):
    text: str