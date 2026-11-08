"""Build the five procurement field catalogs from reviewed contract and local XML evidence."""
from pathlib import Path
import json,csv
ROOT=Path(__file__).resolve().parents[2]
evidence=json.loads((ROOT/'demo/data/kingdee-field-evidence.json').read_text(encoding='utf-8'))
# AMOS 右三列（路径／类型／填写要求）以合同原文为准；金蝶映射只写左三列与 basis
contract=json.loads((ROOT/'docs/AMOS字段合同摘录1108.json').read_text(encoding='utf-8'))
amos_fields={f['path']:f for f in contract.get('A-007_param_fields_before_bleed',[])}
# 飞书 A-PO-CHANGE 参数说明（2026-11-08 已开标签核对）
for f in [
 {'path':'data.previousVersion','type':'字符串','required':'否','meaning':'对方已有的上一审核版本；未提供不阻断普通同步，不要求额外生成'},
 {'path':'data.changeId','type':'字符串','required':'是','meaning':'真实稳定的变更单ID，或已核准路径的持久重审操作ID；数字ID传字符串，操作ID可为UUID；重试不得重新生成。'},
 {'path':'data.changeNumber','type':'字符串／null','required':'是','meaning':'真实变更单号；仅已核准且没有编号变更单的重审操作可明确为null，不编造单号。'},
 {'path':'data.approvedAt','type':'字符串','required':'是','meaning':'UTC时间，使用Z结尾。'},
 {'path':'data.effectiveAt','type':'字符串','required':'是','meaning':'UTC时间，使用Z结尾。'},
 {'path':'data.reason','type':'字符串','required':'否','meaning':'金蝶已有变更原因，有则传，不要求补造'},
 {'path':'data.removedEntryIds','type':'数组','required':'是','meaning':'变更中明确删除的原行ID；没有删除传空数组'},
 {'path':'data.changes','type':'数组','required':'否','meaning':'金蝶已有的原始变更明细可选传；AMOS自行比较旧内容与完整新订单，不要求对方另造差异清单'},
 # A-003 参数说明（同标签核对；数量叶子合同段当前页未完全加载）
 {'path':'data.title','type':'字符串','required':'否','meaning':'已关联询价省略时保留原标题；首次可按真实原申请单号展示，不补造业务数据'},
 {'path':'data.requisition','type':'所选采购申请完整内容','required':'是','meaning':'所选采购申请的完整内容；未选行不作删除'},
 {'path':'data.requisition.requisitionId','type':'字符串','required':'是','meaning':'精确外部内码，不是业务单号。'},
 {'path':'data.requisition.requisitionNumber','type':'字符串','required':'是','meaning':'原采购申请单号'},
 {'path':'data.requisition.documentStatus','type':'字符串','required':'是','meaning':'原FDocumentStatus审核状态；样例C为已审核，实际码表须确认'},
 {'path':'data.requisition.closed','type':'布尔值','required':'是','meaning':'是否关闭'},
 {'path':'data.requisition.cancelled','type':'布尔值','required':'是','meaning':'是否作废'},
 {'path':'data.requisition.lines','type':'数组','required':'是','meaning':'完整所选／当前有效明细，范围见接口规则'},
]:
 amos_fields[f['path']]=f
POCHG_ONLY={p for p in amos_fields if p in {'data.previousVersion','data.changeId','data.changeNumber','data.approvedAt','data.effectiveAt','data.reason','data.removedEntryIds','data.changes'}}

def amos_rule(required,meaning=''):
 required=(required or '').strip(); meaning=(meaning or '').strip()
 if required=='是':
  return ('必填，'+meaning) if meaning else '必填'
 if required=='否':
  return ('可选，'+meaning) if meaning else '可选'
 if meaning and meaning not in required:
  return required+'；'+meaning
 return required or meaning or '必填'

profiles={}

def row(path,typ='字符串',rule='必填',key='',basis=''):
 return {'path':path,'type':typ,'rule':rule,'key':key,'basis':basis}
def common(user=False):
 return [row('id',rule='可选，复用已有请求ID；重投保持一致'),row('occurredAt',rule='必填，UTC时间，以Z结尾'),row('data','对象'),row('data.context','对象'),row('data.context.accountId',rule='必填，与授权账套一致'),row('data.context.organization','对象', '必填，当前单据组织'),*[row('data.context.organization.'+k,rule='必填，组织'+n) for k,n in [('id','内码'),('number','编码'),('name','名称')]],row('data.context.operator','对象','可选，仅审计本次操作人'),row('data.context.operator.userId',rule='提供operator时必填，金蝶操作用户ID'),row('data.context.operator.displayName',rule='可选，操作人显示名'),row('data.sourceVersion',rule='可选；已启用版本保护的记录更新须提供真实版本'),*([row('data.userId',key='FCreatorId',basis='用户已选定创建人；业务归属待确认')] if user else [])]
def ref(path,key='',nullable=False,extra=False):
 """引用对象：表单Key只在对象／id；number／name 用 Key.FNumber／Key.FName 表示同引用带出。"""
 r=[row(path,'对象／null' if nullable else '对象','必填；明确不适用可为null' if nullable else '必填',key)]
 need=('对象非null时必填' if nullable else '必填')
 # 叶子填写要求跟 AMOS「传实际id、number、name」口径，不写金蝶内部词
 if key:
  r += [
   row(path+'.id',rule=need+'，传实际id',key=key,basis='引用字段内码'),
   row(path+'.number',rule=need+'，传实际number',key=key+'.FNumber',basis='同引用带出基础资料编码FNumber；表单无独立Key'),
   row(path+'.name',rule=need+'，传实际name',key=key+'.FName',basis='同引用带出基础资料名称FName；表单无独立Key'),
  ]
 else:
  r += [row(path+'.'+k,rule=need+'，传实际'+k) for k in ('id','number','name')]
 if extra:r.append(row(path+'.description',rule='必填，传付款条件id、number、name、description。',basis='合同必填完整说明；订单无独立付款条件说明字段；FClauseDesc属条款不冒用'))
 return r

def req(state=False):
 p='data.requisition';r=common(not state)
 if not state:r.append(row('data.title',rule='可选；已关联省略保留原标题'))
 r += [row(p,'对象'),row(p+'.requisitionId',key='FID',basis='用户已定单据内码口径'),row(p+'.documentStatus',key='FDocumentStatus',basis='第三方合同指定原审核状态；XML规则中有该标识'),row(p+'.closed','布尔值',key='FCloseStatus'),row(p+'.cancelled','布尔值',key='FCancelStatus')]
 if not state:r.append(row(p+'.requisitionNumber',key='FBillNo',basis='合同和XML规则引用单据编号'))
 r.append(row(p+'.lines','数组','可选；不传或[]均不改变行状态，不表示删除' if state else '必填，所选行完整内容；未选行不作删除'))
 q=p+'.lines[]';r.append(row(q+'.entryId',key='FEntryID',basis='XML FEntity EntryPkFieldName'))
 if not state:
  for field,key in [('material','FMaterialId'),('unit','FUnitId'),('baseUnit','FBaseUnitId'),('project','F_UFFS_Base_re5')]:r+=ref(q+'.'+field,key,field=='project')
  r.append(row(q+'.specification',rule='必填，可为空字符串表示清空',key='FMaterialModel'))
  for field,key in [('requestedQty','FReqQty'),('approvedQty','FApproveQty'),('orderJoinQty','FOrderJoinQty'),('orderedQty','FOrderQty'),('remainingQty','FRemainQty')]:r.append(row(q+'.'+field,rule='必填',key=key))
  r.append(row(q+'.deliveryDate',rule='必填，申请要求到货日期，不是报价截止日',key='FArrivalDate'))
 r += [row(q+'.closed','布尔值',key='FMRPCloseStatus'),row(q+'.terminated','布尔值',key='FMRPTerminateStatus')]
 if not state:r.append(row(q+'.remark',rule='必填，可为空字符串表示清空',key='FEntryNote'))
 return r

def order(state=False,change=False):
 r=common(not state);p='data.order';r += [row(p,'对象'),row(p+'.orderId',key='FID',basis='原订单FID，不是变更单FID'),row(p+'.documentStatus',key='FDocumentStatus',basis='合同及XML业务规则'),row(p+'.closed','布尔值',key='FCloseStatus'),row(p+'.cancelled','布尔值',key='FCancelStatus')]
 if not state:
  r += [row(p+'.orderNumber',key='FBillNo',basis='合同及XML规则引用'),row(p+'.purchaseDate',rule='必填，采购订单业务日期',key='FDate',basis='表头采购日期；继承字段Key=FDate，FPAYDATE属付款计划不冒用')]
  for f,k in [('supplier','FSupplierId'),('currency','FSettleCurrId'),('localCurrency','FLocalCurrId'),('exchangeType','FExchangeTypeId'),('paymentCondition','FPayConditionId')]:r+=ref(p+'.'+f,k,extra=f=='paymentCondition')
  r += [row(p+'.currencyIsoCode',key='FSettleCurrId.FCODE',basis='结算币别带出币别基础资料货币代码FCODE；不等于币别编码FNumber'),row(p+'.exchangeRate',key='FExchangeRate'),row(p+'.taxIncluded','布尔值',key='FIsIncludedTax')]
  for address,hint in [('shipFromAddress','XML有FProviderAddress／FProviderContactId／FProviderPhone等汇总字段，不足以展开合同叶子'),('shipToAddress','XML有FELocationAddress／FLocationAddress等汇总字段，不足以展开合同叶子')]:
   r.append(row(p+'.'+address,'对象',basis=hint))
   for f in ['addressId','countryCode','province','city','district','detail','postalCode','contactName','contactPhone']:
    r.append(row(p+'.'+address+'.'+f,'字符串／null' if f in ['addressId','postalCode'] else '字符串','可选，可明确为null' if f in ['addressId','postalCode'] else '必填，传完整联系人、电话、地区及详细地址。',basis=hint))
  r.append(row(p+'.remark',key='FNote',basis='用户指定单头备注 FNote；明细行为 FEntryNote，勿混'))
  for f,k in [('netAmount','FBillAmount'),('taxAmount','FBillTaxAmount'),('grossAmount','FBillAllAmount')]:r.append(row(p+'.'+f,key=k))
 r.append(row(p+'.lines','数组','可选；不传或[]不改变行状态，不表示删除' if state else '必填，全部当前有效明细；首次不为空，明确删除最后行的变更可为空'))
 q=p+'.lines[]';r.append(row(q+'.entryId',key='FEntryID',basis='XML FPOOrderEntry EntryPkFieldName'))
 if not state:
  r.append(row(q+'.lineNumber','整数','可选，仅显示顺序，不作为稳定身份',key='FSeq',basis='XML序号；仅显示顺序'))
  for f,k in [('material','FMaterialId'),('unit','FUnitId'),('priceUnit','FPriceUnitId'),('baseUnit','FBaseUnitId'),('stockUnit','FStockUnitID'),('project','F_UFFS_Base_83g'),('settlementOrganization','FEntrySettleOrgId')]:r+=ref(q+'.'+f,k,f=='project')
  r.append(row(q+'.specification',key='FModel'))
  for f,k in [('quantity','FQty'),('baseQuantity','FBaseUnitQty'),('priceQuantity','FPriceUnitQty'),('netUnitPrice','FPrice'),('grossUnitPrice','FTaxPrice'),('taxRate','FEntryTaxRate'),('netAmount','FEntryAmount'),('taxAmount','FEntryTaxAmount'),('grossAmount','FAllAmount')]:r.append(row(q+'.'+f,key=k))
  r.append(row(q+'.deliveryDate',key='FDeliveryDate'))
 r.append(row(q+'.closed','布尔值',key='FMRPCloseStatus'))
 if not state:
  r.append(row(q+'.remark',key='FEntryNote'))
  for f in ['packagingRequirement','qualityRequirement']:r.append(row(q+'.'+f,basis='合同条件必填；本订单XML未见对应包装／质量说明字段'))
  r += [row(q+'.sources','数组','必填，原申请单及明细身份；不传Save转换配置'),row(q+'.sources[].requisitionId',key='FSBillId',basis='订单行 Link（FPOOrderEntry_Link）源单内码；不能使用当前订单FID'),row(q+'.sources[].requisitionNumber',key='FSrcBillNo',basis='原申请单号，需核对Link关系'),row(q+'.sources[].entryId',key='FSId',basis='订单行 Link 源单分录内码；不是当前订单行 FEntryID')]
 if change:
  r += [row('data.previousVersion',basis='可选；本期策略不填'),row('data.changeId',key='FID',basis='变更单内码；表 T_PUR_POChange；不是原订单FID'),row('data.changeNumber','字符串／null',key='FBillNo',basis='变更单单据编号'),row('data.approvedAt',key='FApproveDate',basis='变更单审核日期'),row('data.effectiveAt',key='FActiveDate',basis='变更单生效日期；勿与表头FDate（变更日期）混淆'),row('data.reason',key='FChangeReason',basis='变更单变更原因'),row('data.removedEntryIds','数组'),row('data.removedEntryIds[]',rule='有删除行时必填，原订单行内码',key='FEntryID',basis='原订单明细内码，不是变更单行ID'),row('data.changes','数组')]
  for f,t,rule in [('entryId','字符串／null','changes项内必填；单头差异为null'),('field','字符串','changes项内必填，JSON Pointer，不按数组下标识别行'),('operation','字符串','changes项内必填，add／replace／remove'),('oldValue','原类型','changes项内必填，保留旧值原类型'),('newValue','原类型','changes项内必填，保留新值原类型')]:r.append(row('data.changes[].'+f,t,rule))
 return r

def deletion(req):
 return common()+[row('data.'+('requisitionId' if req else 'orderId'),key='FID',basis='用户已定原单FID；删除前留存'),row('data.deletionScope',rule='必填，document整单／entries部分行',basis='删除范围枚举；无对应单据字段'),row('data.entryIds','数组','必填，整单[]；部分删除明确原行ID'),row('data.entryIds[]',rule='部分删除时必填，原明细内码',key='FEntryID',basis='原单明细EntryPkFieldName；删除前留存'),row('data.deletedAt',rule='必填，实际删除时间，UTC以Z结尾',basis='删除事务成功后的业务时间；无单据字段')]
profiles={'A-003:full':req(),'A-003:state':req(True),'A-007:full':order(),'A-007:state':order(True),'A-PO-CHANGE:full':order(change=True),'A-REQ-DEL:full':deletion(True),'A-PO-DEL:full':deletion(False)}
# 用 AMOS 合同原文覆盖 type／rule（右三列中的路径已在、类型与填写要求）
for profile,rs in profiles.items():
 for r in rs:
  c=amos_fields.get(r['path'])
  if not c: continue
  if r['path'] in POCHG_ONLY and not profile.startswith('A-PO-CHANGE'): continue
  if profile.startswith('A-003') and r['path'].startswith('data.order'): continue
  if profile.startswith(('A-007','A-PO-CHANGE')) and r['path'].startswith('data.requisition'): continue
  if profile.startswith(('A-REQ-DEL','A-PO-DEL')) and (r['path'].startswith('data.order') or r['path'].startswith('data.requisition') or r['path'] in POCHG_ONLY or r['path']=='data.title'): continue
  r['type']=c['type']
  r['rule']=amos_rule(c['required'],c.get('meaning',''))
standard={'FID':'单据内码','FEntryID':'明细内码','FBillNo':'单据编号','FDocumentStatus':'单据状态'}
xml_name=lambda kind: '采购申请单' if kind=='req' else '采购订单'
for profile,rs in profiles.items():
 kind='req' if profile.startswith(('A-003','A-REQ-DEL')) else 'po'
 for r in rs:
  key=r['key'];base=key.split('.',1)[0] if key else '';found=evidence[kind].get(base) if key else None
  if key.endswith('.FNumber') and found:
   r.update(name='编码',evidence=f"docs/kingdeeXml/{xml_name(kind)}.xml:{found['line']}",status='同引用字段带出')
  elif key.endswith('.FName') and found:
   r.update(name='名称',evidence=f"docs/kingdeeXml/{xml_name(kind)}.xml:{found['line']}",status='同引用字段带出')
  elif found and key==base:
   r.update(name=found['name'],evidence=f"docs/kingdeeXml/{xml_name(kind)}.xml:{found['line']}",status='XML字段／建议映射；实际取值待联调')
  elif key in standard:
   r.update(name=standard[key],evidence=r['basis'],status='合同或用户已定字段；继承定义未完整展开')
  else:
   r.update(key='',name='',evidence=r['basis'],status='留空：缺少确切来源')
  r['default']='';r['red']=False
  if r['path']=='data.userId':r.update(default='待确认业务归属',red=True)
  # 申请：context.organization = 申请组织
  if kind=='req' and r['path'] in ('data.context.organization','data.context.organization.id','data.context.organization.number','data.context.organization.name'):
   org=evidence['req']['FApplicationOrgId']
   leaf=r['path'].rsplit('.',1)[-1]
   if leaf in ('organization','id'):
    r.update(key='FApplicationOrgId',name=org['name'],evidence=f"docs/kingdeeXml/采购申请单.xml:{org['line']}",status='用户已定口径',basis='用户已定申请组织；XML OrgField' if leaf=='organization' else '同字段内码（FAPPLICATIONORGID）')
   elif leaf=='number':
    r.update(key='FApplicationOrgId.FNumber',name='编码',evidence=f"docs/kingdeeXml/采购申请单.xml:{org['line']}",status='用户已定口径；同引用字段带出',basis='同OrgField带出组织基础资料编码FNumber；表单无独立Key')
   elif leaf=='name':
    r.update(key='FApplicationOrgId.FName',name='名称',evidence=f"docs/kingdeeXml/采购申请单.xml:{org['line']}",status='用户已定口径；同引用字段带出',basis='同OrgField带出组织基础资料名称FName；表单无独立Key')
  # 订单／变更／删订单：context.organization = 采购组织（继承 OrgField，证据 JSON 未收录 Key）
  if kind=='po' and r['path'] in ('data.context.organization','data.context.organization.id','data.context.organization.number','data.context.organization.name'):
   leaf=r['path'].rsplit('.',1)[-1]; ev='docs/kingdeeXml/采购订单.xml:3621'
   if leaf in ('organization','id'):
    r.update(key='FPurchaseOrgId',name='采购组织',evidence=ev,status='XML继承OrgField／建议映射',basis='规则与 OrgFieldKey 均引用 FPurchaseOrgId；导出片段为 action=edit')
   elif leaf=='number':
    r.update(key='FPurchaseOrgId.FNumber',name='编码',evidence=ev,status='同引用字段带出',basis='同OrgField带出组织编码FNumber')
   elif leaf=='name':
    r.update(key='FPurchaseOrgId.FName',name='名称',evidence=ev,status='同引用字段带出',basis='同OrgField带出组织名称FName')
  if r['path']=='id':
   # 合同可选；本期一律不传，不做 New／Edit 两方案
   r.update(key='',name='',default='不填',basis='可选请求追踪id；本期不传',status='本期策略不填',evidence='',red=False)
  # 单据无字段、但接口必填且口径已定：默认值写清怎么取，标识／名称留空；不用「自造：」、也不标「待确认」
  if r['path']=='data.context.accountId':
   r.update(default='当前登录账套ID；指所属来源账套，后台投递使用原通知绑定账套，不随重投时登录账套变化',red=False,status='用户已定口径；单据无此字段',basis='对方必填账套；单据无对应字段',evidence='')
  if r['path']=='occurredAt':
   r.update(default='服务器当前时间（UTC，以Z结尾）；重投沿用首次通知时间',red=False,status='用户已定口径；单据无此字段',basis='对方必填通知时间；单据无对应字段',evidence='')
  if r['path']=='data.sourceVersion':
   r.update(default='不填',basis='可选版本保护；本期策略不填')
  if r['path']=='data.title':
   r.update(default='不填',basis='可选标题；本期策略不填')
  # 采购日期：继承 DateField，Name=采购日期，规则引用 FDate
  if r['path']=='data.order.purchaseDate':
   r.update(key='FDate',name='采购日期',evidence='docs/kingdeeXml/采购订单.xml:3619',status='XML继承DateField／建议映射',basis='表头采购日期；Key=FDate（继承），勿用 FPAYDATE',default='')
  if r['path']=='data.order.currencyIsoCode':
   # 币别基础资料「货币代码」；证据 JSON 未收 FCODE，按同引用带出口径
   curr=evidence['po'].get('FSettleCurrId')
   ev=f"docs/kingdeeXml/采购订单.xml:{curr['line']}" if curr else 'docs/kingdeeXml/采购订单.xml:5758'
   r.update(key='FSettleCurrId.FCODE',name='货币代码',evidence=ev,status='同引用字段带出；币别基础资料货币代码',basis='取结算币别对应币别主数据 FCODE（货币代码），不是 FNumber',default='',red=False)
  if r['path']=='data.order.paymentCondition.description':
   r.update(key='',name='',default='待确认：金蝶无此字段',red=True,evidence='',status='留空：缺少确切来源',basis='合同必填；单据无独立付款条件说明；不冒用 FClauseDesc')
  # 地址：对象行白话说明；叶子短句；可选→不填；对方要且金蝶无→待确认
  if r['path'] in ('data.order.shipFromAddress','data.order.shipToAddress'):
   r.update(default='待确认：省／市／区无此字段（手工如「Bａｏ安区?演示..路18号A栋」）。',red=True,basis=('发货：FProviderAddress／FProviderContactId／FProviderPhone；省市区无独立 Key' if r['path'].endswith('shipFromAddress') else '收货：FELocationAddress；省市区／联系人叶子待核')+'；示例模拟不规范手工输入')
  if '.shipFromAddress.' in r['path'] or '.shipToAddress.' in r['path']:
   leaf=r['path'].rsplit('.',1)[-1]
   if leaf in ('addressId','postalCode'):
    r.update(default='不填',basis='合同可选；金蝶无独立字段；本期不传')
   elif leaf in ('countryCode','province','city','district') or ('.shipToAddress.' in r['path'] and leaf in ('contactName','contactPhone')):
    r.update(default='待确认：金蝶无此字段',red=True)
   # contactName／contactPhone／detail 发货侧及 detail 收货侧由下方专项覆盖
  if r['path'] in ('data.order.lines[].packagingRequirement','data.order.lines[].qualityRequirement'):
   # 合同：未启用可省略；本期不启用 → 不填（不再标红待确认）
   r.update(default='不填',red=False,basis='合同未启用可省略；本订单XML未见对应字段；本期不传',status='本期策略不填',evidence='')
  if r['path']=='data.order.lines[].sources[].requisitionId':
   r.update(key='FSBillId',name='源单FID',evidence='docs/kingdeeXml/采购订单.xml:2463',status='Link实体口径／建议映射；子字段多为继承未展开',basis='FPOOrderEntry_Link 源单内码；不能使用当前订单FID',default='',red=False)
  if r['path']=='data.order.lines[].sources[].entryId':
   r.update(key='FSId',name='源单行内码',evidence='docs/kingdeeXml/采购订单.xml:2463',status='Link实体口径／建议映射；子字段多为继承未展开',basis='FPOOrderEntry_Link 源单分录内码；不是当前订单行FEntryID',default='',red=False)
  # 发货联系人／手机：订单有独立字段，可从金蝶取（省市区仍无）
  if r['path']=='data.order.shipFromAddress.contactName':
   r.update(key='FProviderContactId.FName',name='名称',evidence='docs/kingdeeXml/采购订单.xml:13072',status='同引用字段带出',basis='供货方联系人显示名',default='',red=False)
  if r['path']=='data.order.shipFromAddress.contactPhone':
   r.update(key='FProviderPhone',name='手机',evidence='docs/kingdeeXml/采购订单.xml:13096',status='XML字段／建议映射；实际取值待联调',basis='供货方联系人手机（BaseProperty）',default='',red=False)
  if r['path']=='data.order.shipFromAddress.detail':
   r.update(key='FProviderAddress',name='供货方地址',evidence='docs/kingdeeXml/采购订单.xml:11314',status='XML字段／建议映射；整段文本进 detail',basis='整段手工地址进明细叶子；省市区仍无独立字段',default='',red=False)
  if r['path']=='data.order.shipToAddress.detail':
   r.update(key='FELocationAddress',name='交货地址',evidence='docs/kingdeeXml/采购订单.xml:11014',status='XML字段／建议映射；整段文本进 detail',basis='整段交货地址进明细叶子；省市区仍无独立字段',default='',red=False)
  if r['path']=='data.order.remark':
   # 用户指定 FNote；本 FormMetadata 导出未见表头 Key（明细为 FEntryNote）
   r.update(key='FNote',name='备注',evidence='用户指定；采购订单.xml 表头未展开 FNote',status='用户已定口径',basis='单头备注；与明细 FEntryNote 区分',default='',red=False)
  if r['path']=='data.previousVersion':
   r.update(default='不填',basis='可选上一版本；本期策略不填')
  # A-PO-CHANGE 专有字段：证据来自采购订单变更单.xml（FormId SCP_POChange / T_PUR_POChange）
  if profile.startswith('A-PO-CHANGE') and r['path']=='data.changeId':
   r.update(key='FID',name='单据内码',evidence='docs/kingdeeXml/采购订单变更单.xml:196',status='合同或用户已定字段；表头继承未展开',basis='变更单内码；HeadEntity 表 T_PUR_POChange；不是原订单FID',default='',red=False)
  if profile.startswith('A-PO-CHANGE') and r['path']=='data.changeNumber':
   r.update(key='FBillNo',name='单据编号',evidence='docs/kingdeeXml/采购订单变更单.xml:196',status='合同或用户已定字段；表头继承未展开',basis='变更单单据编号；表头 BillNo 继承未展开',default='',red=False)
  if profile.startswith('A-PO-CHANGE') and r['path']=='data.approvedAt':
   r.update(key='FApproveDate',name='审核日期',evidence='docs/kingdeeXml/采购订单变更单.xml:468',status='XML字段／建议映射；实际取值待联调',basis='变更单审核日期；投递时转 UTC Z',default='',red=False)
  if profile.startswith('A-PO-CHANGE') and r['path']=='data.effectiveAt':
   r.update(key='FActiveDate',name='生效日期',evidence='docs/kingdeeXml/采购订单变更单.xml:508',status='XML字段／建议映射；实际取值待联调',basis='变更单生效日期；勿与表头 FDate（变更日期）混淆；投递时转 UTC Z',default='',red=False)
  if profile.startswith('A-PO-CHANGE') and r['path']=='data.reason':
   r.update(key='FChangeReason',name='变更原因',evidence='docs/kingdeeXml/采购订单变更单.xml:408',status='XML字段／建议映射；实际取值待联调',basis='变更单变更原因；不是采购订单表单上的同名字段',default='',red=False)
  if r['path']=='data.changes' or r['path'].startswith('data.changes[]'):
   r.update(default='不填',basis='可选变更明细；本期策略不填')
  if r['path']=='data.deletionScope':
   r.update(default='按勾选整单 document／部分行 entries',red=False,status='用户已定口径；单据无此字段',basis='对方必填删除范围；单据无对应字段',evidence='')
  if r['path']=='data.deletedAt':
   r.update(default='删除成功时的业务时间（UTC，以Z结尾）',red=False,status='用户已定口径；单据无此字段',basis='对方必填删除时间；单据无对应字段',evidence='')
  # 无金蝶标识的对象／数组容器：默认值列提示整体见请求报文（非业务默认值）
  if not r['key'] and not r['default'] and (r['type'].startswith('对象') or r['type'].startswith('数组') or r['type'] in ('完整订单','所选采购申请完整内容','账套、组织及本次操作人')):
   r['default']='参考：请求报文'
  if profile.startswith('A-PO-CHANGE') and r['path']=='data.userId':
   r.update(key='FCreatorId',name='创建人',evidence='docs/kingdeeXml/采购订单变更单.xml:419',status='XML字段／建议映射；实际取值待联调',basis='用户选定创建人；取自变更单 FCreatorId；与 AMOS 用户对应仍待确认')
  if r['path'] in ('data.context.operator','data.context.operator.userId','data.context.operator.displayName'):
   r.update(default='不填',basis='可选审计操作人；本期策略不填；与data.userId业务用户分开')
  # 申请行 project：扩展1 F_UFFS_Base_re5
  if kind=='req' and r['path'].startswith('data.requisition.lines[].project'):
   leaf=r['path'].rsplit('.',1)[-1]
   ev='docs/kingdeeXml/采购申请单_扩展1.xml:19'
   if leaf in ('project','id'):
    r.update(key='F_UFFS_Base_re5',name='项目编号',evidence=ev,status='XML扩展字段／建议映射；实际取值待联调',basis='明细行基础资料；LookUp 同扩展1项目编号')
   elif leaf=='number':
    r.update(key='F_UFFS_Base_re5.FNumber',name='编码',evidence=ev,status='同引用字段带出',basis='同引用带出基础资料编码FNumber；表单无独立Key')
   elif leaf=='name':
    r.update(key='F_UFFS_Base_re5.FName',name='名称',evidence=ev,status='同引用字段带出',basis='同引用带出基础资料名称FName；表单无独立Key')
   r['default']=''
  # 订单行 project：扩展1 F_UFFS_Base_83g
  if kind=='po' and r['path'].startswith('data.order.lines[].project'):
   leaf=r['path'].rsplit('.',1)[-1]
   ev='docs/kingdeeXml/采购订单_扩展1.xml:99'
   if leaf in ('project','id'):
    r.update(key='F_UFFS_Base_83g',name='项目编号',evidence=ev,status='XML扩展字段／建议映射；实际取值待联调',basis='明细行基础资料；LookUp 同扩展1项目编号')
   elif leaf=='number':
    r.update(key='F_UFFS_Base_83g.FNumber',name='编码',evidence=ev,status='同引用字段带出',basis='同引用带出基础资料编码FNumber；表单无独立Key')
   elif leaf=='name':
    r.update(key='F_UFFS_Base_83g.FName',name='名称',evidence=ev,status='同引用字段带出',basis='同引用带出基础资料名称FName；表单无独立Key')
   r['default']=''
  assert not(r['key'] and r['default'] and r['path'] not in ('data.userId','id'))
  # id 行的「单据FID+接口」是待确认方案说明，不是XML字段名，允许无中文名称
  assert r['name'] or not r['key'] or r['path']=='id'
 assert len({r['path'] for r in rs})==len(rs)
(ROOT/'demo/scripts/procurement-field-catalog.js').write_text('// Reviewed procurement contract fields; generated by audit_procurement_fields.py.\nwindow.procurementFieldCatalog='+json.dumps(profiles,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
with (ROOT/'docs/AMOS字段核对1108.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['场景','AMOS路径','类型','填写要求','金蝶字段标识','中文名称','默认值','状态','证据','补充依据'])
 for profile,rs in profiles.items():
  for r in rs:w.writerow([profile,r['path'],r['type'],r['rule'],r['key'],r['name'],r['default'],r['status'],r['evidence'],r['basis']])
summary={k:{'rows':len(rs),'mapped':sum(bool(r['key']) for r in rs),'blank':sum(not r['key'] for r in rs),'red':sum(r['red'] for r in rs)} for k,rs in profiles.items()}
(ROOT/'docs/AMOS字段核对1108统计.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary))
