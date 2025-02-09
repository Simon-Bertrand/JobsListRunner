from datetime import datetime
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, ValidationError, field_serializer


class JobListItem(BaseModel):
    date: Optional[datetime] = None
    script: Path

    @field_serializer("script")
    def serialize_path(self, value: Path) -> str:
        return value.absolute().as_posix()

    def __pydantic_post_init__(self):
        if not self.script.exists():
            raise ValidationError(f"Script {self.script} does not exist")
        if self.data is not None:
            if self.data > datetime.now():
                raise ValidationError(f"Date {self.data} is in the future")
