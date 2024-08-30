from typing import Dict, List, Optional

from pydantic import AnyHttpUrl, BaseModel, Field
from typing_extensions import Literal


class Contact(BaseModel):
    name: Optional[str] = None
    url: Optional[AnyHttpUrl] = None
    email: Optional[str] = None

class License(BaseModel):
    name: str
    url: Optional[AnyHttpUrl] = None

class Info(BaseModel):
    title: str
    description: Optional[str] = None
    termsOfService: Optional[AnyHttpUrl] = None
    contact: Optional[Contact] = None
    license: Optional[License] = None
    version: str

class Server(BaseModel):
    url: AnyHttpUrl
    description: Optional[str] = None

class OpenAPISettings(BaseModel):
    openapi: Literal["3.0.0"] = "3.0.0"
    info: Info
    servers: Optional[List[Server]] = None
    paths: Dict[str, Dict] = Field(default_factory=dict)
    components: Optional[Dict] = None
    security: Optional[List[Dict[str, List[str]]]] = None
    tags: Optional[List[Dict[str, str]]] = None
    externalDocs: Optional[Dict[str, str]] = None
