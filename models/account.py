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

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    pdf_fel = fields.Binary('PDF FEL', copy=False)
    pdf_fel_name = fields.Char('Nombre PDF FEL', default='pdf_fel.pdf', size=32)

    def invoice_validate(self):
        for factura in self:    
            if factura.journal_id.generar_fel:
                if factura.firma_fel:
                    raise UserError("La factura ya fue validada, por lo que no puede ser validada nuevamnte")
                
                dte = factura.dte_documento()
                xmls = etree.tostring(dte, xml_declaration=True, encoding="UTF-8")
                logging.warn(xmls)
                xmls_base64 = base64.b64encode(xmls)
                wsdl = 'https://fel.g4sdocumenta.com/webservicefront/factwsfront.asmx?wsdl'
                if factura.company_id.pruebas_fel:
                    wsdl = 'https://pruebasfel.g4sdocumenta.com/webservicefront/factwsfront.asmx?wsdl'
                client = zeep.Client(wsdl=wsdl)

                resultado = client.service.RequestTransaction(factura.company_id.requestor_fel, "SYSTEM_REQUEST", "GT", factura.company_id.vat, factura.company_id.requestor_fel, factura.company_id.usuario_fel, "POST_DOCUMENT_SAT", xmls_base64, str(factura.id))
                logging.warn(str(resultado))

                if resultado['Response']['Result']:
                    xml_resultado = base64.b64decode(resultado['ResponseData']['ResponseData1'])
                    logging.warn(xml_resultado)
                    dte_resultado = etree.XML(xml_resultado)

                    numero_autorizacion =  dte_resultado.xpath("//*[local-name() = 'NumeroAutorizacion']")[0]

                    factura.firma_fel = numero_autorizacion.text
                    factura.name = str(numero_autorizacion.get("Serie"))+"-"+str(numero_autorizacion.get("Numero"))
                    factura.serie_fel = numero_autorizacion.get("Serie")
                    factura.numero_fel = numero_autorizacion.get("Numero")
                    factura.documento_xml_fel = xmls_base64
                    factura.resultado_xml_fel = xml_resultado

                    resultado = client.service.RequestTransaction(factura.company_id.requestor_fel, "GET_DOCUMENT", "GT", factura.company_id.vat, factura.company_id.requestor_fel, factura.company_id.usuario_fel, numero_autorizacion.text, "", "PDF")
                    logging.warn(str(resultado))
                    factura.pdf_fel = resultado['ResponseData']['ResponseData3']
                else:
                    raise UserError(resultado['Response']['Description'])

        return super(AccountInvoice,self).invoice_validate()

    def action_cancel(self):
        result = super(AccountInvoice, self).action_cancel()
        if result:
            for factura in self:
                if factura.journal_id.generar_fel:
                    dte = factura.dte_anulacion()
                    if dte:
                        xmls = etree.tostring(dte, xml_declaration=True, encoding="UTF-8")
                        logging.warn(xmls)
                        xmls_base64 = base64.b64encode(xmls)
                        wsdl = 'https://fel.g4sdocumenta.com/webservicefront/factwsfront.asmx?wsdl'
                        if factura.company_id.pruebas_fel:
                            wsdl = 'https://pruebasfel.g4sdocumenta.com/webservicefront/factwsfront.asmx?wsdl'
                        client = zeep.Client(wsdl=wsdl)

                        resultado = client.service.RequestTransaction(factura.company_id.requestor_fel, "SYSTEM_REQUEST", "GT", factura.company_id.vat, factura.company_id.requestor_fel, factura.company_id.usuario_fel, "VOID_DOCUMENT", xmls_base64, "XML")
                        logging.warn(str(resultado))

                        if not resultado['Response']['Result']:
                            raise UserError(resultado['Response']['Description'])

class AccountJournal(models.Model):
    _inherit = "account.journal"

    generar_fel = fields.Boolean('Generar FEL')

class ResCompany(models.Model):
    _inherit = "res.company"
    
    requestor_fel = fields.Char('Requestor GFACE', copy=False)
    usuario_fel = fields.Char('Usuario GFACE', copy=False)
