'use strict';
(() => {
const ref=(id,number,name)=>({id,number,name});
const context={accountId:'DEMO-ACCOUNT',organization:ref('1','100','演示采购组织')};
const material=ref('500','MAT-001','演示电阻');
const unit=ref('10','Pcs','件');
const address=(name,detail)=>({countryCode:'CN',province:'广东省',city:'深圳市',district:'宝安区',detail,contactName:name,contactPhone:'00000000000'});
const req={requisitionId:'100001',requisitionNumber:'CGSQ2611080001',documentStatus:'C',closed:false,cancelled:false,lines:[{entryId:'200001',material,specification:'10k 1%',unit,baseUnit:unit,project:null,requestedQty:'350',approvedQty:'350',orderJoinQty:'0',orderedQty:'0',remainingQty:'350',deliveryDate:'2026-11-20',closed:false,terminated:false,remark:''}]};
const order={orderId:'300001',orderNumber:'CGDD2611080001',purchaseDate:'2026-11-08',supplier:ref('600','SUP-001','演示供应商'),currency:ref('700','PRE001','人民币'),currencyIsoCode:'CNY',localCurrency:ref('700','PRE001','人民币'),exchangeType:ref('800','HLTX01_SYS','演示汇率类型'),exchangeRate:'1',paymentCondition:{...ref('900','001','演示付款条件'),description:'演示约定付款条款'},taxIncluded:true,documentStatus:'C',closed:false,cancelled:false,shipFromAddress:address('演示发货人','演示路18号A栋'),shipToAddress:address('演示收货人','演示路66号收货区'),remark:'',netAmount:'350',taxAmount:'45.50',grossAmount:'395.50',lines:[{entryId:'400001',lineNumber:1,material,specification:'10k 1%',unit,priceUnit:unit,baseUnit:unit,stockUnit:unit,project:null,settlementOrganization:context.organization,quantity:'350',baseQuantity:'350',priceQuantity:'350',netUnitPrice:'1',grossUnitPrice:'1.13',taxRate:'0.13',netAmount:'350',taxAmount:'45.50',grossAmount:'395.50',deliveryDate:'2026-11-20',closed:false,remark:'',sources:[{requisitionId:req.requisitionId,requisitionNumber:req.requisitionNumber,entryId:'200001'}]}]};
const changed=structuredClone(order);Object.assign(changed,{netAmount:'250',taxAmount:'32.50',grossAmount:'282.50'});Object.assign(changed.lines[0],{quantity:'250',baseQuantity:'250',priceQuantity:'250',netAmount:'250',taxAmount:'32.50',grossAmount:'282.50'});
const paths={'A-003':'kingdee-procurement','A-007':'kingdee-procurement-orders','A-PO-CHANGE':'kingdee-procurement-order-changes','A-REQ-DEL':'kingdee-procurement-requisition-deletions','A-PO-DEL':'kingdee-procurement-order-deletions'};
const logs=[];
function add(api,scene,time,data,status,outcome,note,options={}){
 const n=logs.length+1, isReq=api==='A-003'||api==='A-REQ-DEL';
 logs.push({key:n,api,scene,time,status,outcome,note,bill:isReq?req.requisitionNumber:order.orderNumber,fid:isReq?'100001':'300001',record:status===202?'DEMO-REC-'+String(n).padStart(4,'0'):'',attempts:1,body:{occurredAt:`2026-11-08T${time}Z`,data:structuredClone(data)},...options});
}
add('A-003','所选申请完整同步','01:00:00',{userId:'100',context,requisition:req},202,'已应用','所选行完整传入；未选行不表示删除。');
add('A-007','订单首次审核发布','01:10:00',{userId:'100',context,order},202,'已应用','关联AMOS既有建单记录；完整订单及单头地址。');
add('A-PO-CHANGE','审核生效 · 数量变更','02:00:01',{userId:'100',context,changeId:'500001',changeNumber:'CGDDX2611080001',approvedAt:'2026-11-08T02:00:00Z',effectiveAt:'2026-11-08T02:00:00Z',reason:'当前订单数量调整为250，保留已发历史',order:changed,removedEntryIds:[]},202,'已应用','350→250；演示已发300，剩余可发0，提示超出50。',{changeId:'500001'});
add('A-003','已有申请 · 反审核状态','02:05:00',{context,requisition:{requisitionId:'100001',documentStatus:'D',closed:false,cancelled:false}},202,'已应用','只更新状态，保留物料、数量；暂停新增采购。');
add('A-007','已有订单 · 部分行关闭','02:10:00',{context,order:{orderId:'300001',documentStatus:'C',closed:false,cancelled:false,lines:[{entryId:'400001',closed:true}]}},202,'处理中','202已接收，尚无最终业务结果。');
add('A-003','重复完整内容通知','02:15:00',{userId:'100',context,requisition:req},202,'内容未变','独立重复投递场景：同一内容不重复创建询价或催报。');
add('A-PO-CHANGE','相同变更ID · 不同内容','02:20:00',{userId:'100',context,changeId:'500001',changeNumber:'CGDDX2611080001',approvedAt:'2026-11-08T02:00:00Z',effectiveAt:'2026-11-08T02:00:00Z',order,removedEntryIds:[]},202,'处理冲突','同一changeId内容不同；后台记录冲突，不覆盖原变更。',{changeId:'500001'});
add('A-REQ-DEL','申请部分明细删除','02:30:01',{context,requisitionId:'100001',deletionScope:'entries',entryIds:['200001'],deletedAt:'2026-11-08T02:30:00Z'},'timeout','接收待核实','接收状态未知；可重投原报文，保留原身份和时间。',{retryable:true});
add('A-PO-DEL','订单整单独立删除','02:40:01',{context,orderId:'300001',deletionScope:'document',entryIds:[],deletedAt:'2026-11-08T02:40:00Z'},202,'已应用','整单entryIds为空数组；停止新增发货，保留物流历史。');
const invalid=structuredClone(order);delete invalid.shipToAddress;
add('A-007','完整内容缺少收货地址','02:50:00',{userId:'100',context,order:invalid},400,'未进入处理','完整报文缺必填地址；修正源数据后重新提交，不自动降级状态请求。');
const $=id=>document.getElementById(id),esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const localTime=t=>`${String(Number(t.slice(0,2))+8).padStart(2,'0')}${t.slice(2)}`;
const transport=l=>l.status==='timeout'?'超时 · 接收未知':l.status===202?'202 已接收':'400 参数错误';
const tag=(text,kind)=>`<span class="tag ${kind}">${esc(text)}</span>`;
let current=null,tab='request';
function render(){
 const q=$('keyword').value.trim().toLowerCase();
 const shown=logs.filter(l=>(!q||[l.bill,l.fid,l.record,l.changeId||''].join(' ').toLowerCase().includes(q))&&(!$('api').value||l.api===$('api').value)&&(!$('transport').value||String(l.status)===$('transport').value)&&(!$('outcome').value||l.outcome===$('outcome').value));
 $('summary').innerHTML=[['全部通知',logs.length],['已持久接收',logs.filter(l=>l.status===202).length],['处理冲突 / 参数错误',logs.filter(l=>l.outcome==='处理冲突'||l.status===400).length],['接收待核实',logs.filter(l=>l.status==='timeout').length]].map(([k,v])=>`<div class="metric"><b>${v}</b>${k}</div>`).join('');
 $('rows').innerHTML=shown.map(l=>`<tr><td>11-08 ${localTime(l.time)}</td><td>${tag(l.api,'sys')}<div class="sub">${esc(l.scene)}</div></td><td>${esc(l.bill)}<div class="sub">FID ${l.fid}${l.changeId?' · 变更 '+esc(l.changeId):''}</div></td><td>DEMO-ACCOUNT<div class="sub">100 演示采购组织</div></td><td>${tag(transport(l),l.status===202?'on':l.status===400?'err':'pending')}</td><td>${tag(l.outcome,['已应用','内容未变'].includes(l.outcome)?'on':l.outcome==='处理冲突'?'err':'pending')}</td><td class="note">${esc(l.note)}</td><td>${esc(l.record||'—')}</td><td><button class="btn" data-detail="${l.key}">详情 / 报文</button> <button class="btn" data-fields="${l.key}">字段对照</button></td></tr>`).join('')||'<tr><td colspan="9" class="empty">没有符合条件的日志，请调整筛选条件。</td></tr>';
 $('count').textContent=`当前 ${shown.length} 条 / 共 ${logs.length} 条 · 场景为独立演示，非同一订单连续执行记录`;
}
function showFields(l){
 const stateOnly=['A-003','A-007'].includes(l.api)&&!l.body.data.userId;
 const profile=l.api==='A-PO-CHANGE'?'A-PO-CHANGE:full':l.api==='A-REQ-DEL'?'A-REQ-DEL:full':l.api==='A-PO-DEL'?'A-PO-DEL:full':`${l.api}:${stateOnly?'state':'full'}`;
 const catalog=(window.procurementFieldCatalog&&window.procurementFieldCatalog[profile])||[];
 function readPath(root,path){
  let cur=root,parts=path.split('.');
  for(const part of parts){
   if(cur==null)return {found:false};
   if(part.endsWith('[]')){
    const key=part.slice(0,-2);
    if(!(key in cur)||!Array.isArray(cur[key]))return {found:false};
    if(!cur[key].length)return {found:true,value:cur[key],emptyArray:true};
    cur=cur[key][0];
   }else{
    if(!(part in cur))return {found:false};
    cur=cur[part];
   }
  }
  return {found:true,value:cur};
 }
 function exampleOf(path){
  if(path==='data.sourceVersion')return '未传';
  if(l.api==='A-003'&&!stateOnly&&path==='data.title')return '未传';
  if(path.startsWith('data.order.shipToAddress')&&l.body.data.order&&!('shipToAddress' in l.body.data.order))return '缺失：完整内容必填，本条因此被拒绝';
  if(path.startsWith('data.changes'))return '未传';
  if(path==='data.previousVersion'||path==='data.reason'||path==='id'||path==='data.context.operator'||path.startsWith('data.context.operator.')||path==='data.order.lines[].packagingRequirement'||path==='data.order.lines[].qualityRequirement'){
   const hit=readPath(l.body,path);
   if(!hit.found)return '未传';
  }
  const hit=readPath(l.body,path);
  if(!hit.found)return '未传';
  if(hit.emptyArray)return '[]';
  const v=hit.value;
  if(v===null)return 'null';
  // 对象／非空数组不在示例列展开；无标识的容器在默认值列写「参考：请求报文」
  if(typeof v==='object')return '';
  return String(v);
 }
 const rows=catalog.map(item=>{
  const rule=`${item.type}；${item.rule}`;
  const def=item.default||'';
  const red=item.red||item.path==='data.userId';
  return `<tr><td><code>${esc(item.key||'')}</code></td><td>${esc(item.name||'')}</td><td${red&&def?' style="color:#c62828"':''}>${esc(def)}</td><td><code>${esc(item.path)}</code></td><td>${esc(rule)}</td><td style="overflow-wrap:anywhere;max-width:250px">${esc(exampleOf(item.path))}</td></tr>`;
 }).join('');
 $('detailContent').innerHTML=`<div class="result">${esc(l.api)} · ${stateOnly?'已有单据仅状态同步':'当前场景字段对照'} · 合同字段 ${catalog.length} 项。默认值口径：有标识且空＝从金蝶取；无标识但默认值已写清＝单据无字段、本期已定怎么取；「不填」＝可省略且本期不传；「待确认：金蝶无此字段」＝对方要但金蝶没有、策略未定。对象／数组无标识写「参考：请求报文」。不用「自造」。</div><div style="overflow:auto;margin-top:12px"><table class="grid" style="white-space:normal"><thead><tr><th>金蝶字段标识</th><th>金蝶字段名称</th><th>金蝶默认值</th><th>AMOS报文路径</th><th>填写要求</th><th>本条示例</th></tr></thead><tbody>${rows}</tbody></table></div><p class="sub">${stateOnly?'只传原单和所需状态，不携带草稿数量、价格或地址；未传的行不作删除。':'叶子字段给出本条实际值；未传或缺失单独标明，不把业务默认值与「参考：请求报文」提示混为一谈。'} 金蝶标识取自本地XML，字段存在不等于联调通过。<a href="https://auraboot.feishu.cn/wiki/JqFDwH8adiXE2mkwCI8chWm9nTe" target="_blank" rel="noopener">查看接口文档</a></p>`;
}
function showTab(){
 $('detail').classList.toggle('fields-wide',tab==='fields');
 const l=current;document.querySelectorAll('[data-tab]').forEach(b=>b.classList.toggle('on',b.dataset.tab===tab));
 if(tab==='fields')showFields(l);
 if(tab==='request'){
  const body=structuredClone(l.body);
  // 与现行合同一致：外层可不传 id；本演示样例未传 id
  $('detailContent').innerHTML='<h3>请求地址与请求头</h3><pre class="json" id="http"></pre><h3>JSON 请求体</h3><pre class="json" id="payload"></pre><p class="sub">按现行合同：不强制 subject、sequence、type、schemaVersion 或 Idempotency-Key；内部信封由 AMOS 适配。Authorization 使用线下集成令牌。</p>';
  $('http').textContent=`POST <AMOS_API_BASE>/api/open/v1/event-sources/${paths[l.api]}/events\nAuthorization: Bearer <AMOS_INTEGRATION_TOKEN>\nContent-Type: application/json`;
  $('payload').textContent=JSON.stringify(body,null,2);
 }
 if(tab==='response'){
  let text;
  if(l.status===202){
   const receipt={recordPid:l.record};
   // 合同：调用方传了外层 id 才可回显 eventId；本演示未传 id，故不编造 eventId
   if(l.body.id)receipt.eventId=l.body.id;
   text=`HTTP 202\n${JSON.stringify(receipt,null,2)}\n\nHTTP 202仅表示“请求与待处理记录持久化成功”。\nrecordPid用于后续AMOS内部追踪，不是最终业务单号。\n若调用方传了id，可回显eventId；没有则省略。\n接收响应不返回业务duplicate／applied判断：业务判重、版本比较和更新在后台完成。`;
  }else if(l.status===400){
   text='HTTP 400\n\n合同口径：明确缺少／非法字段，不反查补齐、不填默认值。\n本条演示原因：完整请求缺少 data.order.shipToAddress。\n此处仅说明错误场景，未虚构对方错误回执JSON结构。';
  }else{
   text='请求超时，未取得接收回执；不能判断AMOS是否已经接收。\n\n合同口径：429、5xx、超时 —— 退避重投同一业务内容；可选id如有则保持不变，源版本如有则保留原值。';
  }
  $('detailContent').innerHTML='<div class="result" id="receipt"></div>';
  $('receipt').textContent=text;
  $('receipt').style.whiteSpace='pre-wrap';
 }
}
function open(key){current=logs.find(l=>l.key===key);const l=current;tab='request';$('detailTitle').textContent=`${l.api} · ${l.scene}`;$('facts').innerHTML=[['原单',l.bill+' / FID '+l.fid],['通知时间',`2026-11-08 ${localTime(l.time)} 北京时间`],['发送接收',transport(l)],['通知记录',l.record||'未取得'],['源版本','未传 · 真实依据待核准']].map(([k,v])=>`<div><span>${k}：</span>${esc(v)}</div>`).join('');$('retry').disabled=!l.retryable;$('retryHint').textContent=l.retryable?`已发送 ${l.attempts} 次；仅演示重投，不调用真实接口。`:'此记录不直接重投；参数错误须先修正，业务冲突须核查。';showTab();$('detail').showModal();}
 $('filters').onsubmit=e=>{e.preventDefault();render();};$('resetFilters').onclick=()=>{$('filters').reset();render();};$('rows').onclick=e=>{const f=e.target.closest('[data-fields]');if(f){open(Number(f.dataset.fields));tab='fields';showTab();return;}const b=e.target.closest('[data-detail]');if(b)open(Number(b.dataset.detail));};$('close').onclick=()=>$('detail').close();document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{tab=b.dataset.tab;showTab();});
 $('retry').onclick=()=>{if(!current.retryable)return;current.attempts++;current.status=202;current.record='DEMO-RETRY-'+current.key;current.outcome='处理中';current.note='模拟重投已接收；请求体和通知时间保持原样，等待AMOS内部结果。';current.retryable=false;render();$('detail').close();open(current.key);tab='response';showTab();$('retryHint').textContent=`模拟第 ${current.attempts} 次发送；未调用真实接口，未生成新业务身份。`;};
 render();
})();
