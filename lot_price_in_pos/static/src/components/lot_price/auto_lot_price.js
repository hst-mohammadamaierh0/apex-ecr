/** @odoo-module alias="lot_price_in_pos.auto_lot_price" **/

console.log(" Lot Price Module Loaded");

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";

patch(ProductScreen, {

    setup() {
        super.setup();
        this.notification = useService("notification");
        console.log(" ProductScreen patched successfully!");
    },

    async _onClickProduct(event) {
        console.log(" Product clicked:", event.detail);

        const product = event.detail;
        const res = await super._onClickProduct(event);

        const order = this.pos.get_order();
        const line = order?.get_last_orderline();

        if (!line) {
            console.log(" No order line created");
            return res;
        }

        console.log(" Order line:", line);

        // Fetch product lots
        const lots = this.pos.db.get_product_lots(product.id);
        console.log(" Fetched Lots:", lots);

        if (!lots?.length) {
            console.log(" No lots found");
            return res;
        }

        const lot = lots[0];
        console.log(" Selected lot:", lot);

        const price = lot.lot_price || 0;

        line.set_lot_name(lot.lot_name);
        line.set_unit_price(price);

        this.notification.add(`Lot Price Applied: ${price}`, {
            title: "Lot Price Applied",
            type: "info",
        });

        return res;
    },
});
