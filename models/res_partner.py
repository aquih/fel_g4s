# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import zeep
import logging

class Partner(models.Model):
    _inherit = "res.partner"
    
    @api.onchange("vat")
    def _onchange_vat(self):
        self.nit_facturacion_fel = self.vat

    @api.onchange("nit_facturacion_fel")
    def _onchange_nit_facturacion_fel(self):
        self.obtener_nombre_facturacion_fel(self.nit_facturacion_fel)

    def obtener_nombre_facturacion_fel(self, nit):
        client = zeep.Client(wsdl='http://fel.g4sdocumenta.com/ConsultaNIT/ConsultaNIT.asmx?wsdl')
        resultado = client.service.getNIT(nit, self.env.company.vat, self.env.company.requestor_fel)
        logging.warning(str(resultado))
        if resultado['Response']['Result']:
            self.nombre_facturacion_fel = resultado['Response']['nombre']
        else:
            self.nombre_facturacion_fel = 'NIT no valido'