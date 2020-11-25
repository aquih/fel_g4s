# fel_g4s

Para adenda que envía correo:

```python
attr_qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
nsdef = {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
CorreoElectronico = etree.SubElement(Adenda, "CorreoElectronico", {attr_qname: 'Schema-ediFactura esquemaAdendaEmail.xsd'}, xmlns="Schema-ediFactura", nsmap=nsdef)
De = etree.SubElement(CorreoElectronico, "De")
De.text = factura.company_id.email
Para = etree.SubElement(CorreoElectronico, "Para")
Para.text = factura.partner_id.email
Asunto = etree.SubElement(CorreoElectronico, "Asunto")
Asunto.text = "DOCUMENTO TRIBUTARIO ELECTRONICO"
Adjuntos = etree.SubElement(CorreoElectronico, "Adjuntos")
Adjuntos.text = "XML PDF"
```
