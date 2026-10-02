from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.sample_data import USE_CASE_SOURCES


class SourceResponse(BaseModel):
    source_id: str
    title: str


class UseCaseSourcesResponse(BaseModel):
    use_case_id: str
    sources: list[SourceResponse]


class UnknownUseCaseDetail(BaseModel):
    code: Literal["unknown_use_case"]


class UnknownUseCaseResponse(BaseModel):
    detail: UnknownUseCaseDetail


app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get(
    "/v1/use-cases/{use_case_id}/sources",
    response_model=UseCaseSourcesResponse,
    responses={404: {"model": UnknownUseCaseResponse}},
)
def get_sources(use_case_id: str) -> UseCaseSourcesResponse:
    if use_case_id not in USE_CASE_SOURCES:
        raise HTTPException(status_code=404, detail={"code": "unknown_use_case"})

    return UseCaseSourcesResponse(
        use_case_id=use_case_id,
        sources=[
            SourceResponse(**source) for source in USE_CASE_SOURCES[use_case_id]
        ],
    )
