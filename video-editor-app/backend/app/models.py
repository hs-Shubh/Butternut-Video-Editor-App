from typing import Literal, Optional
from pydantic import BaseModel, Field


class Position(BaseModel):
    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)


class Resolution(BaseModel):
    width: int = Field(ge=16)
    height: int = Field(ge=16)


class Overlay(BaseModel):
    id: str
    type: Literal["text", "image", "video"]
    content: str
    position: Position
    scale: float = Field(ge=0.1, le=10.0, default=1.0)
    rotation: float = Field(ge=-360.0, le=360.0, default=0.0)
    opacity: float = Field(ge=0.0, le=1.0, default=1.0)
    start_time: float = Field(ge=0.0)
    end_time: float = Field(ge=0.0)
    z_index: int = 0
    font_size: Optional[int] = Field(default=36, ge=8, le=256)
    background_box: Optional[bool] = False


class Metadata(BaseModel):
    title: str
    overlays: list[Overlay]
    output_format: Literal["mp4"] = "mp4"
    resolution: Resolution = Resolution(width=1280, height=720)
