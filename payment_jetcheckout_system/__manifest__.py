# -*- coding: utf-8 -*-
# Copyright © 2022 Projet (https://www.jetcheckout.com)
# Part of JetCheckout License. See LICENSE file for full copyright and licensing details.

{
    'name': 'jetCheckout Payment System',
    'version': '1.4',
    'author': 'Projet',
    'website': 'https://www.jetcheckout.com',
    'license': 'LGPL-3',
    'sequence': 1454,
    'category': 'Accounting/Payment Acquirers',
    'depends': [
        'sale',
        'sales_team',
        'payment_jetcheckout',
        'sms_api'
    ],
    'data': [
        'data/data.xml',
        'views/dashboard.xml',
        'views/company.xml',
        'views/acquirer.xml',
        'views/transaction.xml',
        'views/templates.xml',
        'views/mail.xml',
        'views/user.xml',
        'views/item.xml',
        'views/partner.xml',
        'views/website.xml',
        'views/settings.xml',
        'views/actions.xml',
        'report/company.xml',
        'wizards/send.xml',
        'wizards/item.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_qweb': [
            'payment_jetcheckout_system/static/src/xml/dashboard.xml',
            'payment_jetcheckout_system/static/src/xml/company.xml',
        ],
        'web.assets_backend': [
            'payment_jetcheckout_system/static/src/js/dashboard.js',
            'payment_jetcheckout_system/static/src/js/company.js',
            'payment_jetcheckout_system/static/src/scss/company.scss',
            'payment_jetcheckout_system/static/src/scss/send.scss',
        ],
        'web.assets_frontend': [
            'payment_jetcheckout_system/static/src/js/system.js',
            'payment_jetcheckout_system/static/src/scss/frontend.scss',
        ],
    },
    'application': False,
    'images': ['static/description/icon.png'],
}
