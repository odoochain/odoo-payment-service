/** @odoo-module alias=paylox.system.jewelry **/
'use strict';

import publicWidget from 'web.public.widget';
import core from 'web.core';
import rpc from 'web.rpc';
import dialog from 'web.Dialog';
import fields from 'paylox.fields';
import payloxPage from 'paylox.page';
import framework from 'paylox.framework';
import systemPage from 'paylox.system.page';
import { format } from 'paylox.tools';

const _t = core._t;
const Qweb = core.qweb;

publicWidget.registry.payloxSystemJewelry = systemPage.extend({
    selector: '.payment-jewelry #wrapwrap',
    xmlDependencies: ['/payment_jewelry/static/src/xml/page.xml'],

    init: function (parent, options) {
        this._super(parent, options);
        this.brands = {};
        this.jewelry = {
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
            items: new fields.element(),
            lines: new fields.element(),
            brand: new fields.element({
                events: [['click', this._onClickBrand]],
            }),
            pay: new fields.element({
            }),
        }
    },

    start: function () {
        return this._super.apply(this, arguments).then(() => {
            this._getBrands();
            this._updateLines();
            this._listenPrices();
        });
    },

    _getBrands: function () {
        let $brands = $('[field="jewelry.brands"]');
        $brands.each((i, e) => {
            let product = e.dataset.product;
            if (!(product in this.brands)) {
                this.brands[product] = [];
            }
            this.brands[product].push({
                id: parseInt(e.dataset.id),
                name: e.dataset.name,
                image: e.dataset.image,
            });
        });
        $brands.remove();
    },

    _listenPrices: function () {
        const events = new EventSource('/longpolling/prices');
        console.log('Price service is active.');
        events.onmessage = (event) => {
            let changed = false;
            let $prices = this.jewelry.price.$;
            let currency = [this.currency.position, this.currency.symbol, this.currency.decimal];
            for (let data of event.data.split('\n')) {
                let [code, price] = data.split(';'); price = parseFloat(price);
                let $price = $prices.filter(`[data-name="${code}"]`);
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
        let $qty = this.jewelry.qty.$.filter(`[data-id=${$price.data('id')}]`);
        let $amount = this.jewelry.amount.$.filter(`[data-id=${$price.data('id')}]`);

        let qty = parseFloat($qty.val());
        let price = parseFloat($price.data('value'));
        let value = qty * price;

        $amount.data('qty', qty);
        $amount.data('value', value);
        $amount.text(format.currency(value, this.currency.position, this.currency.symbol, this.currency.decimal));

        if (update) {
            this._updateLines();
        }
    },

    _updateLines() {
        let subtotal = 0;
        let products = {};
        let currency = [this.currency.position, this.currency.symbol, this.currency.decimal];
        this.jewelry.amount.$.each((i, e) => {
            let $e = $(e);
            let value = parseFloat($e.data('value'));
            if (value > 0) {
                let name = $e.data('name');
                let qty = parseFloat($e.data('qty'));
                let weight = parseFloat($e.data('weight'));
                if (!(name in products)) {
                    products[name] = { weight: 0, value: 0 };
                }
                products[name].weight += qty * weight;
                products[name].value += value;
                subtotal += value;
            }
        });
        this.jewelry.lines.html = Qweb.render('paylox.jewelry.lines', {
            format,
            currency: this.currency,
            products: Object.entries(products),
        });

        let fee = subtotal * this.jewelry.commission.value / 100;
        let total = subtotal + fee;
        this.jewelry.subtotal.text = format.currency(subtotal, ...currency);
        this.jewelry.fee.text = format.currency(fee, ...currency);
        this.jewelry.total.text = format.currency(total, ...currency);
    },

    _onClickBrand(ev) {
        let $button = $(ev.currentTarget);
        let $item = this.jewelry.items.$.filter(`[data-id=${ $button.data('id') }]`)

        let pid = parseInt($item.data('id'));
        let name = $item.data('name');
        let brands = this.brands[pid];
        let foreground = $item.data('foreground');
        let background = $item.data('background');
        let popup = new dialog(this, {
            size: 'small',
            title: _t('Choose a brand'),
            $content: Qweb.render('paylox.jewelry.brands', { brands, foreground, background }),
        });
        popup.open().opened(() => {
            popup.$modal.addClass('payment-jewelry-brand-popup');
            popup.$modal.find('.modal-header').attr('style', `color:${foreground} !important;background-color:${background} !important`);
            popup.$modal.find('.modal-footer button').attr('style', `color:${foreground} !important;background-color:${background} !important`);
            popup.$modal.find('button').click((e) => {
                let $btn = $(e.currentTarget);
                if (!('id' in $btn.data())) {
                    popup.close();
                    return;
                }

                let bid = parseInt($btn.data('id'));
                rpc.query({
                    model: 'product.template',
                    method: 'get_payment_variants',
                    context: {system: 'jewelry'},
                    args: [pid, 'weight', [bid]],
                }).then((weights) => {
                    let currency = this.currency;
                    let brand = brands.find(b => b.id === bid);
                    for (let w of weights) {
                        w.currency = this.currency;
                    }

                    let qtys = {};
                    $item.find('[field="jewelry.qty"]').each((i, e) => {
                        qtys[e.dataset.name] = e.value;
                    });

                    $item.html(Qweb.render('paylox.jewelry.items', {
                        brand,
                        format,
                        weights,
                        currency,
                        product: {
                            id: pid,
                            name: name,
                            foreground: foreground,
                            background: background,
                        },
                    }));

                    payloxPage.prototype._start.apply(this, [
                        'jewelry.price',
                        'jewelry.qty',
                        'jewelry.amount',
                        'jewelry.brand',
                    ]);

                    $item.find('[field="jewelry.qty"]').each((i, e) => {
                        if (e.dataset.name in qtys) {
                            e.value = qtys[e.dataset.name];
                        }
                        $(e).trigger('change');
                    });

                    popup.close();
                }).guardedCatch(() => {
                    this.displayNotification({
                        type: 'danger',
                        title: _t('Error'),
                        message: _t('An error occured. Please contact with your system administrator.'),
                    });
                });
            });
        });
    },

    _onChangeQty(ev) {
        let $qty = $(ev.currentTarget);
        let $price = this.jewelry.price.$.filter(`[data-id=${$qty.data('id')}]`);
        let $amount = this.jewelry.amount.$.filter(`[data-id=${$qty.data('id')}]`);

        let qty = parseFloat($qty.val());
        let price = parseFloat($price.data('value'));
        let value = qty * price;

        $amount.data('qty', qty);
        $amount.data('value', value);
        $amount.text(format.currency(value, this.currency.position, this.currency.symbol, this.currency.decimal));

        this._updateLines();
    },
});