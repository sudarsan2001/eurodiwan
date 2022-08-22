

__version__ = '0.0.1'


import frappe
from erpnext.setup.utils import get_exchange_rate


def invoice_on_submit(self, method):
	if self.is_pos == 1 and not self.invoice_payment:
		return
	for i in self.invoice_payment:
		if i.paid_amount and self.is_return == 0:
			doc = frappe.new_doc("Payment Entry")
			doc.posting_date = self.posting_date
			doc.payment_type = "Receive"
			#doc.naming_series = "ACC-RC-.YYYY.-" #name[self.location]
			doc.sales_invoice = self.name
			doc.mode_of_payment = i.mode_of_payment
			doc.party_type = "Customer"
			doc.party = self.customer
			doc.paid_from = frappe.db.get_value("Company", self.company, 'default_receivable_account')
			doc.paid_to = frappe.db.get_value("Mode of Payment Account", {"parent":i.mode_of_payment}, "default_account")
			doc.paid_amount = i.paid_amount
			doc.received_amount = i.paid_amount
			doc.reference_no = i.reference_no
			doc.reference_date = i.reference_date
			doc.setup_party_account_field()
			doc.set_missing_values()
			doc.set_exchange_rate()
			doc.save(ignore_permissions=True)
			doc.append("references",{
				"reference_doctype": "Sales Invoice",
				"parentfield": "references",
				"parenttype": "Payment Entry",
				"parent": doc.name,
				"reference_name": self.name,
				"total_amount": self.grand_total,
				"outstanding_amount": self.outstanding_amount,
				"allocated_amount": i.paid_amount
			})
			doc.save(ignore_permissions=True)
			doc.submit()

def invoice_on_cancel(self, method):
	for i in frappe.db.get_list("Payment Entry", {"sales_invoice": self.name, "docstatus":1}):
		pe = frappe.get_doc("Payment Entry", i.name)
		pe.cancel()
