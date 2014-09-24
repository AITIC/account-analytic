# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account analytic plan required module for OpenERP
#    Copyright (C) 2014 Acsone (http://acsone.eu).
#    @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _


class account_account_type(orm.Model):
    _inherit = "account.account.type"

    _columns = {
        'analytic_policy': fields.selection([
            ('optional', 'Optional'),
            ('always', 'Always (analytic account)'),
            ('always_plan', 'Always (analytic distribution)'),
            ('always_plan_or_account',
             'Always (analytic account or distribution)'),
            ('never', 'Never')
            ], 'Policy for analytic account',
            help="Set the policy for analytic accounts : if you select "
            "'Optional', the accountant is free to put an analytic account "
            "on an account move line with this type of account ; if you "
            "select 'Always', the accountant will get an error message if "
            "there is no analytic account ; if you select 'Never', the "
            "accountant will get an error message if an analytic account "
            "is present."),  # TODO: help
    }


class account_move_line(orm.Model):
    _inherit = "account.move.line"

    def _check_analytic_required_msg(self, cr, uid, ids, context=None):
        msg = super(account_move_line, self).\
            _check_analytic_required_msg(cr, uid, ids, context=context)
        if msg:
            return msg
        for move_line in self.browse(cr, uid, ids, context=context):
            if move_line.analytic_account_id and move_line.analytics_id:
                return _('Analytic account and analytic distribution '
                         'are mutually exclusive')
            if move_line.debit == 0 and move_line.credit == 0:
                continue
            analytic_policy = \
                move_line.account_id.user_type.analytic_policy
            if analytic_policy == 'always_plan' \
                    and not move_line.analytics_id:
                return _("Analytic policy is set to "
                         "'Always (analytic distribution)' with account "
                         "%s '%s' but the analytic distribution is "
                         "missing in the account move line with "
                         "label '%s'.") % \
                        (move_line.account_id.code,
                         move_line.account_id.name,
                         move_line.name)
            if analytic_policy == 'always_plan_or_account' \
                    and not move_line.analytic_account_id \
                    and not move_line.analytics_id:
                return _("Analytic policy is set to "
                         "'Always (analytic account or distribution)' "
                         "with account %s '%s' but the analytic "
                         "distribution and the analytic account are "
                         "missing in the account move line "
                         "with label '%s'.") % \
                        (move_line.account_id.code,
                         move_line.account_id.name,
                         move_line.name)
            elif analytic_policy == 'never' and move_line.analytics_id:
                return _("Analytic policy is set to 'Never' with account "
                         "%s '%s' but the account move line with label "
                         "'%s' has an analytic distribution %s '%s'.") % \
                       (move_line.account_id.code,
                        move_line.account_id.name,
                        move_line.name,
                        move_line.analytic_account_id.code,
                        move_line.analytic_account_id.name)

    def _check_analytic_required(self, cr, uid, ids, context=None):
        return not self._check_analytic_required_msg(cr, uid, ids,
                                                     context=context)

    _constraints = [
        (_check_analytic_required,
         _check_analytic_required_msg,
         ['analytic_account_id', 'analytics_id']),
    ]
