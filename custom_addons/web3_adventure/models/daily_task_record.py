import datetime

from odoo import models, fields, api, _


class DailyTaskRecord(models.Model):
    _name = 'daily.task.record'
    _rec_name = 'task_id'

    task_id = fields.Many2one('web3.tasks', string='任务')
    operate_date = fields.Date('日期', default=fields.Date.today())
    state = fields.Selection([('todo', '待办'), ('done', '完成'), ('undone', '未做')],
                             default='todo', string='状态')

    task_link = fields.Char(related='task_id.task_link', store=True)
    faucet_link = fields.Char(related='task_id.faucet_link', store=True)
    description = fields.Text(related='task_id.description', store=True)
    login_type = fields.Selection(related='task_id.login_type', store=True)
    login_account = fields.Char(related='task_id.login_account', store=True)
    login_password = fields.Char(related='task_id.login_password', store=True)
    login_wallet = fields.Many2one(related='task_id.login_wallet', store=True)
    login_social_account = fields.Many2one(related='task_id.login_social_account', store=True)
    priority = fields.Selection(related='task_id.priority', store=True)
    sequence = fields.Integer(related='task_id.sequence', store=True)
    active = fields.Boolean(default=True, string='Active')

    def cron_create_daily_task(self):
        today = fields.Date.today()
        yestery = today - datetime.timedelta(days=1)
        # 创建今日任务
        tasks = self.env['web3.tasks'].search([])
        vals_list = []
        for task in tasks:
            vals_list.append({
                'task_id': task.id,
                'operate_date': today,
            })
        self.create(vals_list)
        # 更新昨天未处理的任务状态
        self.search([
            ('operate_date', '=', yestery),
            ('state', '=', 'todo'),
        ]).write({'state': 'undone'})

    def action_done(self):
        self.write({'state': 'done'})
