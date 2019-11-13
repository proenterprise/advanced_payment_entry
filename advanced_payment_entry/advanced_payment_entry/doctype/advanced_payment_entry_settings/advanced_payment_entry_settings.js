// Copyright (c) 2019, Proenterprise Ventures and contributors
// For license information, please see license.txt

frappe.ui.form.on('Advanced Payment Entry Settings', {
	refresh: function(frm) {

	},
	allocate_payment_entries: function(frm){
		frappe.msgprint("Payment Entry allocation has started for all unallocated payments")
		frappe.call({
			method: "advanced_payment_entry.advanced_payment_entry.ape_utilities.allocate_payment_entries",
			args: {},
			callback: function(r) {
				console.log(r);
			}
		});
	}
});
