# TaxCase OCR & GST/Income Tax Case Library

A runnable reference implementation based on the supplied SRS:
- Tool 1: Common OCR Converter for handwritten/printed documents
- Tool 2: GST and Income Tax Case Library + internal litigation tracker

## What is implemented

### Tool 1 — OCR Converter
- JPG/PNG/PDF uploads
- Multi-page PDF handling
- Image deskew/orientation/contrast cleanup
- OCR using Tesseract when installed
- Optional EasyOCR backend when installed
- Per-line confidence estimates
- Side-by-side source image and editable extracted text
- TXT, DOCX and CSV export
- Processing history per user
- User-private document storage
- Basic language selection

### Tool 2 — Case Library
- JWT authentication and role-based access: ADMIN, SENIOR, JUNIOR, CLIENT
- Case-law repository with forum, sections, issues, assessment year, citation, outcome
- Multiple document attachments
- Tags
- Version history
- Internal client/litigation cases
- Important dates and limitation date
- Precedent mapping
- Advanced filtering + pagination + sorting
- Practice notes and templates
- Tasks, deadlines and hearing diary
- In-app reminders
- Dashboard metrics
- Audit log
- CSV bulk import
- CSV, XLSX and PDF report export
- Calendar/ICS export
- Responsive browser UI

## Important SRS notes
The SRS leaves `[X]`, `[Y]`, and `[Z]` unspecified for concurrency/search performance. This implementation does not invent those acceptance values. See `docs/SRS_TRACEABILITY.md` for the implemented interpretation and remaining production-hardening items.

The SRS also says external tax databases are manual import/link only in Phase 1; this project does not scrape or automatically integrate external legal databases.

## Stack
- Python 3.11+
- FastAPI
- SQLAlchemy
- SQLite by default; PostgreSQL-ready through `DATABASE_URL`
- Jinja2 + vanilla JavaScript/CSS
- Tesseract OCR optional
- OpenCV optional but recommended
- python-docx / pandas / openpyxl-compatible CSV workflow
- Docker + docker-compose

## Quick start

### 1. Create environment
```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
# .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Optional OCR system packages

Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y tesseract-ocr tesseract-ocr-eng
```

For additional regional languages, install the relevant Tesseract language packages and pass the language code supported by your installation.

### 3. Start
```bash
uvicorn app.main:app --reload
```

Open:
http://127.0.0.1:8000

Demo accounts:
- admin@example.com / Admin@123
- senior@example.com / Senior@123
- junior@example.com / Junior@123
- client@example.com / Client@123

Change these passwords before any real deployment.

### Docker
```bash
docker compose up --build
```

## Project layout
```text
app/
  main.py
  config.py
  database.py
  models.py
  schemas.py
  security.py
  services/
    ocr_service.py
    export_service.py
    reminder_service.py
    audit_service.py
  routers/
    auth.py
    ocr.py
    cases.py
    clients.py
    tasks.py
    notes.py
    dashboard.py
    reports.py
    admin.py
  templates/
  static/
tests/
docs/
scripts/
storage/
```

## Production hardening before real client data
1. Use PostgreSQL and object storage instead of local SQLite/files.
2. Put the app behind HTTPS and a reverse proxy.
3. Replace demo secrets and credentials.
4. Add malware scanning for uploads.
5. Encrypt object storage and backups.
6. Add an external job queue for OCR/reminders.
7. Configure SMTP for email reminders.
8. Add centralized logging/monitoring.
9. Configure retention and deletion policies with the firm's legal/compliance policy.
10. Validate OCR accuracy on the firm's real handwriting sample set; the SRS target is 85–90% on clear handwriting.
11. Load-test against the firm's actual concurrency/search targets once `[X]/[Y]/[Z]` are defined.
12. Review confidentiality, access-control, retention, and professional-conduct requirements with the responsible organization.

## License
Internal project/reference implementation. Add the organization's license and data-use policy before deployment.
