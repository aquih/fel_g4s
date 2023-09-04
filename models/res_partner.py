# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import zeep
import logging

class Partner(models.Model):
    _inherit = "res.partner"
            
    def obtener_nombre_facturacion_fel(self):
        nit = self.nit_facturacion_fel
        if not nit:
            nit = self.vat
        if nit:
            client = zeep.Client(wsdl='http://fel.g4sdocumenta.com/ConsultaNIT/ConsultaNIT.asmx?wsdl')
            resultado = client.service.getNIT(nit, self.env.company.vat, self.env.company.requestor_fel)
            logging.warning(str(resultado))
            if resultado['Response']['Result']:
                self.nombre_facturacion_fel = resultado['Response']['nombre']
            else:
                self.nombre_facturacion_fel = 'NIT no valido'