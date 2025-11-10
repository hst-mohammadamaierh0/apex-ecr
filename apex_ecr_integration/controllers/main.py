# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import requests
import xml.etree.ElementTree as ET
from requests.exceptions import RequestException, SSLError, Timeout, ConnectionError as ReqConnErr
import time
import logging

_logger = logging.getLogger(__name__)

APPROVED_CODES = {"000", "00", "0", "APPROVED"}  # recognized success codes


class ApexECRController(http.Controller):

    @http.route('/pos/apex_send', type='json', auth='user', csrf=False)
    def send_to_ecr(self, amount):
        """
        Handles Apex ECR Sale transaction.
        If test mode is enabled in POS config, simulates approval.
        Otherwise, performs a live SOAP request to the ECR endpoint.
        """
        t0 = time.time()

        # Get active POS config
        pos_config = request.env['pos.config'].sudo().search(
            [('apex_ecr_enabled', '=', True)], limit=1
        )
        if not pos_config:
            return {
                'success': False,
                'source': 'odoo',
                'message': 'Apex ECR is not enabled for this POS configuration.',
            }

        merchant_key = (pos_config.apex_secure_key or '').strip()
        mid = (pos_config.apex_mid or '').strip()
        tid = (pos_config.apex_tid or '').strip()
        test_mode = getattr(pos_config, "apex_ecr_test_mode", False)
        currency_code = "400"  # JOD

        # 2️ TEST MODE — always simulate approval
        if test_mode:
            _logger.info("[ApexECR][TEST] Simulating approved transaction for amount %.3f", float(amount))
            time.sleep(1.0)
            return {
                'success': True,
                'message': (
                    " Transaction Approved (Test Mode)\n"
                    f"Amount: {float(amount):.3f} JOD\n"
                    f"Auth Code: 999999\n"
                    f"Card: ****1234\n"
                    f"Message: Simulated Approval (No ECR Call)"
                )
            }

        # 3️ LIVE MODE — send real SOAP call
        url = "https://188.247.84.45:6610/EcrWebInterface/EcrComInterface.svc"
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/IEcrComInterface/Sale",
        }

        try:
            amt = float(amount)
        except Exception:
            return {'success': False, 'source': 'odoo', 'message': f'Invalid amount: {amount}'}

        payload = f"""\
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:tem="http://tempuri.org/"
                  xmlns:ns="http://schemas.datacontract.org/2004/07/">
  <soapenv:Header/>
  <soapenv:Body>
    <tem:Sale>
      <tem:webReq>
        <ns:Config>
          <ns:EcrCurrencyCode>{currency_code}</ns:EcrCurrencyCode>
          <ns:MerchantSecureKey>{merchant_key}</ns:MerchantSecureKey>
          <ns:Mid>{mid}</ns:Mid>
          <ns:Tid>{tid}</ns:Tid>
        </ns:Config>
        <ns:EcrAmount>{amt:.3f}</ns:EcrAmount>
        <ns:Printer>
          <ns:PrinterWidth>1</ns:PrinterWidth>
          <ns:ReceiptNote>3</ns:ReceiptNote>
        </ns:Printer>
      </tem:webReq>
    </tem:Sale>
  </soapenv:Body>
</soapenv:Envelope>""".strip()

        # 4️ Send request to real ECR
        try:
            _logger.info("[ApexECR] --> POST %s | MID=%s TID=%s Amount=%.3f", url, mid, tid, amt)
            resp = requests.post(url, data=payload, headers=headers, timeout=60, verify=False)
            rtt_ms = int((time.time() - t0) * 1000)
            _logger.info("[ApexECR] <-- %s in %d ms | len=%d", resp.status_code, rtt_ms, len(resp.text))
            resp.raise_for_status()
        except (Timeout, SSLError, ReqConnErr, RequestException) as e:
            _logger.exception("[ApexECR] HTTP error")
            return {
                'success': False,
                'source': 'http',
                'message': f'Connection error: {e}',
                'rtt_ms': int((time.time() - t0) * 1000),
            }

        # 5️ Parse SOAP XML response
        try:
            tree = ET.fromstring(resp.text)
            ns = {
                "s": "http://schemas.xmlsoap.org/soap/envelope/",
                "tem": "http://tempuri.org/",
                "a": "http://schemas.datacontract.org/2004/07/"
            }

            sale_result = tree.find(".//tem:SaleResult", ns) or tree.find(".//SaleResult", ns)

            def get_text(tag):
                node = sale_result.find(f".//a:{tag}", ns) if sale_result is not None else tree.find(f".//a:{tag}", ns)
                return node.text.strip() if node is not None and node.text else None

            result_code = get_text("ResultCode")
            result_msg = get_text("ResultMessage")
            auth_code = get_text("PosAuthCode")
            pos_amount = get_text("PosAmount")
            card_number = get_text("CardNumber")

            _logger.info("[ApexECR] Parsed XML: Code=%s, Auth=%s, Msg=%s, Amount=%s",
                         result_code, auth_code, result_msg, pos_amount)

            #  Success condition
            if auth_code or (result_code and result_code.strip() in APPROVED_CODES):
                return {
                    'success': True,
                    'message': (
                        "✅ Transaction Approved\n"
                        f"Amount: {pos_amount or amount} JOD\n"
                        f"Auth Code: {auth_code or 'N/A'}\n"
                        f"Card: {card_number or 'N/A'}\n"
                        f"Message: {result_msg or 'Approved'}"
                    )
                }

            #  Declined or cancelled
            return {
                'success': False,
                'message': (
                    "❌ Transaction Cancelled or Declined\n"
                    f"Code: {result_code or 'N/A'}\n"
                    f"Msg: {result_msg or 'No message'}"
                )
            }

        except ET.ParseError as e:
            _logger.warning("Failed to parse Apex ECR response: %s", e)
            return {
                'success': False,
                'message': f'Unexpected ECR response format: {resp.text[:500]}'
            }
