/** @odoo-module **/

import { Component } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class ApexEcrConsoleDialog extends Component {
    static template = "apex_ecr_integration.ApexEcrConsoleDialog";
    static components = { Dialog };

    constructor(env, props) {
        super(env, props);
        this.lines = props.lines || [];
    }

    addLine(text) {
        this.lines.push(text);
        this.render();
    }
}
