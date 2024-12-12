frappe.ui.form.on('Customer', {
    refresh: function(frm) {
        frm.add_custom_button(__('Send Balance Qualification Link'), function() {
            frappe.call({
                method: 'balance_integration.api.qualification.send_qualification_link',
                args: {
                    customer: frm.doc.name
                },
                callback: function(r) {
                    if (!r.exc) {
                        frappe.show_alert({
                            message: __('Qualification link sent successfully'),
                            indicator: 'green'
                        });
                    }
                }
            });
        }, __('Balance'));
    }
});