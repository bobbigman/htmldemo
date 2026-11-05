# -*- coding: utf-8 -*-
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

def U(*codes):
    return "".join(chr(c) for c in codes)

# Chinese via codepoints to keep this source ASCII-only
REQ_MAP = [
    ("BillHead", "FID", "subject.pid / data.selected[].requisitionId", "json", U(0x901A,0x77E5,0x8EAB,0x4EFD) + ";" + U(0x4E0D,0x662F,0x5355,0x53F7)),
    ("FEntity", "FEntryID", "data.selected[].entryId", "json", U(0x660E,0x7EC6,0x5185,0x7801)),
    ("", "(" + U(0x91D1,0x8776,0x62FC) + ")", "data.title", "json", U(0x8BE2,0x4EF7,0x6807,0x9898)),
    ("BillHead", "FBillNo", U(0x7533,0x8BF7,0x5355,0x53F7), "read", U(0x4E1A,0x52A1,0x5355,0x53F7)),
    ("BillHead", "FDocumentStatus", U(0x5355,0x636E,0x72B6,0x6001), "read", "A/B/C/D/Z"),
    ("BillHead", "FApplicationDate", U(0x7533,0x8BF7,0x65E5,0x671F), "read", ""),
    ("BillHead", "FBillTypeID", U(0x5355,0x636E,0x7C7B,0x578B), "read", ""),
    ("BillHead", "FApplicationOrgId", U(0x7533,0x8BF7,0x7EC4,0x7EC7), "read", ""),
    ("BillHead", "FApplicationDeptId", U(0x7533,0x8BF7,0x90E8,0x95E8), "read", ""),
    ("BillHead", "FApplicantId", U(0x7533,0x8BF7,0x4EBA), "read", ""),
    ("BillHead", "FCurrencyId", U(0x5E01,0x522B), "read", ""),
    ("BillHead", "FCloseStatus", U(0x5173,0x95ED,0x72B6,0x6001), "read", ""),
    ("BillHead", "FCancelStatus", U(0x4F5C,0x5E9F,0x72B6,0x6001), "read", ""),
    ("BillHead", "FApproverId", U(0x5BA1,0x6838,0x4EBA), "read", ""),
    ("BillHead", "FApproveDate", U(0x5BA1,0x6838,0x65E5,0x671F), "read", ""),
    ("BillHead", "FNote", U(0x5907,0x6CE8), "read", ""),
    ("FEntity", "FMaterialId", U(0x7269,0x6599), "read", U(0x7269,0x6599,0x7F16,0x7801)),
    ("FEntity", "FUnitId", U(0x7533,0x8BF7,0x5355,0x4F4D), "read", ""),
    ("FEntity", "FReqQty", U(0x7533,0x8BF7,0x6570,0x91CF), "read", U(0x7269,0x6599,0x6570,0x91CF) + "(" + U(0x7533,0x8BF7) + ")"),
    ("FEntity", "FApproveQty", U(0x6279,0x51C6,0x6570,0x91CF), "read", U(0x7269,0x6599,0x6570,0x91CF) + "(" + U(0x6279,0x51C6) + ")"),
    ("FEntity", "FRemainQty", U(0x5269,0x4F59,0x6570,0x91CF), "read", ""),
    ("FEntity", "FOrderQty", U(0x8BA2,0x5355,0x6570,0x91CF), "read", ""),
    ("FEntity", "FSuggestSupplierId", U(0x5EFA,0x8BAE,0x4F9B,0x5E94,0x5546), "read", ""),
    ("FEntity", "FPurchaseOrgId", U(0x91C7,0x8D2D,0x7EC4,0x7EC7), "read", ""),
    ("FEntity", "FPurchaseDeptId", U(0x91C7,0x8D2D,0x90E8,0x95E8), "read", ""),
    ("FEntity", "FPurchaserId", U(0x91C7,0x8D2D,0x5458), "read", ""),
    ("FEntity", "FArrivalDate", U(0x5230,0x8D27,0x65E5,0x671F), "read", ""),
    ("FEntity", "FEntryNote", U(0x660E,0x7EC6,0x5907,0x6CE8), "read", ""),
    ("FEntity", "FMRPCloseStatus", U(0x4E1A,0x52A1,0x5173,0x95ED), "read", ""),
    ("FEntity", "FEvaluatePrice", U(0x4F30,0x4EF7), "read", U(0x53EF,0x9009)),
]

PO_MAP = [
    ("BillHead", "FID", "subject.pid / data.orderIds[]", "json", U(0x901A,0x77E5,0x8EAB,0x4EFD)),
    ("", "(" + U(0x65E0) + ")", "data.requestId", "json", U(0x5EFA,0x8BAE,0x7701,0x7565)),
    ("BillHead", "FBillNo", U(0x91C7,0x8D2D,0x8BA2,0x5355,0x53F7), "read", U(0x4E1A,0x52A1,0x5355,0x53F7)),
    ("BillHead", "FDocumentStatus", U(0x5355,0x636E,0x72B6,0x6001), "read", ""),
    ("BillHead", "FDate", U(0x91C7,0x8D2D,0x65E5,0x671F), "read", ""),
    ("BillHead", "FBillTypeID", U(0x5355,0x636E,0x7C7B,0x578B), "read", ""),
    ("BillHead", "FPurchaseOrgId", U(0x91C7,0x8D2D,0x7EC4,0x7EC7), "read", ""),
    ("BillHead", "FPurchaseDeptId", U(0x91C7,0x8D2D,0x90E8,0x95E8), "read", ""),
    ("BillHead", "FPurchaserId", U(0x91C7,0x8D2D,0x5458), "read", ""),
    ("BillHead", "FSupplierId", U(0x4F9B,0x5E94,0x5546), "read", ""),
    ("BillHead", "FCloseStatus", U(0x5173,0x95ED,0x72B6,0x6001), "read", ""),
    ("BillHead", "FCancelStatus", U(0x4F5C,0x5E9F,0x72B6,0x6001), "read", ""),
    ("BillHead", "FApproverId", U(0x5BA1,0x6838,0x4EBA), "read", ""),
    ("BillHead", "FApproveDate", U(0x5BA1,0x6838,0x65E5,0x671F), "read", ""),
    ("FPOOrderEntry", "FEntryID", "entryIds (A-PO-DEL)", "json-del", U(0x5220,0x9664,0x660E,0x7EC6,0x65F6)),
    ("FPOOrderEntry", "FMaterialId", U(0x7269,0x6599), "read", ""),
    ("FPOOrderEntry", "FUnitId", U(0x91C7,0x8D2D,0x5355,0x4F4D), "read", ""),
    ("FPOOrderEntry", "FQty", U(0x91C7,0x8D2D,0x6570,0x91CF), "read", U(0x7269,0x6599,0x6570,0x91CF) + "(" + U(0x8BA2,0x5355) + ")"),
    ("FPOOrderEntry", "FPrice", U(0x5355,0x4EF7), "read", ""),
    ("FPOOrderEntry", "FTaxPrice", U(0x542B,0x7A0E,0x5355,0x4EF7), "read", ""),
    ("FPOOrderEntry", "FEntryTaxRate", U(0x7A0E,0x7387) + "%", "read", ""),
    ("FPOOrderEntry", "FEntryTaxAmount", U(0x7A0E,0x989D), "read", ""),
    ("FPOOrderEntry", "FDeliveryDate", U(0x4EA4,0x8D27,0x65E5,0x671F), "read", ""),
    ("FPOOrderEntry", "FRemainReceiveQty", U(0x5269,0x4F59,0x6536,0x6599,0x6570,0x91CF), "read", ""),
    ("FPOOrderEntry", "FStockInQty", U(0x7D2F,0x8BA1,0x5165,0x5E93,0x6570,0x91CF), "read", ""),
    ("FPOOrderEntry", "FReceiveQty", U(0x7D2F,0x8BA1,0x6536,0x6599,0x6570,0x91CF), "read", ""),
    ("FPOOrderEntry", "FEntryNote", U(0x660E,0x7EC6,0x5907,0x6CE8), "read", ""),
    ("FPOOrderEntry", "FMRPCloseStatus", U(0x4E1A,0x52A1,0x5173,0x95ED), "read", ""),
]


def load(form_id):
    return json.loads((DATA / ("fields_%s.json" % form_id)).read_text(encoding="utf-8"))


def index_fields(data):
    return {(f["entityKey"], f["key"]): f for f in data["fields"]}


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def channel_tag(ch):
    if ch == "json":
        return '<span class="tag sys">' + U(0x5199,0x5165,0x4E8B,0x4EF6) + " JSON</span>"
    if ch == "json-del":
        return '<span class="tag warn">' + U(0x4EC5,0x5220,0x9664,0x901A,0x77E5) + " JSON</span>"
    return '<span class="tag on">AMOS ' + U(0x8BFB,0x91D1,0x8776,0x8D26,0x5957) + "</span>"


def mapping_table(title, rows, idx):
    lines = [
        '<div class="section-title">%s</div>' % esc(title),
        '<div class="panel"><table class="grid"><thead><tr>',
        "<th>#</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th>" % (
            U(0x5230,0x8FBE,0x65B9,0x5F0F), U(0x91D1,0x8776,0x5B9E,0x4F53), U(0x91D1,0x8776) + " Key",
            U(0x91D1,0x8776,0x540D,0x79F0), U(0x7B2C,0x4E09,0x65B9,0x4FA7), U(0x8BF4,0x660E), U(0x4F1A,0x8BAE,0x7ED3,0x8BBA),
        ),
        "</tr></thead><tbody>",
    ]
    n = 0
    for ek, key, amos, ch, note in rows:
        n += 1
        meta = idx.get((ek, key)) if ek else None
        if meta:
            name = meta.get("name") or ""
            elem = meta.get("elem") or ""
            entity_name = meta.get("entityName") or ek
        else:
            name = "(" + U(0x975E) + " XML)" if not ek else "(XML " + U(0x672A,0x627E,0x5230) + ")"
            elem = ""
            entity_name = ek or "-"
        kd_key = key if key else "-"
        path = ((ek + ".") if ek else "") + (key or amos)
        elem_html = ("<br><span class='tag pend'>%s</span>" % esc(elem)) if elem else ""
        lines.append(
            '<tr data-field-row data-path="%s" data-type="%s" data-req="%s">'
            "<td>%d</td><td>%s</td>"
            "<td>%s<br><code>%s</code></td>"
            "<td><code>%s</code>%s</td>"
            "<td>%s</td><td><code>%s</code></td><td>%s</td>"
            "<td><select><option>%s</option><option>%s</option><option>%s</option></select></td>"
            "</tr>"
            % (
                esc(path), ch, "Y" if ch.startswith("json") else "N",
                n, channel_tag(ch),
                esc(entity_name), esc(ek or "-"),
                esc(kd_key), elem_html,
                esc(name), esc(amos), esc(note),
                U(0x5F85,0x5B9A), U(0x7EB3,0x5165), U(0x4E0D,0x7EB3,0x5165),
            )
        )
    lines.append("</tbody></table></div>")
    return "\n".join(lines)


EXPLAIN = (
    '<div class="tip warn"><b>'
    + U(0x300C) + "AMOS " + U(0x8BFB,0x8D26,0x5957,0x300D,0x662F,0x4EC0,0x4E48,0x610F,0x601D,0xFF1F)
    + U(0x8981,0x4E0D,0x8981,0x6211,0x4EEC,0x628A,0x8FD9,0x4E9B,0x5B57,0x6BB5,0x5199,0x8FDB) + " JSON?</b><br>"
    + "<b>" + U(0x4E0D,0x9700,0x8981,0x3002) + "</b>"
    + U(0x91D1,0x8776,0x8C03,0x7B2C,0x4E09,0x65B9,0x65F6,0xFF0C,0x4E8B,0x4EF6) + " JSON <b>"
    + U(0x53EA,0x4F20,0x8EAB,0x4EFD) + "</b>"
    + U(0xFF08,0x5982) + " FID" + U(0x3001,0x660E,0x7EC6) + " EntryId" + U(0x3001) + "title" + U(0xFF09,0x3002) + "<br>"
    + U(0x7269,0x6599,0x3001,0x6570,0x91CF,0x3001,0x72B6,0x6001,0x3001,0x4F9B,0x5E94,0x5546)
    + U(0x7B49,0x4E1A,0x52A1,0x5B57,0x6BB5,0xFF0C,0x7531) + " <b>AMOS "
    + U(0x7528,0x4E8B,0x5148,0x914D,0x7F6E,0x597D,0x7684,0x91D1,0x8776,0x8FDE,0x63A5) + "</b>"
    + U(0xFF08) + "WebAPI/" + U(0x8D26,0x5957,0x8D26,0x53F7,0xFF09,0x81EA,0x5DF1,0x53BB,0x91D1,0x8776,0x91CC,0x8BFB,0x6700,0x65B0,0x5355,0x636E,0x3002) + "<br>"
    + U(0x56E0,0x6B64,0x4E0B,0x8868,0x5206,0x4E24,0x8272,0xFF1A)
    + '<span class="tag sys">' + U(0x5199,0x5165,0x4E8B,0x4EF6) + " JSON</span>="
    + U(0x6211,0x4EEC,0x8981,0x7EC4,0x7684,0x62A5,0x6587,0xFF1B)
    + '<span class="tag on">AMOS ' + U(0x8BFB,0x91D1,0x8776,0x8D26,0x5957) + "</span>="
    + U(0x53CC,0x65B9,0x8981,0x5BF9,0x9F50,0x7684,0x91D1,0x8776,0x5B57,0x6BB5,0xFF0C)
    + U(0x91D1,0x8776,0x4E0D,0x7528,0x585E,0x8FDB) + " POST JSON"
    + "</div>"
)

SHELL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="common.css">
</head>
<body {body_attr}>
<div class="page">
{body}
</div>
<script src="_ui.js"></script>
</body>
</html>
"""


def write(name, title, body, body_attr=""):
    # Force UTF-8 no BOM
    path = ROOT / name
    path.write_text(SHELL.format(title=title, body=body, body_attr=body_attr), encoding="utf-8")
    print("wrote", name)


def main():
    req = load("PUR_Requisition")
    po = load("PUR_PurchaseOrder")
    req_idx = index_fields(req)
    po_idx = index_fields(po)

    tip_req = (
        '<div class="tip">' + U(0x5B57,0x6BB5,0x6765,0x6E90) + ":<code>docs/kingdeeXml/"
        + U(0x91C7,0x8D2D,0x7533,0x8BF7,0x5355) + ".xml</code>(" + str(req["fieldCount"]) + ") + A-003. "
        + U(0x672C,0x9875,0x662F) + "<strong>" + U(0x5B57,0x6BB5,0x6620,0x5C04,0x8868) + "</strong></div>"
    )
    body = tip_req + EXPLAIN + (
        '<div class="toolbar">'
        '<button class="btn p" type="button" onclick="act(\'' + U(0x540C,0x6B65,0x62A5,0x6587) + '\')">'
        + U(0x67E5,0x770B) + " A-003 JSON</button>"
        '<button class="btn" type="button" onclick="act(\'' + U(0x5BFC,0x51FA,0x4F1A,0x8BAE,0x786E,0x8BA4) + '\')">'
        + U(0x5BFC,0x51FA,0x4F1A,0x8BAE,0x786E,0x8BA4) + "</button>"
        '<span class="tag sys">JSON ' + U(0x5F88,0x77ED) + " / " + U(0x4E1A,0x52A1,0x5B57,0x6BB5,0x9760,0x8BFB,0x8D26,0x5957) + "</span></div>"
    ) + mapping_table(U(0x91C7,0x8D2D,0x7533,0x8BF7) + " A-003 " + U(0x5B57,0x6BB5,0x6620,0x5C04,0x8868), REQ_MAP, req_idx) + (
        '<div class="section-title">A-003 JSON ' + U(0x6837,0x4F8B) + " (" + U(0x4EC5,0x8EAB,0x4EFD) + ")</div>"
        '<div class="mono">{\n  "id": "kd-inquiry-example-001",\n  "type": "inquiry.requested",\n'
        '  "schemaVersion": 1,\n  "occurredAt": "2026-11-04T02:00:00Z",\n'
        '  "subject": {"type": "purchase-requisition", "pid": "101"},\n  "sequence": 1,\n'
        '  "data": {\n    "title": "' + U(0x91C7,0x8D2D,0x7533,0x8BF7,0x9009,0x4E2D,0x660E,0x7EC6,0x8BE2,0x4EF7) + '",\n'
        '    "selected": [{"requisitionId": "101", "entryId": "11"}]\n  }\n}</div>'
        '<div class="tip">' + U(0x6CE8,0x610F) + ':<strong>' + U(0x6CA1,0x6709) + "</strong> FBillNo / FDocumentStatus / FReqQty. "
        + U(0x8FD9,0x4E9B,0x5728,0x4E0A,0x8868) + " = AMOS " + U(0x8BFB,0x8D26,0x5957) + "</div>"
    )
    write("21_" + U(0x91C7,0x8D2D,0x7533,0x8BF7) + "_" + U(0x540C,0x6B65,0x5B57,0x6BB5) + ".html",
          U(0x91C7,0x8D2D,0x7533,0x8BF7) + " A-003", body, 'data-api="A-003"')

    tip_po = (
        '<div class="tip">' + U(0x5B57,0x6BB5,0x6765,0x6E90) + ":<code>docs/kingdeeXml/"
        + U(0x91C7,0x8D2D,0x8BA2,0x5355) + ".xml</code>(" + str(po["fieldCount"]) + ") + A-007. "
        + U(0x672C,0x9875,0x662F) + "<strong>" + U(0x5B57,0x6BB5,0x6620,0x5C04,0x8868) + "</strong></div>"
    )
    body = tip_po + EXPLAIN + (
        '<div class="toolbar">'
        '<button class="btn p" type="button" onclick="act(\'' + U(0x540C,0x6B65,0x62A5,0x6587) + '\')">'
        + U(0x67E5,0x770B) + " A-007 JSON</button>"
        '<button class="btn" type="button" onclick="act(\'' + U(0x5BFC,0x51FA,0x4F1A,0x8BAE,0x786E,0x8BA4) + '\')">'
        + U(0x5BFC,0x51FA,0x4F1A,0x8BAE,0x786E,0x8BA4) + "</button></div>"
    ) + mapping_table(U(0x91C7,0x8D2D,0x8BA2,0x5355) + " A-007 " + U(0x5B57,0x6BB5,0x6620,0x5C04,0x8868), PO_MAP, po_idx) + (
        '<div class="section-title">A-007 JSON ' + U(0x6837,0x4F8B) + " (" + U(0x4EC5,0x8EAB,0x4EFD) + ")</div>"
        '<div class="mono">{\n  "id": "kd-order-sync-example-001",\n  "type": "order.published",\n'
        '  "schemaVersion": 1,\n  "occurredAt": "2026-11-04T03:00:00Z",\n'
        '  "subject": {"type": "purchase-order", "pid": "300001"},\n  "sequence": 1,\n'
        '  "data": {"orderIds": ["300001"]}\n}</div>'
        '<div class="tip">' + U(0x6CE8,0x610F) + ':<strong>' + U(0x6CA1,0x6709) + "</strong> FBillNo / FSupplierId / FQty / FTaxPrice</div>"
    )
    write("31_" + U(0x91C7,0x8D2D,0x8BA2,0x5355) + "_" + U(0x540C,0x6B65,0x5B57,0x6BB5) + ".html",
          U(0x91C7,0x8D2D,0x8BA2,0x5355) + " A-007", body, 'data-api="A-007"')

    body = (
        '<div class="tip">' + U(0x4E24,0x5957,0x901A,0x9053) + ": JSON vs AMOS " + U(0x8BFB,0x8D26,0x5957) + "</div>"
        + EXPLAIN
        + '<div class="section-title">' + U(0x901A,0x9053,0x5BF9,0x6BD4) + "</div>"
        + '<div class="panel"><table class="grid"><thead><tr><th>' + U(0x901A,0x9053) + "</th><th>"
        + U(0x8C01,0x505A) + "</th><th>" + U(0x4F20,0x4EC0,0x4E48) + "</th><th>" + U(0x4F8B,0x5B50) + "</th></tr></thead><tbody>"
        + '<tr><td><span class="tag sys">JSON</span></td><td>' + U(0x91D1,0x8776) + " POST</td><td>"
        + U(0x8EAB,0x4EFD) + '</td><td><code>FID</code>/<code>FEntryID</code>/<code>orderIds</code></td></tr>'
        + '<tr><td><span class="tag on">AMOS ' + U(0x8BFB,0x8D26,0x5957) + "</span></td><td>AMOS</td><td>"
        + U(0x4E1A,0x52A1,0x5B57,0x6BB5) + '</td><td><code>FBillNo</code>/<code>FDocumentStatus</code>/'
        + U(0x7269,0x6599,0x6570,0x91CF) + "</td></tr></tbody></table></div>"
        + '<div class="confirm-bar"><div class="sum">' + U(0x4E1A,0x52A1,0x5B57,0x6BB5,0x6620,0x5C04,0x8BF7,0x5230,0x7533,0x8BF7,0x002F,0x8BA2,0x5355,0x9875)
        + '</div>'
        + '<button class="btn" type="button" onclick="parent.postMessage({mod:\'req\',page:\''
        + U(0x540C,0x6B65,0x5B57,0x6BB5) + " A-003'},'*')\">" + U(0x7533,0x8BF7,0x6620,0x5C04) + "</button>"
        + '<button class="btn" type="button" onclick="parent.postMessage({mod:\'po\',page:\''
        + U(0x540C,0x6B65,0x5B57,0x6BB5) + " A-007'},'*')\">" + U(0x8BA2,0x5355,0x6620,0x5C04) + "</button></div>"
    )
    write("40_" + U(0x516C,0x5171,0x8BF7,0x6C42,0x5B57,0x6BB5) + ".html", "JSON vs " + U(0x8BFB,0x8D26,0x5957), body)
    print("done")


if __name__ == "__main__":
    main()
