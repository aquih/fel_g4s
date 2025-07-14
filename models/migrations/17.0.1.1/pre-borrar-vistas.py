import logging
from odoo.upgrade import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    util.records.remove_view(cr, xml_id="fel_g4s.invoice_form_fel_g4s")
    util.records.remove_view(cr, xml_id="fel_g4s.journal_form_fel_g4s")
    util.records.remove_view(cr, xml_id="fel_g4s.view_company_form_fel_g4s")
    _logger.info("Vistas viejas borradas")
