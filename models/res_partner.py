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
            res = self._datos_sat(self.env.company, nit)
            if res['Result'] == True:
                self.nombre_facturacion_fel = res['nombre']
            else:
                self.nombre_facturacion_fel = res['error']
                
    def _datos_sat(self, company, vat):
        if vat:
            client = zeep.Client(wsdl='http://fel.g4sdocumenta.com/ConsultaNIT/ConsultaNIT.asmx?wsdl')
            resultado = client.service.getNIT(vat, company.vat, company.requestor_fel)['Response']
            logging.warning(resultado)
            return resultado
        return {'nombre': '', 'nit': ''}