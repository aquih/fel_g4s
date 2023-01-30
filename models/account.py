# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

import odoo.addons.l10n_gt_extra.a_letras

from datetime import datetime
from lxml import etree
import base64
import logging
import zeep

import logging.config

class AccountMove(models.Model):
    _inherit = "account.move"

    pdf_fel = fields.Binary('PDF FEL', copy=False)
    pdf_fel_name = fields.Char('Nombre PDF FEL', default='pdf_fel.pdf')

    pdf_fel = fields.Char('PDF FEL', copy=False)
    
    def _post(self, soft=True):
        if self.certificar():
            return super(AccountMove, self)._post(soft)

    def post(self):
        if self.certificar():
            return super(AccountMove, self).post()
    
    def certificar(self):
        for factura in self:
            if factura.requiere_certificacion('g4s'):
                self.ensure_one()

                if factura.error_pre_validacion():
                    return False
                
                dte = factura.dte_documento()
                xmls = etree.tostring(dte, xml_declaration=True, encoding="UTF-8")
                logging.warning(xmls.decode("utf-8"))
                xmls_base64 = base64.b64encode(xmls)
                wsdl = 'https://fel.g4sdocumenta.com/webservicefront/factwsfront.asmx?wsdl'
                if factura.company_id.pruebas_fel:
                    wsdl = 'https://pruebasfel.g4sdocumenta.com/webservicefront/factwsfront.asmx?wsdl'
                client = zeep.Client(wsdl=wsdl)

                resultado = client.service.RequestTransaction(factura.company_id.requestor_fel, "SYSTEM_REQUEST", "GT", factura.company_id.vat, factura.company_id.requestor_fel, factura.company_id.usuario_fel, "POST_DOCUMENT_SAT", xmls_base64, factura.journal_id.code+str(factura.id))
                logging.warning(str(resultado))

                if resultado['Response']['Result']:
                    xml_resultado = base64.b64decode(resultado['ResponseData']['ResponseData1'])
                    logging.warning(xml_resultado)
                    dte_resultado = etree.XML(xml_resultado)

                    numero_autorizacion =  dte_resultado.xpath("//*[local-name() = 'NumeroAutorizacion']")[0]

                    factura.firma_fel = numero_autorizacion.text
                    factura.serie_fel = numero_autorizacion.get("Serie")
                    factura.numero_fel = numero_autorizacion.get("Numero")
                    factura.documento_xml_fel = xmls_base64
                    factura.resultado_xml_fel = xml_resultado
                    factura.certificador_fel = 'g4s' 

                    resultado = client.service.RequestTransaction(factura.company_id.requestor_fel, "GET_DOCUMENT", "GT", factura.company_id.vat, factura.company_id.requestor_fel, factura.company_id.usuario_fel, numero_autorizacion.text, "", "PDF")
                    logging.warning(str(resultado))
                    factura.pdf_fel = resultado['ResponseData']['ResponseData3']
                else:
                    factura.error_certificador(resultado['Response']['Description'])
                    return False

        return True

    def button_cancel(self):
        result = super(AccountMove, self).button_cancel()
        for factura in self:
            if factura.requiere_certificacion() and factura.firma_fel:
                dte = factura.dte_anulacion()

                xmls = etree.tostring(dte, xml_declaration=True, encoding="UTF-8")
                logging.warning(xmls.decode("utf-8"))
                xmls_base64 = base64.b64encode(xmls)
                wsdl = 'https://fel.g4sdocumenta.com/webservicefront/factwsfront.asmx?wsdl'
                if factura.company_id.pruebas_fel:
                    wsdl = 'https://pruebasfel.g4sdocumenta.com/webservicefront/factwsfront.asmx?wsdl'
                client = zeep.Client(wsdl=wsdl)

                resultado = client.service.RequestTransaction(factura.company_id.requestor_fel, "SYSTEM_REQUEST", "GT", factura.company_id.vat, factura.company_id.requestor_fel, factura.company_id.usuario_fel, "VOID_DOCUMENT", xmls_base64, "XML")
                logging.warning(str(resultado))

                if not resultado['Response']['Result']:
                    raise UserError(resultado['Response']['Description'])

    def obtener_pdf(self):
        for factura in self:    
            wsdl = 'https://fel.g4sdocumenta.com/webservicefront/factwsfront.asmx?wsdl'
            if factura.company_id.pruebas_fel:
                wsdl = 'https://pruebasfel.g4sdocumenta.com/webservicefront/factwsfront.asmx?wsdl'
            client = zeep.Client(wsdl=wsdl)

            resultado = client.service.RequestTransaction(factura.company_id.requestor_fel, "GET_DOCUMENT", "GT", factura.company_id.vat, factura.company_id.requestor_fel, factura.company_id.usuario_fel, factura.firma_fel, "", "PDF")
            logging.warning(str(resultado))
            factura.pdf_fel = resultado['ResponseData']['ResponseData3']

class AccountJournal(models.Model):
    _inherit = "account.journal"

class ResCompany(models.Model):
    _inherit = "res.company"
    
    requestor_fel = fields.Char('Requestor FEL', copy=False)
    usuario_fel = fields.Char('Usuario FEL', copy=False)
    pruebas_fel = fields.Boolean('Modo de Pruebas FEL')
