/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { useService } from "@web/core/utils/hooks";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup();
        this.dialog = useService("dialog");
        this.notification = useService("notification");
    },

    async onClickApexECR() {
        const order = this.currentOrder;
        const amount = order.get_due();

        //  Validation: amount > 0
        if (amount <= 0) {
            this.dialog.add(AlertDialog, {
                title: "Invalid Amount",
                body: "No payment is due for this order.",
            });
            return;
        }

        //  Notify user that connection is starting
        this.notification.add(`Connecting to Apex ECR terminal...`, {
            title: "Apex ECR",
            type: "info",
        });

        try {
            const response = await fetch("/pos/apex_send", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: { amount },
                    id: Math.floor(Math.random() * 1000),
                }),
            });

            //  Parse JSON-RPC safely
            const data = await response.json();
            const result = data?.result;

            if (!result) throw new Error("Invalid response format from server.");

            //  SUCCESS
            if (result.success) {
                this.notification.add(result.message || "Transaction Approved.", {
                    title: "✅ Transaction Approved",
                    type: "success",
                });

                //  Add payment line automatically
                const method =
                    this.payment_methods_from_config.find(pm => pm.use_payment_terminal) ||
                    this.payment_methods_from_config[0];

                if (method) {
                    const line = order.add_paymentline(method);
                    if (line) {
                        line.set_amount(amount);
                    }
                }

                //  Notify success
                this.notification.add("Payment approved and processing validation...", {
                    title: "Payment Successful",
                    type: "success",
                });

                //  Automatically validate order
                await this.autoValidateOrder(order);

            } else {
                //  Failed / Cancelled
                this.dialog.add(AlertDialog, {
                    title: "Transaction Failed or Cancelled ❌",
                    body: result.message || "The terminal declined the transaction.",
                });

                this.notification.add(result.message || "Transaction failed.", {
                    title: "Apex ECR",
                    type: "warning",
                });
            }

        } catch (error) {
            console.error("Apex RPC Error:", error);
            this.dialog.add(AlertDialog, {
                title: " Connection Error",
                body: `Could not reach Apex terminal.\n${error.message || ""}`,
            });
            this.notification.add("Failed to connect to Apex ECR.", {
                title: "Network Error",
                type: "danger",
            });
        }
    },

    async autoValidateOrder(order) {
        try {
            await this.validateOrder(true); // instantly validate in POS

            
            this.notification.add("The order has been successfully validated and closed.", {
                title: "Order Validated",
                type: "success",
            });

        } catch (error) {
            console.error("Order validation error:", error);
            this.dialog.add(AlertDialog, {
                title: " Validation Error",
                body: "Payment succeeded, but order validation failed.",
            });

            this.notification.add("Order validation failed after payment.", {
                title: " Validation Error",
                type: "danger",
            });
        }
    },
});
