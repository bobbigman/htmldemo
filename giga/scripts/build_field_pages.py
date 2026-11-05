# -*- coding: utf-8 -*-
"""从 docs/kingdeeXml 抽出的字段 JSON，生成演示页用的字段对照 HTML 片段。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS_XML = ROOT.parent / "docs" / "kingdeeXml"

# AMOS 通知身份字段（第三方文档）
AMOS_A003 = [
    ("subject.pid", "string", "是", "申请单 FID，须在 selected 内"),
    ("data.title", "string", "是", "询价标题，最长200"),
    ("data.selected[].requisitionId", "string", "是", "申请单 FID"),
    ("data.selected[].entryId", "string", "是", "明细 FEntity_FEntryID"),
]
AMOS_A007 = [
    ("subject.pid", "string", "是", "订单 FID，须在 orderIds 内"),
    ("data.orderIds[]", "string[]", "是", "1～100 个订单 FID"),
    ("data.requestId", "string", "否", "建议省略；若有须等于外层 id"),
]
AMOS_COMMON = [
    ("id", "string", "是", "通知编号"),
    ("type", "string", "是", "固定事件名"),
    ("schemaVersion", "integer", "是", "固定 1"),
    ("occurredAt", "string", "是", "ISO8601"),
    ("subject.type", "string", "是", "purchase-requisition / purchase-order"),
    ("subject.pid", "string", "是", "金蝶 FID"),
    ("sequence", "integer", "是", "通知序号"),
    ("data", "object", "是", "业务参数"),
]

# 金蝶单据中，AMOS 读账套时常用的业务字段（从 XML 名中筛选）
REQ_READ_KEYS = {
    "BillHead": [
        "FID", "FBillNo", "FDocumentStatus", "FApplicationDate", "FBillTypeID", "FApplicationOrgId",
        "FApplicationDeptId", "FApplicantId", "FCurrencyId", "FCloseStatus", "FCancelStatus",
        "FApproverId", "FApproveDate", "FNote",
    ],
    "FEntity": [
        "FEntryID", "FMaterialId", "FUnitId", "FReqQty", "FApproveQty", "FRemainQty",
        "FSuggestSupplierId", "FPurchaseOrgId", "FPurchaseDeptId", "FPurchaserId",
        "FArrivalDate", "FEntryNote", "FMRPCloseStatus",
    ],
}
PO_READ_KEYS = {
    "BillHead": [
        "FID", "FBillNo", "FDocumentStatus", "FDate", "FBillTypeID", "FPurchaseOrgId",
        "FPurchaseDeptId", "FPurchaserId", "FSupplierId",
        "FCloseStatus", "FCancelStatus", "FApproverId", "FApproveDate",
    ],
    "FPOOrderEntry": [
        "FEntryID", "FMaterialId", "FUnitId", "FQty", "FPrice", "FTaxPrice", "FEntryTaxRate",
        "FEntryTaxAmount", "FDeliveryDate", "FRemainReceiveQty", "FStockInQty",
        "FEntryNote", "FMRPCloseStatus",
    ],
}


def load(form_id: str):
    fn = DATA / f"fields_{form_id}.json"
    return json.loads(fn.read_text(encoding="utf-8"))


def pick(data, entity_key, keys):
    by = {f["key"]: f for f in data["fields"] if f["entityKey"] == entity_key}
    rows = []
    for k in keys:
        f = by.get(k)
        if f:
            rows.append(f)
        else:
            # fuzzy: EntryID often FENTRYID physical
            for kk, ff in by.items():
                if kk.upper() == k.upper() or kk.endswith(k):
                    rows.append(ff)
                    break
            else:
                rows.append({
                    "entityKey": entity_key,
                    "entityName": "",
                    "key": k,
                    "name": "(XML 未解析到，需核对)",
                    "fieldName": "",
                    "elem": "",
                })
    return rows


def all_entity_fields(data, entity_key):
    return [f for f in data["fields"] if f["entityKey"] == entity_key]


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def kd_table(rows, title):
    h = [f'<div class="section-title">{esc(title)}</div>',
         '<div class="panel"><table class="grid"><thead><tr>',
         '<th>实体</th><th>金蝶字段 Key</th><th>名称</th><th>类型元素</th><th>物理字段</th>',
         '</tr></thead><tbody>']
    for f in rows:
        h.append(
            "<tr>"
            f"<td>{esc(f.get('entityName') or f.get('entityKey'))}<br><code>{esc(f.get('entityKey'))}</code></td>"
            f"<td><code>{esc(f['key'])}</code></td>"
            f"<td>{esc(f.get('name'))}</td>"
            f"<td>{esc(f.get('elem'))}</td>"
            f"<td><code>{esc(f.get('fieldName'))}</code></td>"
            "</tr>"
        )
    h.append("</tbody></table></div>")
    return "\n".join(h)


def amos_table(rows, title):
    h = [f'<div class="section-title">{esc(title)}</div>',
         '<div class="panel"><table class="grid"><thead><tr>',
         '<th>第三方字段</th><th>类型</th><th>必填</th><th>说明</th>',
         '</tr></thead><tbody>']
    for path, typ, req, note in rows:
        h.append(
            f"<tr><td><code>{esc(path)}</code></td><td>{esc(typ)}</td><td>{esc(req)}</td><td>{esc(note)}</td></tr>"
        )
    h.append("</tbody></table></div>")
    return "\n".join(h)


def map_table(maps, title):
    h = [f'<div class="section-title">{esc(title)}</div>',
         '<div class="panel"><table class="grid"><thead><tr>',
         '<th>用途</th><th>金蝶字段（XML）</th><th>第三方字段</th><th>说明</th>',
         '</tr></thead><tbody>']
    for use, kd, amos, note in maps:
        h.append(
            f"<tr><td>{esc(use)}</td><td><code>{esc(kd)}</code></td>"
            f"<td><code>{esc(amos)}</code></td><td>{esc(note)}</td></tr>"
        )
    h.append("</tbody></table></div>")
    return "\n".join(h)


PAGE_SHELL = """<!DOCTYPE html>
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


def write_page(name, title, body, body_attr=""):
    html = PAGE_SHELL.format(title=title, body=body, body_attr=body_attr)
    (ROOT / name).write_text(html, encoding="utf-8")
    print("wrote", name)


def main():
    req = load("PUR_Requisition")
    po = load("PUR_PurchaseOrder")

    # 补全 EntryID：XML 里可能是系统字段
    for data, ek in ((req, "FEntity"), (po, "FPOOrderEntry")):
        keys = {f["key"] for f in data["fields"] if f["entityKey"] == ek}
        if "FEntryID" not in keys and "FENTRYID" not in {k.upper() for k in keys}:
            data["fields"].append({
                "entityKey": ek,
                "entityName": "明细信息",
                "key": "FEntryID",
                "name": "分录内码",
                "fieldName": "FENTRYID",
                "elem": "IntegerField(系统)",
            })

    # —— 采购申请同步字段页 ——
    req_head = pick(req, "BillHead", REQ_READ_KEYS["BillHead"])
    req_entry = pick(req, "FEntity", REQ_READ_KEYS["FEntity"])
    # also list any FRemain* / FQty* found
    extra_entry = [
        f for f in all_entity_fields(req, "FEntity")
        if any(x in f["key"] for x in ("Qty", "Remain", "Material", "Supplier", "Purchase"))
        and f["key"] not in {r["key"] for r in req_entry}
    ][:15]

    maps_req = [
        ("通知身份", "BillHead.FID", "subject.pid / selected.requisitionId", "金蝶只传 FID，不传单号作主键"),
        ("通知身份", "FEntity.FEntryID", "selected[].entryId", "明细内码"),
        ("通知辅助", "（金蝶拼标题）", "data.title", "如：采购申请选中明细询价"),
        ("AMOS读账套", "FBillNo/FDocumentStatus/物料数量等", "（不在事件体）", "AMOS 用已配置连接读金蝶最新数据"),
    ]

    body = f"""
  <div class="tip">字段来源：<code>docs/kingdeeXml/采购申请单.xml</code>（FormId={esc(req['formId'])}，共 {req['fieldCount']} 个字段）+ 第三方 A-003。下方为<strong>模拟取出</strong>：金蝶侧列出 AMOS 读单常用字段；第三方侧列出事件报文必传字段。</div>
  <div class="toolbar">
    <button class="btn p" type="button" onclick="act('模拟取出金蝶字段')">模拟取出金蝶字段</button>
    <button class="btn" type="button" onclick="act('同步报文')">查看 A-003 报文样例</button>
    <span class="tag sys">来源 XML · 非在线 QueryBusinessInfo</span>
  </div>
  {map_table(maps_req, "对照：金蝶 → 第三方（谁传什么）")}
  {amos_table(AMOS_A003, "第三方 A-003 事件字段（金蝶 POST 出去）")}
  {kd_table(req_head, "金蝶模拟取出 · 单据头（AMOS 读账套常用）")}
  {kd_table(req_entry + extra_entry, "金蝶模拟取出 · 明细 FEntity（AMOS 读账套常用）")}
  <div class="tip warn">完整字段共 {req['fieldCount']} 个，本页只展示对接相关子集。全部 JSON：<code>demo/data/fields_PUR_Requisition.json</code></div>
"""
    write_page("21_采购申请_同步字段.html", "采购申请同步字段 A-003", body, 'data-api="A-003"')

    # —— 采购订单同步字段 ——
    po_head = pick(po, "BillHead", PO_READ_KEYS["BillHead"])
    po_entry = pick(po, "FPOOrderEntry", PO_READ_KEYS["FPOOrderEntry"])
    extra_po = [
        f for f in all_entity_fields(po, "FPOOrderEntry")
        if any(x in f["key"] for x in ("Qty", "Price", "Tax", "Material", "Delivery", "Stock"))
        and f["key"] not in {r["key"] for r in po_entry}
    ][:15]
    maps_po = [
        ("通知身份", "BillHead.FID", "subject.pid / data.orderIds[]", "可批量 1～100 个 FID"),
        ("AMOS读账套", "FBillNo/供应商/明细物料价税等", "（不在事件体）", "首次/改单/状态同步同一套通知"),
    ]
    body = f"""
  <div class="tip">字段来源：<code>docs/kingdeeXml/采购订单.xml</code>（FormId={esc(po['formId'])}，共 {po['fieldCount']} 个字段）+ 第三方 A-007。</div>
  <div class="toolbar">
    <button class="btn p" type="button" onclick="act('模拟取出金蝶字段')">模拟取出金蝶字段</button>
    <button class="btn" type="button" onclick="act('同步报文')">查看 A-007 报文样例</button>
    <span class="tag sys">来源 XML · 非在线 QueryBusinessInfo</span>
  </div>
  {map_table(maps_po, "对照：金蝶 → 第三方（谁传什么）")}
  {amos_table(AMOS_A007, "第三方 A-007 事件字段（金蝶 POST 出去）")}
  {kd_table(po_head, "金蝶模拟取出 · 单据头（AMOS 读账套常用）")}
  {kd_table(po_entry + extra_po, "金蝶模拟取出 · 明细 FPOOrderEntry（AMOS 读账套常用）")}
  <div class="tip warn">完整字段共 {po['fieldCount']} 个。全部 JSON：<code>demo/data/fields_PUR_PurchaseOrder.json</code></div>
"""
    write_page("31_采购订单_同步字段.html", "采购订单同步字段 A-007", body, 'data-api="A-007"')

    # —— 公共请求字段：改为模拟公共外层 + 指向两边 ——
    body = f"""
  <div class="tip">不再单独「先定公共层」。本页直接列出<strong>四接口共用外层</strong>（第三方文档）与金蝶侧通知身份来源（XML 内码）。各接口 data 见申请/订单字段页。</div>
  {amos_table(AMOS_COMMON, "第三方 · 公共外层字段")}
  <div class="section-title">请求头（第三方）</div>
  <div class="panel"><table class="grid">
    <thead><tr><th>请求头</th><th>必填</th><th>说明</th></tr></thead>
    <tbody>
      <tr><td><code>Authorization</code></td><td>是</td><td>Bearer 永久集成令牌</td></tr>
      <tr><td><code>Content-Type</code></td><td>是</td><td>application/json；UTF-8</td></tr>
      <tr><td><code>Idempotency-Key</code></td><td>是</td><td>建议与正文 id 相同；重试不变</td></tr>
    </tbody>
  </table></div>
  <div class="section-title">金蝶身份字段从哪里来</div>
  <div class="panel"><table class="grid">
    <thead><tr><th>单据</th><th>XML 来源</th><th>身份 Key</th><th>进第三方</th></tr></thead>
    <tbody>
      <tr><td>采购申请</td><td>采购申请单.xml</td><td><code>FID</code> / <code>FEntity.FEntryID</code></td><td>A-003 subject/selected</td></tr>
      <tr><td>采购订单</td><td>采购订单.xml</td><td><code>FID</code> / <code>FPOOrderEntry.FEntryID</code></td><td>A-007 orderIds；删除用 entryIds</td></tr>
    </tbody>
  </table></div>
"""
    write_page("40_公共请求字段.html", "公共请求字段", body)

    # 字段总览加 XML 统计
    overview_note = {
        "requisitionFields": req["fieldCount"],
        "purchaseOrderFields": po["fieldCount"],
        "xmlDir": str(DOCS_XML),
    }
    (DATA / "xml_source_meta.json").write_text(
        json.dumps(overview_note, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("done", overview_note)


if __name__ == "__main__":
    main()
