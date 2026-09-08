from __future__ import annotations

import os
import re
import uuid

from flask import current_app
from werkzeug.utils import secure_filename


ALLOWED_RESUME_EXTENSIONS = {'pdf', 'docx', 'txt'}
MAX_RESUME_BYTES = 10 * 1024 * 1024


def validate_file_signature(path, extension):
    with open(path, 'rb') as file:
        header = file.read(8)
    if extension == 'pdf' and not header.startswith(b'%PDF-'):
        raise ValueError('The uploaded file is not a valid PDF.')
    if extension == 'docx' and not header.startswith(b'PK'):
        raise ValueError('The uploaded file is not a valid DOCX file.')


def extract_resume_text(path, extension):
    if extension == 'pdf':
        try:
            import fitz
        except ImportError as exc:
            raise ValueError('PDF processing requires PyMuPDF. Install the project requirements first.') from exc
        with fitz.open(path) as document:
            return '\n'.join(page.get_text() for page in document)
    if extension == 'docx':
        try:
            from docx import Document
        except ImportError as exc:
            raise ValueError('DOCX processing requires python-docx. Install the project requirements first.') from exc
        return '\n'.join(paragraph.text for paragraph in Document(path).paragraphs)
    with open(path, 'r', encoding='utf-8', errors='replace') as file:
        return file.read()


def save_resume_upload(upload):
    original = secure_filename(upload.filename or '')
    extension = original.rsplit('.', 1)[-1].lower() if '.' in original else ''
    if not original or extension not in ALLOWED_RESUME_EXTENSIONS:
        raise ValueError('Upload a PDF, DOCX, or TXT resume.')
    upload.stream.seek(0, os.SEEK_END)
    size = upload.stream.tell()
    upload.stream.seek(0)
    if size == 0:
        raise ValueError('The uploaded resume is empty.')
    if size > MAX_RESUME_BYTES:
        raise ValueError('Resumes must be 10 MB or smaller.')

    folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resumes')
    os.makedirs(folder, exist_ok=True)
    stored = f'{uuid.uuid4().hex}.{extension}'
    path = os.path.join(folder, stored)
    upload.save(path)
    try:
        validate_file_signature(path, extension)
        text = re.sub(r'\s+', ' ', extract_resume_text(path, extension)).strip()
    except Exception as exc:
        if os.path.exists(path):
            os.remove(path)
        if isinstance(exc, ValueError):
            raise
        raise ValueError('The uploaded resume could not be read.') from exc
    if not text:
        os.remove(path)
        raise ValueError('No readable text was found in the uploaded resume.')
    return original, stored, os.path.relpath(path), extension, text