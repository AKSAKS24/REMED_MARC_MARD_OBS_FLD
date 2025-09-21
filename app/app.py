from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import re

app = FastAPI()


class Payload(BaseModel):
    pgm_name: str
    inc_name: str
    type: str
    name: Optional[str] = ""
    class_implementation: Optional[str] = ""
    code: str


class ResponseModel(BaseModel):
    pgm_name: str
    inc_name: str
    type: str
    name: Optional[str] = ""
    class_implementation: Optional[str] = ""
    original_code: str
    remediated_code: str


def process_abap_code(payload: Payload):
    code = payload.code
    original_code = code
    today_str = datetime.now().strftime("%Y-%m-%d")

    # List of obsolete fields
    obsolete_fields = [
        "MEGRU", "USEQU", "ALTSL", "MDACH",
        "DPLFS", "DPLPU", "DPLHO", "FHORI",
        "DISKZ", "LSOBS", "LMINB", "LBSTF"
    ]

    remediated_code = code

    for field in obsolete_fields:
        pattern = re.compile(rf"\b{field}\b", re.IGNORECASE)
        remediated_code = pattern.sub(
            f" \"Obsolete field {field.upper()} as per SAP Note 2267246 - Added By Pwc {today_str}",
            remediated_code
        )

    return ResponseModel(
        pgm_name=payload.pgm_name,
        inc_name=payload.inc_name,
        type=payload.type,
        name=payload.name,
        class_implementation=payload.class_implementation,
        original_code=original_code,
        remediated_code=remediated_code,
    )


@app.post('/remediate_abap', response_model=ResponseModel)
async def remediate_abap(payload: Payload):
    return process_abap_code(payload)
