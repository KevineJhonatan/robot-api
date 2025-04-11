"""Steps du pipeline."""

from src.modules.pipeline.steps.company.processing import process_companies_and_collect_data, prepare_excel_and_upload_to_snaplogic
from src.modules.pipeline.steps.company.collection import fetch_company_list
from src.modules.pipeline.steps.company.avp.collection import collect_company_avps
from src.modules.pipeline.steps.company.pdf.collection import collect_company_pdfs
from src.modules.pipeline.steps.company.alt.collection import collect_company_alternants
from src.modules.pipeline.steps.snaplogic import send_to_snaplogic, prepare_metadata

__all__ = [
    'process_companies_and_collect_data',
    'prepare_excel_and_upload_to_snaplogic',
    'fetch_company_list',
    'collect_company_avps',
    'collect_company_pdfs',
    'collect_company_alternants',
    'send_to_snaplogic',
    'prepare_metadata'
]
