#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
وحدة حسابات الفاتورة
"""

class InvoiceCalculator:
    """فئة لإجراء حسابات الفاتورة"""
    
    @staticmethod
    def calculate_item_total(price, quantity, discount_amount, tax_rate):
        """حساب إجمالي الصنف اعتماداً على خصم نقدي محدد لكل صنف"""
        quantity = quantity or 0
        discount_amount = discount_amount or 0
        if quantity <= 0:
            discount_per_unit = 0
            net_price_per_unit = max(price, 0)
            net_total = 0
        else:
            discount_per_unit = discount_amount / quantity
            net_price_per_unit = max(price - discount_per_unit, 0)
            net_total = net_price_per_unit * quantity
        
        tax_amount = net_total * tax_rate
        total = net_total + tax_amount
        
        return {
            'discount_per_unit': discount_per_unit,
            'discount_amount': discount_amount,
            'price_after_discount': net_price_per_unit,
            'tax_amount': tax_amount,
            'total': total
        }
    
    @staticmethod
    def calculate_invoice_totals(items, tax_rate):
        """حساب مجاميع الفاتورة"""
        subtotal_before = 0
        total_discount = 0
        
        for item in items:
            item_price = item.get('price', 0) or 0
            item_qty = item.get('quantity', 0) or 0
            discount_total = item.get('discount_amount') or 0
            discount_per_unit = item.get('discount_per_unit')
            
            if item_qty <= 0:
                discount_per_unit = 0
            else:
                if discount_per_unit is None:
                    discount_per_unit = discount_total / item_qty
            
            discount_total = discount_per_unit * item_qty
            
            # تأكد من تساوي القيم المخزنة مع المخرجات الحديثة
            item['discount_per_unit'] = discount_per_unit
            item['discount_amount'] = discount_total
            
            item_subtotal = item_price * item_qty
            subtotal_before += item_subtotal
            
            total_discount += discount_total
            
            net_price_per_unit = max(item_price - discount_per_unit, 0)
            net_total = net_price_per_unit * item_qty
            tax_for_item = net_total * tax_rate
            
            item['price_after_discount'] = net_price_per_unit
            item['tax_amount'] = tax_for_item
            item['total'] = net_total + tax_for_item
        
        subtotal = subtotal_before - total_discount
        tax = sum(item['tax_amount'] for item in items)
        total = subtotal + tax
        
        return {
            'subtotal_before_discount': subtotal_before,
            'total_discount': total_discount,
            'subtotal': subtotal,
            'tax': tax,
            'total': total
        }
