'use strict';
(() => {
const ref=(id,number,name)=>({id,number,name});
const context={accountId:'DEMO-ACCOUNT',organization:ref('1','100','演示采购组织')};
const material=ref('500','MAT-001','演示电阻');
const unit=ref('10','Pcs','件');
const address=(name,detail)=>({countryCode:'CN',province:'广东省',city:'深圳市',district:'宝安区',detail,contactName:name,contactPhone:'00000000000'});
const req={requisitionId:'100001',requisitionNumber:'CGSQ2611080001',documentStatus:'C',closed:false,cancelled:false,lines:[{entryId:'200001',material,specification:'10k 1%',unit,baseUnit:unit,project:null,requestedQty:'350',approvedQty:'350',orderJoinQty:'0',orderedQty:'0',remainingQty:'350',deliveryDate:'2026-11-20',closed:false,terminated:false,remark:''}]};
const order={orderId:'300001',orderNumber:'CGDD2611080001',purchaseDate:'2026-11-08',supplier:ref('600','SUP-001','演示供应商'),currency:ref('700','PRE001','人民币'),currencyIsoCode:'CNY',localCurrency:ref('700','PRE001','人民币'),exchangeType:ref('800','HLTX01_SYS','演示汇率类型'),exchangeRate:'1',paymentCondition:{...ref('900','001','演示付款条件'),description:'演示约定付款条款'},taxIncluded:true,documentStatus:'C',closed:false,cancelled:false,shipFromAddress:address('演示发货人','演示路18号A栋'),shipToAddress:address('演示收货人','演示路66号收货区'),remark:'',netAmount:'350',taxAmount:'45.50',grossAmount:'395.50',lines:[{entryId:'400001',lineNumber:1,material,specification:'10k 1%',unit,priceUnit:unit,baseUnit:unit,stockUnit:unit,project:null,settlementOrganization:context.organization,quantity:'350',baseQuantity:'350',priceQuantity:'350',netUnitPrice:'1',grossUnitPrice:'1.13',taxRate:'0.13',netAmount:'350',taxAmount:'45.50',grossAmount:'395.50',deliveryDate:'2026-11-20',closed:false,remark:'',sources:[{requisitionId:req.requisitionId,requisitionNumber:req.requisitionNumber,entryId:'200001'}]}]};
const oldAct=window.act;
const selected=()=>[...document.querySelectorAll('#chgGrid tbody tr')].filter(r=>r.querySelector('input').checked);
function phrase(rs){const nos=[...new Set(rs.map(r=>r.dataset.bill))];return nos.length===1?"单据编号为 '"+nos[0]+"' 的采购订单变更单":"单据编号为 '"+nos[0]+"' 等 "+nos.length+' 张采购订单变更单';}
function payload(r){
 const snapshot=structuredClone(order),c=r.cells;
 snapshot.orderId=r.dataset.orderId;snapshot.orderNumber=r.dataset.srcPo;
 snapshot.supplier=ref('DEMO-SUP-'+r.dataset.orderId,'DEMO-SUP',c[2].textContent.trim());
 const line=snapshot.lines[0];line.entryId='DEMO-ENTRY-'+r.dataset.orderId;
 line.material=ref('DEMO-MATERIAL',c[5].textContent.trim(),c[6].textContent.trim());line.specification=c[7].textContent.trim();
 const u=ref('DEMO-UNIT',c[8].textContent.trim(),c[8].textContent.trim());line.unit=u;line.baseUnit=u;line.priceUnit=u;line.stockUnit=u;
 line.quantity=c[9].textContent.trim();line.baseQuantity=line.quantity;line.priceQuantity=line.quantity;
 line.deliveryDate=c[10].textContent.trim().replaceAll('/','-');line.netUnitPrice=c[11].textContent.trim();line.grossUnitPrice=line.netUnitPrice;line.taxRate='0';
 line.netAmount=(Number(line.quantity)*Number(line.netUnitPrice)).toFixed(2);line.grossAmount=line.netAmount;line.taxAmount='0';
 snapshot.taxIncluded=false;snapshot.netAmount=line.netAmount;snapshot.grossAmount=line.netAmount;snapshot.taxAmount='0';
 return {occurredAt:'2026-11-08T02:00:01Z',data:{userId:'100',context,changeId:r.dataset.fid,changeNumber:r.dataset.bill,approvedAt:'2026-11-08T02:00:00Z',effectiveAt:'2026-11-08T02:00:00Z',order:snapshot,removedEntryIds:[]}};
}
window.act=function(action,...args){
 const rs=selected();
 if(action==='同步报文'){
  if(!rs.length)return window.xyKdPrompt('请先勾选要查看的单据。',{error:true});
  const escape=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  window.xyKdInlinePayload('同步报文','<p>A-PO-CHANGE · POST /api/open/v1/event-sources/kingdee-procurement-order-changes/events</p><p>演示样例，单价按未税、税率按0示意；原订单明细内码、完整订单、税率、来源及审核生效时间须从实际单据取得。每张变更单分别发送，未修改的有效明细也须传全。</p><pre class="xy-mono">'+escape(JSON.stringify(rs.map(payload),null,2))+'</pre><p>删除明细清单按现行文档展示；由AMOS比较完整订单识别删除的建议仍待双方确认。</p>');return;
 }
 if(action==='同步到AMOS'){
  if(!rs.length)return window.xyKdPrompt('请先勾选要同步的单据。',{error:true});
  if(rs.some(r=>r.dataset.billStatus!=='已审核'||r.dataset.effective!=='1'))return window.xyKdPrompt(phrase(rs)+'，同步到AMOS失败！',{error:true,detail:'变更单须已审核并生效，请检查后重试。'});
  rs.forEach(r=>{r.querySelector('[data-sync-status]').textContent='成功';r.querySelector('[data-sync-err]').textContent='-';});window.xyKdPrompt(phrase(rs)+'，同步到AMOS成功！');return;
 }
 if(action==='审核'||action==='生效'){
  if(!rs.length)return window.xyKdPrompt('请先勾选要操作的单据。',{error:true});
  if(action==='生效'&&rs.some(r=>r.dataset.billStatus!=='已审核'))return window.xyKdPrompt('请先审核选定的变更单。',{error:true});
  rs.forEach(r=>{if(action==='审核'){r.dataset.billStatus='已审核';r.cells[3].textContent='已审核';}else r.dataset.effective='1';});
  window.xyKdPrompt(phrase(rs)+'，'+action+'成功！',{detail:action==='审核'?'变更生效后，可点击“同步到AMOS”。':'可点击“同步到AMOS”演示同步结果。'});return;
 }
 return oldAct(action,...args);
};
})();
