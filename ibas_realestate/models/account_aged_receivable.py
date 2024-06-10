from odoo import models, api, _

class CustomAgedReceivableReport(models.AbstractModel):
    _inherit = "account.aged.receivable.report.handler"

    def _get_columns_name(self, options):
        columns = super(CustomAgedReceivableReport, self)._get_columns_name(options)

        # Find the index of the "Due Date" column
        due_date_index = next((index for index, column in enumerate(columns) if column.get('name') == _("Due Date")),
                              None)

        # Define new columns to be inserted
        new_columns = [
            {'name': _("Unit"), 'class': '', 'style': 'text-align:center; white-space:nowrap;'},
            {'name': _("Project"), 'class': '', 'style': 'text-align:center; white-space:nowrap;'}
        ]

        # Check if "Due Date" column was found
        if due_date_index is not None:
            # Insert the new columns before the "Due Date" column
            for new_column in reversed(new_columns):
                columns.insert(due_date_index, new_column)
        else:
            # If "Due Date" column was not found, append the new columns at the end
            columns.extend(new_columns)

        return columns

    @api.model
    def _get_lines(self, options, line_id=None):
        lines = super(CustomAgedReceivableReport, self)._get_lines(options, line_id)
        new_lines = []

        for line in lines:
            if 'partner_id' in line:
                # For folded lines, determine if there are multiple units or projects
                if not line.get('unfolded'):
                    units, projects = set(), set()
                    account_move_lines = self.env['account.move.line'].search([
                        ('partner_id', '=', line['partner_id']),
                        ('account_id.internal_type', '=', 'receivable'),
                        ('move_id.state', '=', 'posted'),
                    ])

                    for account_move_line in account_move_lines:
                        if len(units) > 1 and len(projects) > 1:
                            # If we already have multiple units and projects, no need to check further
                            break

                        sale_order = self._get_related_sale_order(account_move_line)
                        if sale_order:
                            unit_name = sale_order.unit_id.name if sale_order.unit_id else ""
                            project_name = sale_order.project_id.name if sale_order.project_id else ""
                            units.add(unit_name)
                            projects.add(project_name)

                    unit_name = "Multiple" if len(units) > 1 else next(iter(units), "")
                    project_name = "Multiple" if len(projects) > 1 else next(iter(projects), "")

                    # Insert "Multiple" or the actual unit/project names
                    line['columns'][0:0] = [{'name': unit_name}, {'name': project_name}]

                new_lines.append(line)

                # If the line is unfolded, we add unit and project information to its children
                if line.get('unfolded'):
                    for aml_line in lines:
                        if aml_line.get('parent_id') == line['id']:
                            account_move_line = self.env['account.move.line'].browse(aml_line['id'])
                            sale_order = self._get_related_sale_order(account_move_line)
                            unit_name = sale_order.unit_id.name if sale_order and sale_order.unit_id else ""
                            project_name = sale_order.project_id.name if sale_order and sale_order.project_id else ""

                            # Insert the unit and project names
                            aml_line['columns'].insert(0, {'name': unit_name})
                            aml_line['columns'].insert(1, {'name': project_name})

                            new_lines.append(aml_line)

        return new_lines

    def _get_unit_and_project_from_move_lines(self, partner_id):
        account_move_lines = self.env['account.move.line'].search([
            ('partner_id', '=', partner_id),
            ('account_id.internal_type', '=', 'receivable'),
            ('move_id.state', '=', 'posted'),
        ])
        for account_move_line in account_move_lines:
            sale_order = self._get_related_sale_order(account_move_line)
            if sale_order:
                unit_name = sale_order.unit_id.name if sale_order.unit_id else ""
                project_name = sale_order.project_id.name if sale_order.project_id else ""
                return unit_name, project_name
        return "", ""

    def _get_related_sale_order(self, account_move_line):
        # Define the logic to fetch the related sale.order based on the account.move.line
        # This could depend on your specific business flow and Odoo configuration
        # Example: Fetching the sale order related to the invoice of the account move line
        sale_order = self.env['sale.order'].search([
            ('invoice_ids', 'in', account_move_line.move_id.ids),
        ], limit=1)
        return sale_order
