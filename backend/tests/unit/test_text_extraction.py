import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.services.text_extraction_service import extract_text, TextExtractionError, _extract_pdf_text, _transcribe_media

@patch("fitz.open")
def test_extract_pdf_text_success(mock_fitz_open, tmp_path):
    mock_doc = MagicMock()
    mock_page1 = MagicMock()
    mock_page1.get_text.return_value = "Page 1 text"
    mock_page2 = MagicMock()
    mock_page2.get_text.return_value = "Page 2 text"
    mock_doc.__iter__.return_value = [mock_page1, mock_page2]
    mock_doc.__enter__.return_value = mock_doc
    mock_fitz_open.return_value = mock_doc

    pdf_path = tmp_path / "test.pdf"
    pdf_path.touch()

    text = _extract_pdf_text(pdf_path)
    assert text == "Page 1 text\n\nPage 2 text"

@patch("app.services.text_extraction_service._get_whisper_model")
def test_transcribe_media_success(mock_get_model, tmp_path):
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {
        "text": "Hello world",
        "segments": [{"text": "Hello", "start": 0.0, "end": 1.0}, {"text": "world", "start": 1.0, "end": 2.0}]
    }
    mock_get_model.return_value = mock_model

    media_path = tmp_path / "test.mp3"
    media_path.touch()

    text, segments = _transcribe_media(media_path)
    assert text == "Hello world"
    assert len(segments) == 2
    assert segments[0]["start"] == 0.0

@patch("app.services.text_extraction_service._extract_pdf_text")
def test_extract_text_pdf(mock_extract_pdf, tmp_path):
    mock_extract_pdf.return_value = "PDF content"
    pdf_path = tmp_path / "test.pdf"
    
    result = extract_text(pdf_path)
    assert result.text == "PDF content"
    assert result.segments is None

@patch("app.services.text_extraction_service._transcribe_media")
def test_extract_text_audio(mock_transcribe, tmp_path):
    mock_transcribe.return_value = ("Audio content", [{"text": "Audio content", "start": 0.0, "end": 2.0}])
    audio_path = tmp_path / "test.mp3"
    
    result = extract_text(audio_path)
    assert result.text == "Audio content"
    assert result.segments is not None
    assert result.segments[0]["start"] == 0.0

def test_extract_text_unsupported(tmp_path):
    txt_path = tmp_path / "test.txt"
    with pytest.raises(TextExtractionError):
        extract_text(txt_path)
