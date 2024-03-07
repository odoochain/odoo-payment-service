/** @odoo-module alias=paylox.system.product.page **/
'use strict';

import { _t, qweb } from 'web.core';
import rpc from 'web.rpc';
import dialog from 'web.Dialog';
import publicWidget from 'web.public.widget';

import fields from 'paylox.fields';
import payloxPage from 'paylox.page';
import framework from 'paylox.framework';
import systemPage from 'paylox.system.page';
import { format } from 'paylox.tools';

payloxPage.include({

    init: function (parent, options) {
        this._super(parent, options);
        this.state = {
            product: {
                payment: false,
            }
        };
    },

    start: function () {
        return this._super.apply(this, arguments).then(() => {
            if (this.options.product) {
                window.addEventListener('payment-started', () => {
                    this.state.product.payment = true;
                    this._getInstallment();
                });
                window.addEventListener('payment-stopped', () => {
                    this.state.product.payment = false;

                    this.installment.colempty.$.removeClass('d-none');
                    this.installment.col.$.addClass('d-none');
                    this.installment.col.html = '';
                    this.installment.cols = [];
    
                    this.installment.rowempty.$.removeClass('d-none');
                    this.installment.row.$.addClass('d-none');
                    this.installment.row.html = '';
                    this.installment.rows = [];
    
                    this.card.logo.html = '';
                    this.card.logo.$.removeClass('show');
                    this.card.bin = '';
                    this.card.family = '';
                });
            }
        });
    },

    _checkData: function () {
        if (this.options.product) {
            if (!this.state.product.payment) {
                this.displayNotification({
                    type: 'warning',
                    title: _t('Warning'),
                    message: _t('Price locked has been removed.\nPlease start the payment procedure all over.'),
                });
                this._enableButton();
                return false;
            }
        } else {
            return this._super.apply(this, arguments);
        }
    },

    //_getParams: function () {
    //    let params = this._super.apply(this, arguments);
    //    return params;
    //},
});

publicWidget.registry.payloxSystemProduct = systemPage.extend({
    selector: '.payment-product #wrapwrap',
    xmlDependencies: ['/payment_system_product/static/src/xml/page.xml'],

    init: function (parent, options) {
        this._super(parent, options);
        this._saveOrder = _.debounce(this._save, 1000);
        this._saveTime = undefined;

        this.lines = {};
        this.brands = {};
        this.products = {};
        this.validity = 0;
        this.commission = 0;
        this.product = {
            price: new fields.float({
                default: 0,
            }),
            qty: new fields.integer({
                default: 0,
                events: [['change', this._onChangeQty]],
            }),
            amount: new fields.float({
                default: 0,
            }),
            validity: new fields.float({
                default: 0,
            }),
            commission: new fields.float({
                default: 0,
            }),
            subtotal: new fields.float({
                default: 0,
            }),
            fee: new fields.float({
                default: 0,
            }),
            total: new fields.float({
                default: 0,
            }),
            counter: new fields.element(),
            items: new fields.element(),
            lines: new fields.element(),
            categ: new fields.element({
                events: [['click', this._onClickCateg]],
            }),
            plus: new fields.element({
                events: [['click', this._onClickPlus]],
            }),
            minus: new fields.element({
                events: [['click', this._onClickMinus]],
            }),
            brands: new fields.element({
                events: [['click', this._onClickBrands]],
            }),
            policy: new fields.element({
                events: [['click', this._onClickPolicy]],
            }),
            pay: new fields.element({
                events: [['click', this._onClickPay]],
            }),
            back: new fields.element({
                events: [['click', this._onClickBack]],
            }),
        }
    },

    start: function () {
        return this._super.apply(this, arguments).then(() => {
            this._getNumbers();
            this._getBrands();
            this._getProducts();
            this._updateLines();
            this._listenPrices();
        });
    },

    _save: function (values) {
        rpc.query({
            route: '/my/order',
            params: { values },
        }).then((res) => {
            this._saveTime = Date.now();
        }).catch((err) => {
            this.displayNotification({
                type: 'danger',
                title: _t('Error'),
                message: _t('An error occured.'),
            });
        });
    },

    _getNumbers: function () {
        this.validity = this.product.validity.value; this.product.validity.$.remove();
        this.commission = this.product.commission.value; this.product.commission.$.remove();
    },

    _getBrands: function () {
        let $brands = $('[field="product.brands"]');
        $brands.each((i, e) => {
            let bid = e.dataset.id;
            let pid = e.dataset.product;
            if (!(pid in this.brands)) {
                this.brands[pid] = {};
            }
            this.brands[pid][bid] = {
                id: parseInt(bid),
                name: e.dataset.name,
                image: e.dataset.image,
            }
        });
    },

    _getProducts: function () {
        let $products = $('[field="product.items"]');
        $products.each((i, e) => {
            let pid = e.dataset.id;
            this.products[pid] = {
                id: parseInt(pid),
                name: e.dataset.name,
                foreground: e.dataset.foreground,
                background: e.dataset.background,
            }
        });
    },

    _listenPrices: function () {
        const events = new EventSource('/longpolling/prices');
        console.log('Price service is active.');
        events.onmessage = (event) => {
            let changed = false;
            let $prices = this.product.price.$;
            let currency = [this.currency.position, this.currency.symbol, this.currency.decimal];
            for (let data of event.data.split('\n')) {
                let [code, price] = data.split(';'); price = parseFloat(price);
                let $price = $prices.filter(`[data-id="${code}"]`);
                let value = $price.data('value');
                if (price == value) {
                    continue;
                } else if (price > value) {
                    $price.css({ backgroundColor: '#93daa3' });
                } else if (price < value) {
                    $price.css({ backgroundColor: '#eccfd1' });
                }

                changed = true;
                $price.animate({ backgroundColor: '#ffffff' }, 'slow');
                $price.data('value', price);
                $price.text(format.currency(price, ...currency));
                this._onChangePrice($price, false);
            }
            if (changed) {
                this._updateLines();
            }
        };
        events.onerror = () => {
            console.error('An error occured on price service. Reconnecting...');
            events.close();
            setTimeout(this._listenPrices.bind(this), 10000);
        };
    },

    _onChangePrice($price, update=true) {
        let $qty = this.product.qty.$.filter(`.base[data-id=${$price.data('id')}]`);
        let $amount = this.product.amount.$.filter(`[data-id=${$price.data('id')}]`);

        let qty = parseFloat($qty.val());
        let price = parseFloat($price.data('value'));
        let value = qty * price;

        $amount.data('qty', qty);
        $amount.data('price', price);
        $amount.data('value', value);
        $amount.text(format.currency(value, this.currency.position, this.currency.symbol, this.currency.decimal));

        if (update) {
            this._updateLines();
        }
    },

    _updateLines() {
        if (this.timeout) return;

        let subtotal = 0;
        let brands = {};
        let currency = [this.currency.position, this.currency.symbol, this.currency.decimal];
        this.product.amount.$.filter(`.base`).each((i, e) => {
            let $e = $(e);
            let value = parseFloat($e.data('value'));
            if (value > 0) {
                let vid = $e.data('id') || 0;
                let bid = $e.data('brand') || 0;
                let pid = $e.data('product') || 0;
                let qty = parseFloat($e.data('qty') || 0);
                let price = parseFloat($e.data('price') || 0);
                let weight = parseFloat($e.data('weight') || 0);
                this.lines[vid] = { pid: vid, price, qty };

                if (!(bid in brands)) {
                    brands[bid] = { products: {}, name: this.brands?.[pid]?.[bid]?.['name'] || '' };
                }
                if (!(pid in brands[bid]['products'])) {
                    brands[bid]['products'][pid] = { weight: 0, value: 0, name: this.products[pid]['name'] };
                }
                brands[bid]['products'][pid]['weight'] += qty * weight;
                brands[bid]['products'][pid]['value'] += value;
                subtotal += value;
            }
        });

        this.product.brands.$.each((i, e) => {
            let $e = $(e);
            let $span = $e.find('span');
            let bid = parseInt($e.data('id'));
            let pid = parseInt($e.data('product'));

            let weight = brands?.[bid]?.['products']?.[pid]?.['weight'];
            if (weight) {
                $span.removeClass('d-none');
                $span.text(weight);
            } else {
                $span.addClass('d-none');
            }
        });

        brands = Object.values(brands);
        for (let brand of brands) {
            brand.products = Object.values(brand.products);
        }

        this.product.lines.html = qweb.render('paylox.product.lines', {
            format,
            brands,
            currency: this.currency,
        });

        let fee = subtotal * this.commission;
        let total = subtotal + fee;
        this.amount.value = format.float(total);
        this.amount.$.trigger('update');

        this.product.subtotal.text = format.currency(subtotal, ...currency);
        this.product.fee.text = format.currency(fee, ...currency);
        this.product.total.text = format.currency(total, ...currency);

        this._saveOrder({ lines: Object.values(this.lines) });
    },

    _onChangeQty(ev) {
        let $qty = $(ev.currentTarget);
        let pid = $qty.data('id');
        this.product.qty.$.filter(`[data-id=${pid}]`).val($qty.val());

        let $price = this.product.price.$.filter(`.base[data-id=${pid}]`);
        let $amount = this.product.amount.$.filter(`[data-id=${pid}]`);

        let qty = parseFloat($qty.val());
        let price = parseFloat($price.data('value'));
        let value = qty * price;

        $amount.data('qty', qty);
        $amount.data('value', value);
        $amount.text(format.currency(value, this.currency.position, this.currency.symbol, this.currency.decimal));

        this._updateLines();
    },

    _onClickCateg(ev) {
        const categ = ev.currentTarget.value;
        this.product.items.$.each((_, e) => {
            if (e.dataset.categ === categ) {
                e.classList.remove('d-none');
            } else {
                e.classList.add('d-none');
            }
        });
    },

    _onClickPlus(ev) {
        let btn = $(ev.currentTarget);
        let pid = btn.data('id');
        let qty = this.product.qty.$.filter(`.base[data-id=${pid}]`);

        let val = qty.val();
        qty.val(+val+1);
        qty.trigger('change');
    },

    _onClickMinus(ev) {
        let btn = $(ev.currentTarget);
        let pid = btn.data('id');
        let qty = this.product.qty.$.filter(`.base[data-id=${pid}]`);

        let val = qty.val();
        if (val > 0) {
            qty.val(+val-1);
        } else {
            qty.val(0);
        }
        qty.trigger('change');
    },

    _onClickBrands(ev) {
        let $btn = $(ev.currentTarget);
        let $item = this.product.items.$.filter(`[data-id=${ $btn.data('product') }]`);
        if ($btn.hasClass('base')) {
            $item.find(`[data-brand]`).each((i, e) => $(e).addClass('d-none'));
            $item.find(`[data-brand=${ $btn.data('id') }]`).each((i, e) => $(e).removeClass('d-none'));
    
            this.product.brands.$.filter(`[data-product=${ $btn.data('product') }]`).removeClass('active');
            this.product.brands.$.filter(`[data-product=${ $btn.data('product') }][data-id=${ $btn.data('id') }]`).each((i, e) => $(e).addClass('active'));
        } else {   
            let pid = parseInt($item.data('id'));
            let brands = Object.values(this.brands[pid]);
            let foreground = $item.data('foreground');
            let background = $item.data('background');
            let popup = new dialog(this, {
                size: 'small',
                title: _t('Choose a brand'),
                $content: qweb.render('paylox.product.brands', { brands, foreground, background }),
            });
            popup.open().opened(() => {
                popup.$modal.addClass('payment-product-brand-popup');
                popup.$modal.find('.modal-header').attr('style', `color:${foreground} !important;background-color:${background} !important`);
                popup.$modal.find('.modal-footer button').attr('style', `color:${foreground} !important;background-color:${background} !important`);
                popup.$modal.find('button').click((e) => {
                    let bid = parseInt(e.currentTarget.dataset.id);
                    if (!isNaN(bid)) {
                        $item.find(`[data-brand]`).each((i, e) => $(e).addClass('d-none'));
                        $item.find(`[data-brand=${ bid }]`).each((i, e) => $(e).removeClass('d-none'));
                
                        this.product.brands.$.filter(`[data-product=${ $btn.data('product') }]`).removeClass('active');
                        this.product.brands.$.filter(`[data-product=${ $btn.data('product') }][data-id=${ bid }]`).each((i, e) => $(e).addClass('active'));
                    }
                    popup.close();
                });
            });
        }
    },

    _onClickPolicy() {
        framework.showLoading();
        rpc.query({
            route: '/my/product/policy',
        }).then((partner) => {
            let popup = new dialog(this, {
                size: 'small',
                technical: false,
                title: _t('My PoS Policy'),
                $content: qweb.render('paylox.product.policy', partner),
            });
            popup.open().opened(() => {
                let $loading = popup.$modal.find('.loading');
                popup.$modal.addClass('payment-product-policy-popup');
                popup.$modal.find('.modal-body button').click(() => {
                    $loading.addClass('show');
                    rpc.query({
                        route: '/my/product/policy/send',
                    }).then((result) => {
                        if (result.error) {
                            this.displayNotification({
                                type: 'danger',
                                title: _t('Error'),
                                message: result.error,
                            });
                        } else {
                            this.displayNotification({
                                type: 'info',
                                title: _t('Success'),
                                message: _t('Policy has been sent succesfully.'),
                            });
                            popup.close();
                        }
                        $loading.removeClass('show');
                    }).guardedCatch(() => {
                        this.displayNotification({
                            type: 'danger',
                            title: _t('Error'),
                            message: _t('An error occured. Please contact with your system administrator.'),
                        });
                        $loading.removeClass('show');
                    });
                });
            });
            framework.hideLoading();
        }).guardedCatch(() => {
            this.displayNotification({
                type: 'danger',
                title: _t('Error'),
                message: _t('An error occured. Please contact with your system administrator.'),
            });
            framework.hideLoading();
        });
    },

    _onClickPay(ev) {
        $(document.body).addClass(['payment-form', this.validity > 0 ? 'payment-counter' : '']);
        $(ev.currentTarget).addClass('hide');
        this.product.back.$.removeClass('hide');
        this._startPayment();
    },

    _onClickBack(ev) {
        $(document.body).removeClass(['payment-form', this.validity > 0 ? 'payment-counter' : '']);
        $(ev.currentTarget).addClass('hide');
        this.product.pay.$.text(_t('Pay Now'));
        this.product.pay.$.removeClass('hide');
        this._stopPayment();
    },

    _startPayment() {
        this._saveOrder({ lock: true });
        if (this.validity > 0) {
            const $counter = this.product.counter.$.find('svg');
            const $progress = $counter.find('.progress');
            const counter = () => {
                if (this.timeout <= 0) {
                    this.product.pay.$.text(_t('Restart Payment'));
                    this.product.pay.$.removeClass('hide');
                    this._stopPayment();
                    return;
                }
    
                $counter.next().text(--this.timeout);
                $progress.css('stroke-dashoffset', 400 - 400 * this.timeout / this.validity);
            }

            this.timeout = this.validity + 1; counter();
            this.interval = setInterval(counter, 1000);
    
            $('[field="installment.table"] button').removeClass('disabled').removeAttr('disabled');
            $('[field="campaign.table"] button').removeClass('disabled').removeAttr('disabled');
            $('[field="payment.button"]').removeClass('disabled').removeAttr('disabled');
            window.dispatchEvent(new Event('payment-started'));
        }
    },

    _stopPayment() {
        if (this.validity > 0) {
            this.timeout = undefined;
            clearInterval(this.interval);
    
            $('[field="installment.table"] button').addClass('disabled').attr('disabled', 'disabled');
            $('[field="campaign.table"] button').addClass('disabled').attr('disabled', 'disabled');
            $('[field="payment.button"]').addClass('disabled').attr('disabled', 'disabled');
            window.dispatchEvent(new Event('payment-stopped'));
        }
        this._updateLines();
    },
});
