/** @odoo-module alias=paylox.system.page **/
'use strict';

import core from 'web.core';
import rpc from 'web.rpc';
import publicWidget from 'web.public.widget';
import dialog from 'web.Dialog';
import utils from 'web.utils';
import payloxPage from 'paylox.page';
import fields from 'paylox.fields';
import { format } from 'paylox.tools';

const _t = core._t;
const qweb = core.qweb;

payloxPage.include({
    init: function (parent, options) {
        this._super(parent, options);
        this.system = new fields.string({
            default: false,
        });
    },

    _getParams: function () {
        const params = this._super.apply(this, arguments);
        const $items = $('input[type="checkbox"].payment-items:checked');
        if ($items.length) {
            const payment_ids = [];
            $items.each(function () { payment_ids.push(parseInt($(this).data('id'))); });
            params['system'] = this.system.value;
            params['payments'] = payment_ids;
        }
        return params;
    },

    _checkData: function () {
        var $items = $('input[type="checkbox"].payment-items');
        if (!$items.length) {
            return this._super.apply(this, arguments);
        }

        var $items = $('input[type="checkbox"].payment-items:checked');
        if (!$items.length) {
            this.displayNotification({
                type: 'warning',
                title: _t('Warning'),
                message: _t('Please select at least one payment'),
            });
            this._enableButton();
            return false;
        } else {
            return this._super.apply(this, arguments);
        }
    },

});

publicWidget.registry.payloxSystemPage = publicWidget.Widget.extend({
    selector: '.payment-system',
    xmlDependencies: ['/payment_jetcheckout_system/static/src/xml/system.xml'],

    init: function (parent, options) {
        this._super(parent, options);
        this.currency = {
            id: 0,
            decimal: 2,
            name: '',
            separator: '.',
            thousand: ',', 
            position: 'after',
            symbol: '', 
        },
        this.amount = new fields.float({
            default: 0,
        });
        this.vat = new fields.string();
        this.payment = {
            privacy: new fields.element({
                events: [['click', this._onClickPrivacy]],
            }),
            agreement: new fields.element({
                events: [['click', this._onClickAgreement]],
            }),
            membership: new fields.element({
                events: [['click', this._onClickMembership]],
            }),
            contact: new fields.element({
                events: [['click', this._onClickContact]],
            }),
            item: new fields.element({
                events: [['change', this._onChangePaid]],
            }),
            items: new fields.element({
                events: [['change', this._onChangePaidAll]],
            }),
            tags: new fields.element({
                events: [['click', this._onClickTag]],
            }),
            link: new fields.element({
                events: [['click', this._onClickLink]],
            }),
            pivot: new fields.element(),
        };
    },
 
    start: function () {
        const self = this;
        return this._super.apply(this, arguments).then(function () {
            payloxPage.prototype._setCurrency.apply(self);
            payloxPage.prototype._start.apply(self);
            if (self.payment.item.exist) {
                self._onChangePaid();
            }
        });
    },

    _onChangePaidAll: function (ev) {
        if (this.payment.items.checked) {
            this.payment.item.checked = true;
        } else {
            this.payment.item.checked = false;
        }
        this._onChangePaid();
    },

    _onClickTag: function (ev) {
        const $button = $(ev.currentTarget);
        const pid = $button.data('id');
        $button.toggleClass('btn-light');

        _.each(this.payment.item.$, function(item) {
            const $el = $(item);
            if ($el.data('type-id') === pid) {
                if ($button.hasClass('btn-light')) {
                    $el.prop('checked', false);
                    $el.closest('tr').addClass('d-none');
                } else {
                    $el.prop('checked', true);
                    $el.closest('tr').removeClass('d-none');
                }
            }
        });
        this._onChangePaid();
    },

    _onChangePaid: function (ev) {
        if (!this.amount.exist) {
            return;
        }

        if (ev) {
            const $input = $(ev.currentTarget);
            const id = $input.data('id');
            const checked = $input.prop('checked');
            $('input[type="checkbox"][data-id="' + id + '"].payment-items').prop('checked', checked);
        }

        const $total = $('p.payment-amount-total');
        const $items = $('input[type="checkbox"].payment-items:checked');
        this.payment.items.checked = !!$items.length;

        let amount = 0;
        $items.each(function() { amount += parseFloat($(this).data('amount'))});
        
        const event = new Event('update');
        this.amount.value = format.float(amount);
        this.amount.$[0].dispatchEvent(event);

        $total.html(format.currency(amount, this.currency.position, this.currency.symbol, this.currency.decimal));
    },

    _onClickPrivacy: function (ev) {
        ev.stopPropagation();
        ev.preventDefault();
        rpc.query({route: '/p/privacy'}).then(function (content) {
            new dialog(this, {
                title: _t('Privacy Policy'),
                $content: $('<div/>').html(content),
            }).open();
        });
    },

    _onClickAgreement: function (ev) {
        ev.stopPropagation();
        ev.preventDefault();
        rpc.query({route: '/p/agreement'}).then(function (content) {
            new dialog(this, {
                title: _t('Distant Sale Agreement'),
                $content: $('<div/>').html(content),
            }).open();
        });
    },

    _onClickMembership: function (ev) {
        ev.stopPropagation();
        ev.preventDefault();
        rpc.query({route: '/p/membership'}).then(function (content) {
            new dialog(this, {
                title: _t('Membership Agreement'),
                $content: $('<div/>').html(content),
            }).open();
        });
    },

    _onClickContact: function (ev) {
        ev.stopPropagation();
        ev.preventDefault();
        rpc.query({route: '/p/contact'}).then(function (content) {
            new dialog(this, {
                title: _t('Contact Information'),
                $content: $('<div/>').html(content),
            }).open();
        });
    },

    _onClickLink: function (ev) {
        ev.stopPropagation();
        ev.preventDefault();
        const params = [
            ['amount', this.amount.value],
            ['currency', this.currency.name],
            ['vat', this.vat.value],
        ];

        let link = window.location.href;
        for (let i=0; i<params.length; i++) {
            if (!i) {
                link += '?';
            } else {
                link += '&';
            }
            link += params[i][0] + '=' + params[i][1];
        }
        navigator.clipboard.writeText(link);

        const content = qweb.render('paylox.system.link', { link });
        this.displayNotification({
            type: 'info',
            title: _t('Payment link is ready'),
            message: utils.Markup(content),
            sticky: true,
        });
    },
});

export default publicWidget.registry.payloxSystemPage;
