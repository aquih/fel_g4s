# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import zeep
import logging

class Partner(models.Model):
    _inherit = "res.partner"
            
    def obtener_nombre_facturacion_fel(self):
        vat = self.vat
        if self.nit_facturacion_fel:
            vat = self.nit_facturacion_fel
            
        res = self._datos_sat(self.env.company, vat)
        self.nombre_facturacion_fel = res['nombre']
                
    def _datos_sat(self, company, vat):
        if vat:
            client = zeep.Client(wsdl='http://fel.g4sdocumenta.com/ConsultaNIT/ConsultaNIT.asmx?wsdl')
            resultado = client.service.getNIT(vat, company.vat, company.requestor_fel)['Response']
            logging.warning(resultado)
            
            if resultado['Result'] == True:
                return {'nombre': resultado['nombre'], 'nit': resultado['NIT']}
            else:
                raise ValidationError(res['error'])
                
        return {'nombre': '', 'nit': ''}
