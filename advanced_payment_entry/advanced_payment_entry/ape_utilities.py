# -*- coding: utf-8 -*-
# Copyright (c) 2019, Proenterprise Ventures and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import datetime, frappe, redis, ast
from frappe import msgprint, _
from frappe.utils import add_months
from erpnext.accounts.doctype.payment_entry.payment_entry import get_outstanding_reference_documents

class ApeUtilities():
    pass

@frappe.whitelist()
def allocate_payment_entries():
    pe_sett = frappe.get_doc("Advanced Payment Entry Settings", "Advanced Payment Entry Settings")
    if pe_sett.enable_automated_allocation == 1:
        pes = frappe.get_list("Payment Entry", filters=[["docstatus", "=", 1], ["unallocated_amount", ">", 0], ["payment_type", "=", "Receive"]], fields=["name", "unallocated_amount", "total_allocated_amount"], order_by='posting_date')
        for e in pes:
            dc = frappe.get_doc("Payment Entry", e.name)
            args = frappe._dict({
                "posting_date": dc.posting_date,
                "company": dc.company,
                "party_type": dc.party_type,
                "payment_type": dc.payment_type,
                "party": dc.party,
                "party_account": dc.paid_from,
                "from_posting_date":add_months(dc.posting_date, -12),
                "to_posting_date":add_months(dc.posting_date, 12),
                "allocate_payment_amount": dc.unallocated_amount,
            })
            list_of_unpaid_trans = get_outstanding_reference_documents(args)
            update_ref_flag = False
            if len(list_of_unpaid_trans) > 0:
                balance = dc.unallocated_amount
                for f in list_of_unpaid_trans:
                    balance -= f.outstanding_amount
                    if balance >= 0:
                        dc.append("references", {
                            "reference_doctype": f.voucher_type,
                            "reference_name": f.voucher_no,
                            "due_date": f.due_date,
                            "total_amount": f.invoice_amount,
                            "outstanding_amount": f.outstanding_amount,
                            "allocated_amount": f.outstanding_amount,
                            "exchange_rate": f.exchange_rate
                        })
                        update_ref_flag = True
                    elif balance < 0 and f.outstanding_amount + balance > 0:
                        dc.append("references", {
                            "reference_doctype": f.voucher_type,
                            "reference_name": f.voucher_no,
                            "due_date": f.due_date,
                            "total_amount": f.invoice_amount,
                            "outstanding_amount": f.outstanding_amount,
                            "allocated_amount": f.outstanding_amount + balance,
                            "exchange_rate": f.exchange_rate
                        })
                        update_ref_flag = True
                if update_ref_flag:
                    dc.flags.ignore_validate_update_after_submit = True
                    dc.validate()
                    dc.submit() 
                    dc.on_submit()
                    dc.setup_party_account_field()
                    if dc.difference_amount:
                        frappe.throw(_("Difference Amount must be zero"))
                    dc.make_gl_entries(cancel=1)
                    dc.make_gl_entries()
                    dc.update_outstanding_amounts()
                    dc.update_advance_paid()
                    dc.update_expense_claim()
                    dc.set_status()
                    frappe.db.commit()
            else:
                frappe.msgprint("No outstanding invoices for {0}".format(dc.party))
            # break
    else:
        return "Automated allocation is disabled"
    return True
