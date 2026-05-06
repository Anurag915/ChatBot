from fastapi import APIRouter, Depends, HTTPException, status
from starlette.concurrency import run_in_threadpool

from app.models.chat import ChatRequest, ChatResponse, SummarizeRequest, SummarizeResponse
from app.routes.auth import get_current_user
from app.services.chat_service import ChatProcessingError, generate_answer, generate_summary


router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
) -> ChatResponse:
    """Generate an answer based on document context using RAG."""
    
    try:
        result = await run_in_threadpool(
            generate_answer, 
            request.query, 
            request.file_id
        )
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            timestamps=result.get("timestamps", [])
        )
    except ChatProcessingError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during chat processing.",
        ) from exc


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_endpoint(
    request: SummarizeRequest,
    current_user: dict = Depends(get_current_user),
) -> SummarizeResponse:
    """Generate a summary of an uploaded document using its extracted text."""
    
    try:
        summary = await generate_summary(request.file_id)
        return SummarizeResponse(summary=summary)
    except ChatProcessingError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during summarization.",
        ) from exc
