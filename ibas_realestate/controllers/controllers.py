# -*- coding: utf-8 -*-


from odoo import http
from odoo.http import request, Response
import base64

from odoo.http import content_disposition, Controller, request, route


class ibasPreviewController(http.Controller):
    @http.route('/ibas/preview_attachment', type='http', auth='public',website=True, csrf=False)
    def preview_attachment(self, attachment_id=None, **kwargs):
        data = {'attachment_id':int(attachment_id)}
        return http.request.render('ibas_realestate.testing', data)




































        attachment = request.env['ir.attachment'].sudo().browse(int(attachment_id))
        # if post.get('attachment', False):
            # name = post.get('attachment').filename
        if attachment.name.endswith('.pdf'):
            data = BytesIO(attachment.datas).read()
            return {
            'name': attachment.name,
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s/%d/file/%s?download=false' % (attachment._name, attachment.id, attachment.name),
            }
            # file = attachment.datas
            # attachment = data
            # doc = request.env['ir.attachment'].create([{
            #     'name': name,
            #     'datas': base64.b64encode(attachment),
            # }])
            # filename = "%s.pdf" % (re.sub('\W+', '-', model._get_report_base_filename()))
            # pdfhttpheaders = [
            #     ("Content-Type", "application/pdf"),
            #     ("Content-Length", 1),
                # ('Content-Disposition', content_disposition(attachment.name))
            # ]
            # res = request.make_response(data, headers=pdfhttpheaders)
            # return res

            # out = data_file.read()
            # data_file.close()
            # self.name = 'Failed Cashier Saee IDS' + '.xlsx'
            # self.file = base64.b64encode(out)
         

#    status, headers, content = request.env['ir.http'].binary_content(id=mock_attachment.id, unique=asset.checksum)
#         content_base64 = base64.b64decode(content) if content else ''
#         headers.append(('Content-Length', len(content_base64)))
#         return request.make_response(content_base64, headers)




        #    <a t-attf-href="/web/content/#{attachment.id}?download=true&amp;access_token=#{attachment.access_token}" target="_blank">
        #                 <div class='oe_attachment_embedded o_image' t-att-title="attachment.name" t-att-data-mimetype="attachment.mimetype"/>
        #                 <div class='o_portal_chatter_attachment_name'><t t-esc='attachment.name'/></div>
        #             </a>

        #     reporthttpheaders = [
        #     ('Content-Type', 'application/pdf'),
        #     ('Content-Length', 1),]
        # if report_type == 'pdf' and download:
        #     filename = "%s.pdf" % (re.sub('\W+', '-', model._get_report_base_filename()))
        #     reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))
        # return request.make_response(report, headers=reporthttpheaders)

        # if attachment.name.endswith('.pdf'):
        #     file = post.get('attachment')
        #     attachment = file.read()
        #     doc = request.env['ir.attachment'].create([{
        #         'name': name,
        #         'datas': base64.b64encode(attachment),
        #     }])
        #     pdfhttpheaders = [
        #         ("Content-Type", "application/pdf"),
        #         ("Content-Length", len(attachment)),
        #     ]
        #     res = request.make_response(attachment, headers=pdfhttpheaders)
        #     return res
