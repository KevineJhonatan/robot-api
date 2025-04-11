"""
Constantes AWS.
"""

# Types d'opérations
OPERATION_TYPES = {
    "PIPELINE_START": "pipeline_start",
    "SCRAPING_START": "scraping_start",
    "COMPANY_LIST": "company_list",
    "AVP_FETCH": "avp_fetch",
    "AVP_DOWNLOAD": "avp_download",
    "ALT_FETCH": "alt_fetch",
    "ALT_DOWNLOAD": "alt_download",
    "PDF_DOWNLOAD": "pdf_download",
    "EXCEL_CREATE": "excel_create",
    "SNAPLOGIC_SEND": "snaplogic_send",
    "DOWNLOAD": "download",
    "UPLOAD": "upload",
    "PROCESS": "process",
    "VALIDATE": "validate",
    "TRANSFORM": "transform",
    "CLEAN": "clean",
    "PIPELINE_SUCCESS": "pipeline_success",
    "PIPELINE_ERROR": "pipeline_error",
    "COMPANIES_DONE": "companies_done",
    "COMPANY_ERROR": "company_error",
    "SNAPLOGIC_UPLOAD": "snaplogic_upload",
}

# Statuts des opérations
STATUS = {
    "RUNNING": "running",
    "SUCCESS": "success",
    "ERROR": "error",
    "PENDING": "pending",
    "SKIPPED": "skipped",
    "COMPLETED": "completed",
    "FAILED": "failed",
}
