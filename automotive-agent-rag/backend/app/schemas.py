from typing import List, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    provider: str = "groq"
    model: Optional[str] = None
    brand: str = "Volkswagen"
    vehicle_model: str = "Taos"
    year: str = "2023"


class EvidenceItem(BaseModel):
    content: str
    page: Optional[int] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[str] = None
    manual_id: Optional[str] = None
    source_filename: Optional[str] = None
    relevance: Optional[float] = None


class ChatResponse(BaseModel):
    answer: str
    evidence: List[EvidenceItem] = []


class ManualOut(BaseModel):
    id: str
    brand: str
    model: str
    year: str
    filename: str
    source: str
    num_pages: int
    num_chunks: int
    uploaded_at: str
    preload_key: Optional[str] = None


class UploadResponse(BaseModel):
    manual: ManualOut
    num_chunks: int


class PreloadedManualStatus(BaseModel):
    key: str
    label: str
    brand: str
    model: str
    year: str
    loaded: bool


class ProviderModelInfo(BaseModel):
    label: str
    models: List[str]
    default_model: str
    available: bool


class HealthResponse(BaseModel):
    status: str
    storage_backend: str
    manuals_indexed: int


class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    created_at: str


class AuthResponse(BaseModel):
    token: str
    user: UserOut
