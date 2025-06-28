from pydantic import BaseModel
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    status: str
    message: str
    data: Optional[T] = None
