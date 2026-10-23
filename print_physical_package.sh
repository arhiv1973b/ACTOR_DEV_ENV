#!/usr/bin/env bash
# ==============================================================================
# AUTOMATED PRINTING SCRIPT FOR PHYSICAL FILING PACKAGE
# CASE-MACHERET-1997-2026
# ==============================================================================
set -e

echo "[*] Initializing automated print queue for physical filing documents..."

PDF_FILES=(
    "PHYSICAL_FILING_PACKAGE_INSTRUCTIONS.pdf"
    "US_EMBASSY_DIPLOMATIC_MEMORANDUM_2026.pdf"
    "Delivery_Status_Report_CASE_MACHERET.pdf"
)

for pdf in "${PDF_FILES[@]}"; do
    if [ -f "$pdf" ]; then
        echo " [✓] Sending to printer: $pdf"
        # Use lp or lpr if available (Linux/WSL/CUPS)
        if command -v lp &> /dev/null; then
            lp "$pdf" || echo "[WARN] Printer command failed for $pdf"
        elif command -v lpr &> /dev/null; then
            lpr "$pdf" || echo "[WARN] Printer command failed for $pdf"
        else
            echo "[INFO] No default printer daemon (lp/lpr) found. PDF generated successfully for manual print."
        fi
    else
        echo " [!] File not found: $pdf"
    fi
done

echo "[SUCCESS] Physical filing print queue execution completed."
