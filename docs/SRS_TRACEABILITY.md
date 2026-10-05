# SRS Traceability

This document maps the supplied SRS to the implementation.

## Tool 1

| SRS | Implementation |
|---|---|
| JPG/PNG/PDF input | `/api/ocr/process` |
| Handwritten + printed | Tesseract baseline; production model comparison is still recommended |
| Multi-page | PyMuPDF renders every PDF page |
| Cleanup/orientation | EXIF transpose, grayscale, autocontrast, upscale |
| Side-by-side / compare | Browser UI keeps extracted text editable; source upload is stored privately. A production viewer can be added for exact image overlay |
| Manual correction | Editable textarea + save endpoint |
| TXT/DOCX/CSV | Export endpoints |
| Confidence | Average OCR confidence shown; raw per-word confidence is available inside OCR service for extension |
| History | User-scoped OCR history |
| Cursive/print + regional languages | Language parameter + Tesseract language packs; validation against target language dataset is required |
| 85–90% target | Acceptance testing must be done on representative clear handwriting; not claimed automatically |
| <10 sec/page | Requires benchmarking on deployment hardware |
| Secure storage | User-specific storage directory and ownership checks; production encryption/object storage recommended |
| Scalability | Stateless API design; background queue/object storage recommended for production |

## Tool 2

FR1–FR4: Case-law create, attachments, tags, version snapshots.
FR5–FR8: ClientCase entity, dates, exposure, precedent mapping.
FR9–FR11: Multi-filter search, sorting, pagination. Full PDF text search is deliberately a later-phase item.
FR12–FR13: Practice Notes and Templates.
FR14–FR16: Tasks, reminders, calendar ICS.
FR17–FR18: CSV reports and dashboard metrics.
FR19–FR21: RBAC, user roles, audit log. Sensitive per-case visibility groups are represented as a production-hardening extension rather than falsely claimed complete.
FR22–FR23: CSV import and CSV export; PDF reporting can be added through a PDF renderer.

## Requirements intentionally left configurable

The SRS uses `[X]`, `[Y]`, `[Z]` for concurrency/search targets. No values were supplied, so this project does not invent them.

The SRS recommends datasets for Tool 1 but does not provide their contents. No copyrighted or external dataset is bundled.

The SRS allows cloud AI/vision models but does not require a particular provider. The baseline implementation uses local Tesseract to keep the project runnable without an external API key.

## Production extensions
- PostgreSQL
- Redis/Celery or a job queue
- object storage
- email SMTP provider
- full-text search index
- OCR overlay coordinates
- PDF report generation
- granular case visibility groups
- MFA/SSO
- antivirus scanning
- encryption/key management
- monitoring and backups
