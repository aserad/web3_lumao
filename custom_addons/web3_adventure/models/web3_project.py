from odoo import models, fields, api, _


class Web3Project(models.Model):
    _name = 'web3.project'
    _description = 'Web3项目'

    name = fields.Char(string='Name', required=True)
    project_link = fields.Char(string='项目地址')  # 项目地址
    task_link = fields.Char(string='任务地址')  # 任务地址
    faucet_link = fields.Char(string='领水地址')  # 领水地址

    description = fields.Text(string='描述')  # 任务描述
    note = fields.Html(string='备注')  # 备注
    sequence = fields.Integer(string='序号')
    priority = fields.Selection([('very_high', '极高'), ('high', '高'),
                                 ('medium', '中等'), ('low', '低')], string='优先级')  # 项目优先级
    progress = fields.Char(string='进度')  # 项目进度
    snapshot_date = fields.Date(string='预计快照日期')  # 预计快照日期
    airdrop_date = fields.Date(string='预计空投日期')  # 预计空投日期
    active = fields.Boolean(default=True, string='有效')


class Web3Tasks(models.Model):
    _name = 'web3.tasks'
    _inherits = {'web3.project': 'project_id'}
    _description = 'Web3任务'

    project_id = fields.Many2one('web3.project', required=True, ondelete='restrict', auto_join=True,
                                 index=True, string='Web3项目')
    name = fields.Char(string='名称')
    priority = fields.Selection([('very_high', '极高'), ('high', '高'),
                                 ('medium', '中等'), ('low', '低')], string='优先级')  # 任务优先级
    sequence = fields.Integer(string='序号')
    reminder_time = fields.Datetime("每日提醒时间")
    description = fields.Text(string='描述')  # 任务描述
    galxe_task = fields.Text(string='Galxe任务')

    # 关联的钱包
    wallet_ids = fields.Many2many('web3.wallet', relation='web3_project_wallet_rel',
                                  column1='project_id', column2='wallet_id', string='虚拟币钱包')
    # 关联的社交帐号
    social_account_ids = fields.Many2many('social.account', relation='web3_project_sicoal_account_rel',
                                          column1='project_id', column2='account_id', string='社交账号')
    # 项目登录方式以及登录账号
    login_type = fields.Selection([('self', '自建账号'), ('wallet', '钱包登录'),
                                   ('social', '社交账号登录'),], string='登录方式')
    login_account = fields.Char('登录账号')
    login_password = fields.Char('密码')
    login_wallet = fields.Many2one('web3.wallet', string='登录钱包')
    login_social_account = fields.Many2one('social.account', string='登录社交帐号')

    costs = fields.Text(string='成本')  # 花费成本
    aridrop_amount = fields.Text(string='空头数量')  # 空投数量

    @api.onchange('project_id')
    def _onchange_project_id(self):
        for rec in self:
            rec.name = rec.project_id.name
            rec.priority = rec.project_id.priority
            rec.description = rec.project_id.description
            rec.sequence = rec.project_id.sequence


