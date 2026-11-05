# -*- coding: utf-8 -*-
"""从 docs/kingdeeXml 的 FormMetadata XML 抽取字段清单。"""
import json
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
XML_DIR = ROOT / "docs" / "kingdeeXml"
OUT_DIR = ROOT / "demo" / "data"

FIELD_TAGS = {
    "BillNoField", "BillTypeField", "BillStatusField", "OrgField", "BaseDataField", "UserField",
    "CreaterField", "ModifierField", "DateField", "DateTimeField", "AmountField", "QtyField",
    "PriceField", "DecimalField", "TextField", "LargeTextField", "CheckBoxField", "ComboField",
    "IntegerField", "AssistantField", "RelatedFlexGroupField", "ItemClassTypeField",
    "MulBaseDataField", "BasePropertyField", "ProxyField", "UnitField", "TaxRateField",
    "TaxCombinationField", "LotField", "MulAssistantField", "BillLookUpField",
    "CreateDateField", "ModifyDateField", "ApproveDateField", "ApproverField",
    "CancelStatusField", "CheckerField", "CheckDateField", "OCRBaseDataField",
}
ENTITY_TAGS = {
    "EntryEntity", "SubHeadEntity", "SubEntryEntity", "TaxDetailSubEntryEntity", "HeadEntity",
}


def local(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def kids(el) -> dict:
    return {local(c.tag): (c.text or "").strip() for c in list(el)}


def extract(path: Path) -> dict:
    root = ET.parse(path).getroot()
    form_id = ""
    for el in root.iter():
        if local(el.tag) == "Id" and el.text and el.text.strip().startswith("PUR_"):
            form_id = el.text.strip()
            break

    entities = []
    for el in root.iter():
        tag = local(el.tag)
        if tag not in ENTITY_TAGS:
            continue
        k = kids(el)
        if k.get("Key"):
            entities.append({
                "key": k["Key"],
                "name": k.get("Name") or k["Key"],
                "table": k.get("TableName") or "",
                "elem": tag,
            })

    ename = {e["key"].upper(): e for e in entities}
    ename["BILLHEAD"] = {"key": "BillHead", "name": "单据头", "table": "", "elem": "HeadEntity"}

    fields = []
    for el in root.iter():
        tag = local(el.tag)
        if tag not in FIELD_TAGS:
            continue
        k = kids(el)
        if not k.get("Key"):
            continue
        ek = k.get("EntityKey") or "BillHead"
        if not ek:
            ek = "BillHead"
        meta = ename.get(ek.upper(), {"key": ek, "name": ek, "table": ""})
        fields.append({
            "entityKey": meta.get("key") or ek,
            "entityName": meta.get("name") or ek,
            "key": k["Key"],
            "name": k.get("Name") or "",
            "fieldName": k.get("FieldName") or "",
            "elem": tag,
            "mustInput": k.get("MustInput") or "",
        })

    best = {}
    for f in fields:
        idk = (f["entityKey"].upper(), f["key"].upper())
        old = best.get(idk)
        if not old or (f["fieldName"] and not old["fieldName"]):
            best[idk] = f
    out = list(best.values())
    out.sort(key=lambda x: (x["entityKey"], x["key"]))
    return {
        "formId": form_id,
        "source": path.name,
        "entities": entities,
        "fields": out,
        "fieldCount": len(out),
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {}
    for path in sorted(XML_DIR.glob("*.xml")):
        data = extract(path)
        if not data["formId"]:
            data["formId"] = "PUR_Requisition" if "申请" in path.name else "PUR_PurchaseOrder"
        # 继承自 BOS_BillModel 的系统字段在 FormMetadata 业务元素里常不出现，补上便于对接对照
        has = {(f["entityKey"].upper(), f["key"].upper()) for f in data["fields"]}
        inherited = [
            ("BillHead", "单据头", "FID", "单据内码", "FID", "IntegerField(继承)"),
            ("BillHead", "单据头", "FBillNo", "单据编号", "FBILLNO", "BillNoField(继承)"),
            ("BillHead", "单据头", "FDocumentStatus", "单据状态", "FDOCUMENTSTATUS", "BillStatusField(继承)"),
        ]
        if data["formId"] == "PUR_PurchaseOrder":
            inherited.append(("BillHead", "单据头", "FDate", "采购日期", "FDATE", "DateField(继承)"))
        for ek, en, key, name, field_name, elem in inherited:
            if (ek.upper(), key.upper()) not in has:
                data["fields"].insert(0, {
                    "entityKey": ek, "entityName": en, "key": key,
                    "name": name, "fieldName": field_name, "elem": elem, "mustInput": "",
                })
                has.add((ek.upper(), key.upper()))
        for ek, en in (("FEntity", "明细信息"), ("FPOOrderEntry", "明细信息")):
            if data["formId"] == "PUR_Requisition" and ek == "FPOOrderEntry":
                continue
            if data["formId"] == "PUR_PurchaseOrder" and ek == "FEntity":
                continue
            if (ek.upper(), "FENTRYID") not in has and any(e["key"].upper() == ek.upper() for e in data["entities"]):
                real_ek = next(e["key"] for e in data["entities"] if e["key"].upper() == ek.upper())
                data["fields"].append({
                    "entityKey": real_ek, "entityName": en, "key": "FEntryID",
                    "name": "分录内码", "fieldName": "FENTRYID",
                    "elem": "IntegerField(系统)", "mustInput": "",
                })
        data["fieldCount"] = len(data["fields"])
        out_path = OUT_DIR / f"fields_{data['formId']}.json"
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        c = Counter(f["entityKey"] for f in data["fields"])
        summary[data["formId"]] = {
            "file": path.name,
            "fieldCount": data["fieldCount"],
            "byEntity": dict(c),
        }
        print(data["formId"], data["fieldCount"], dict(c))
        for want in ["FBillNo", "FDocumentStatus", "FDate", "FID", "FMaterialId", "FReqQty", "FQty", "FEntryID", "FSupplierId"]:
            hits = [f for f in data["fields"] if f["key"] == want]
            print(" ", want, [(h["entityKey"], h["name"]) for h in hits])

    (OUT_DIR / "_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("written", OUT_DIR)


if __name__ == "__main__":
    main()
