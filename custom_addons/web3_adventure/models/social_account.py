from odoo import models, fields, api, _


class SocialAccountType(models.Model):
    _name = 'social.account.type'
    _description = '社交帐号类型'

    name = fields.Char(string='名称', required=True)
    code = fields.Char(string='编码', required=True)
    abbr_name = fields.Char(string='简称')


class SocialAccount(models.Model):
    _name = 'social.account'
    _description = '社交帐号'

    name = fields.Char(string='名称', store=True, compute='_compute_name')
    account = fields.Char(string='账号', required=True)  # 账号
    password = fields.Char(string='密码')  # 密码
    social_account_type = fields.Many2one('social.account.type',
                                          string='社交账号类型', required=True)
    sequence = fields.Integer(string='序号')
    note = fields.Char(string='说明')
    session_data = fields.Text(string='Session Data')

    @api.depends('account', 'social_account_type.abbr_name')
    def _compute_name(self):
        for record in self:
            record.name = f'{record.social_account_type.abbr_name}/{record.account}'

    def check_is_valid_session(self):
        """
        检查 session_data 是否可用
        :return:
        """
        pass  # todo


