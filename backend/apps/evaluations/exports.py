"""
PKL CMS — Evaluations Export Helpers
Fungsi untuk mengekspor data evaluasi ke Excel (.xlsx) dan PDF.
"""

import io
import zipfile
from datetime import datetime

from django.http import HttpResponse
from django.template.loader import render_to_string

import openpyxl
from openpyxl.styles import (
    Alignment, Border, Font, PatternFill, Side
)
from openpyxl.utils import get_column_letter


# ─────────────────────────────────────────────────────────────────
# HELPER: border & style shortcuts
# ─────────────────────────────────────────────────────────────────

def _thin_border():
    thin = Side(style="thin", color="B0B8C8")
    return Border(left=thin, right=thin, top=thin, bottom=thin)


def _header_fill():
    return PatternFill(fill_type="solid", fgColor="0F3460")


def _subheader_fill():
    return PatternFill(fill_type="solid", fgColor="E8F0FE")


# ─────────────────────────────────────────────────────────────────
# EXPORT EXCEL — rekap semua evaluasi
# ─────────────────────────────────────────────────────────────────

def export_evaluations_excel(queryset) -> HttpResponse:
    """
    Hasilkan file .xlsx berisi rekap semua evaluasi pada queryset.

    Kolom:
      No | Nama Intern | Departemen | Mentor | Periode | Status
      | Kriteria | Skor | Skor Maks | Bobot | Skor Akhir | Grade
      | Tanggal Dibuat
    """

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Rekap Evaluasi"

    # ── Judul workbook ──────────────────────────────────────────
    ws.merge_cells("A1:M1")
    title_cell = ws["A1"]
    title_cell.value = "REKAP EVALUASI MAHASISWA MAGANG — IMS PKL CMS"
    title_cell.font = Font(name="Arial", bold=True, size=13, color="FFFFFF")
    title_cell.fill = PatternFill(fill_type="solid", fgColor="0F3460")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    ws.merge_cells("A2:M2")
    gen_cell = ws["A2"]
    gen_cell.value = f"Digenerate pada: {datetime.now().strftime('%d %B %Y %H:%M')}"
    gen_cell.font = Font(name="Arial", italic=True, size=9, color="555555")
    gen_cell.alignment = Alignment(horizontal="right")
    ws.row_dimensions[2].height = 16

    # ── Header kolom ────────────────────────────────────────────
    headers = [
        "No", "Nama Intern", "Email", "Departemen", "Mentor",
        "Periode", "Status", "Kriteria", "Skor",
        "Skor Maks", "Bobot (%)", "Skor Akhir", "Grade",
        "Tanggal Dibuat",
    ]

    col_widths = [5, 28, 28, 22, 24, 20, 14, 30, 10, 12, 12, 12, 8, 18]

    header_row = 3
    for col_idx, (header, width) in enumerate(zip(headers, col_widths), start=1):
        cell = ws.cell(row=header_row, column=col_idx, value=header)
        cell.font = Font(name="Arial", bold=True, size=9, color="FFFFFF")
        cell.fill = _header_fill()
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = _thin_border()
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    ws.row_dimensions[header_row].height = 24
    ws.freeze_panes = "A4"  # freeze judul + header

    # ── Data rows ────────────────────────────────────────────────
    row = header_row + 1
    no = 1

    # Prefetch untuk performa
    qs = queryset.select_related(
        "intern", "intern__department", "mentor"
    ).prefetch_related("scores__criteria")

    for evaluation in qs:
        scores = list(evaluation.scores.select_related("criteria").all())

        # Kalau belum ada skor, tetap tampilkan satu baris kosong
        rows_to_fill = scores if scores else [None]

        first_row_of_eval = row

        for score in rows_to_fill:
            fill = PatternFill(fill_type="solid", fgColor="F4F7FB") if (no % 2 == 0) else None
            border = _thin_border()

            def _cell(col, value, bold=False, center=False, num_format=None):
                c = ws.cell(row=row, column=col, value=value)
                c.font = Font(name="Arial", size=9, bold=bold)
                c.border = border
                c.alignment = Alignment(
                    horizontal="center" if center else "left",
                    vertical="center",
                    wrap_text=True
                )
                if fill:
                    c.fill = fill
                if num_format:
                    c.number_format = num_format
                return c

            dept = getattr(evaluation.intern.department, "name", "—") if evaluation.intern.department else "—"

            _cell(1, no, center=True)
            _cell(2, evaluation.intern.full_name, bold=True)
            _cell(3, evaluation.intern.email)
            _cell(4, dept)
            _cell(5, evaluation.mentor.full_name)
            _cell(6, evaluation.period_label, center=True)
            _cell(7, evaluation.get_status_display(), center=True)

            if score:
                _cell(8, score.criteria.name)
                _cell(9, float(score.raw_score), center=True, num_format="0.00")
                _cell(10, score.criteria.max_score, center=True)
                bobot_pct = float(score.criteria.weight) * 100
                _cell(11, bobot_pct, center=True, num_format="0.00")
            else:
                _cell(8, "—", center=True)
                _cell(9, "—", center=True)
                _cell(10, "—", center=True)
                _cell(11, "—", center=True)

            _cell(12, float(evaluation.final_score) if evaluation.final_score else "—", center=True, num_format="0.00")
            _cell(13, evaluation.grade or "—", center=True, bold=True)
            _cell(14, evaluation.created_at.strftime("%d/%m/%Y") if evaluation.created_at else "—", center=True)

            ws.row_dimensions[row].height = 18
            row += 1

        # Merge kolom identitas untuk evaluasi yang punya banyak skor
        if len(rows_to_fill) > 1:
            last_row_of_eval = row - 1
            for col in [1, 2, 3, 4, 5, 6, 7, 12, 13, 14]:
                ws.merge_cells(
                    start_row=first_row_of_eval,
                    start_column=col,
                    end_row=last_row_of_eval,
                    end_column=col,
                )
                merged_cell = ws.cell(row=first_row_of_eval, column=col)
                merged_cell.alignment = Alignment(
                    horizontal="center" if col in [1, 7, 12, 13, 14] else "left",
                    vertical="center",
                    wrap_text=True
                )

        no += 1

    # ── Auto-filter ──────────────────────────────────────────────
    ws.auto_filter.ref = f"A{header_row}:{get_column_letter(len(headers))}{row - 1}"

    # ── Output HTTP response ─────────────────────────────────────
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"rekap_evaluasi_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


# ─────────────────────────────────────────────────────────────────
# EXPORT PDF — laporan individual per-evaluasi
# ─────────────────────────────────────────────────────────────────

def _render_evaluation_pdf_bytes(evaluation) -> bytes:
    """
    Render satu Evaluation menjadi bytes PDF menggunakan WeasyPrint.
    """
    from weasyprint import HTML as WeasyHTML, CSS

    scores = evaluation.scores.select_related("criteria").order_by(
        "criteria__category", "criteria__name"
    )

    # Coba ambil InternProfile jika ada
    try:
        intern_profile = evaluation.intern.intern_profile
    except Exception:
        intern_profile = None

    approved_by_name = (
        evaluation.approved_by.full_name if evaluation.approved_by else None
    )

    context = {
        "evaluation": evaluation,
        "scores": scores,
        "intern_profile": intern_profile,
        "approved_by_name": approved_by_name,
        "generated_at": datetime.now().strftime("%d %B %Y, %H:%M"),
    }

    html_string = render_to_string("evaluations/report_pdf.html", context)

    # Bobot font WeasyPrint (persentase disimpan sebagai Decimal, ubah dulu)
    pdf_bytes = WeasyHTML(string=html_string).write_pdf()
    return pdf_bytes


def export_evaluation_pdf_single(evaluation) -> HttpResponse:
    """
    Kembalikan HttpResponse berisi satu file PDF untuk satu evaluasi.
    """
    pdf_bytes = _render_evaluation_pdf_bytes(evaluation)

    intern_name = evaluation.intern.full_name.replace(" ", "_")
    period = evaluation.period_label.replace(" ", "_")
    filename = f"evaluasi_{intern_name}_{period}.pdf"

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def export_evaluation_pdf_zip(queryset) -> HttpResponse:
    """
    Kembalikan HttpResponse berisi ZIP berisi banyak PDF (satu per evaluasi).
    """
    qs = queryset.select_related(
        "intern", "intern__department", "mentor", "approved_by"
    ).prefetch_related("scores__criteria")

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for evaluation in qs:
            pdf_bytes = _render_evaluation_pdf_bytes(evaluation)
            intern_name = evaluation.intern.full_name.replace(" ", "_")
            period = evaluation.period_label.replace(" ", "_")
            pdf_filename = f"evaluasi_{intern_name}_{period}.pdf"
            zf.writestr(pdf_filename, pdf_bytes)

    zip_buffer.seek(0)
    filename = f"laporan_evaluasi_{datetime.now().strftime('%Y%m%d_%H%M')}.zip"
    response = HttpResponse(zip_buffer.read(), content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
