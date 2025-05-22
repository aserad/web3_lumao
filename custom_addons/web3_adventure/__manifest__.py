# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Web3 Adventure',
    'version' : '0.1',
    'summary': 'Web3 Adventure',
    'sequence': 10,
    'description': """Web3 Adventure""",
    'category': 'Tools',
    'website': '',
    'depends' : ['base'],
    'data': [
        'security/ir.model.access.csv',

        'views/social_account_type_view.xml',
        'views/social_account_view.xml',
        'views/web3_currency_type_view.xml',
        'views/web3_project_view.xml',
        'views/web3_tasks_view.xml',
        'views/web3_wallet_type_view.xml',
        'views/web3_wallet_view.xml',
        'views/daily_task_record_views.xml',
        'views/script_tasks_view.xml',
        'views/menu_item_view.xml',

        'data/social_account_type.xml',
        'data/web3_currency_type.xml',
        'data/web3_wallet_type.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
