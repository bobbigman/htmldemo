'use strict';
(() => {
 const oldAct=window.act;
 const rows=()=>[...document.querySelectorAll('#reqGrid tbody tr')];
 const selected=()=>rows().filter(r=>r.querySelector('input').checked);
 const ref=(id,number,name)=>({id,number,name});
 const context={accountId:'DEMO-ACCOUNT',organization:ref('1','100','演示采购组织')};
 const unit=ref('10','Pcs','件');let last=[];
 function show(message,payload){
  if(payload){
   const escaped=JSON.stringify(payload,null,2).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
   window.xyKdInlinePayload('同步报文','<p style="margin-bottom:10px">'+message+'</p><pre class="xy-mono">'+escaped+'</pre>');
  }else window.xyKdPrompt(message,{error:/^请先|本次未发送|尚未同步/.test(message)});
 }
 function state(r){return {entryId:r.dataset.entry,closed:r.dataset.closed==='1',terminated:r.dataset.terminated==='1'};}
 function build(chosen,statusOnly){const groups=new Map();chosen.forEach(r=>{if(!groups.has(r.dataset.fid))groups.set(r.dataset.fid,[]);groups.get(r.dataset.fid).push(r);});return [...groups].map(([fid,rs])=>{const r=rs[0],req={requisitionId:fid,documentStatus:r.dataset.billStatus==='已审核'?'C':'D',closed:r.dataset.closed==='1',cancelled:false,lines:rs.map(r=>{if(statusOnly)return state(r);const c=r.cells;return {...state(r),material:ref('DEMO-'+r.dataset.entry,c[7].textContent.trim(),c[8].textContent.trim()),specification:'',unit,baseUnit:unit,project:null,requestedQty:c[9].textContent.trim(),approvedQty:c[9].textContent.trim(),orderJoinQty:r.dataset.entry==='13'?'200':'0',orderedQty:r.dataset.entry==='13'?'200':'0',remainingQty:r.dataset.remainQty,deliveryDate:'2026-11-20',remark:''};})};if(!statusOnly)req.requisitionNumber=r.dataset.bill;return {occurredAt:new Date().toISOString(),data:{...(!statusOnly?{userId:'100'}:{}),context,requisition:req}};});}
 function mark(chosen){chosen.forEach(r=>{r.querySelector('[data-sync-status]').textContent='成功';r.querySelector('[data-sync-err]').textContent='-';});}
 function billPhrase(chosen){const numbers=[...new Set(chosen.map(r=>r.dataset.bill))];return numbers.length===1?"单据编号为 '"+numbers[0]+"' 的采购申请单":"单据编号为 '"+numbers[0]+"' 等 "+numbers.length+' 张采购申请单';}
 function send(statusOnly=false){
  const chosen=selected();if(!chosen.length)return show('请先勾选要同步的明细。');
  const invalid=chosen.filter(r=>statusOnly?r.dataset.synced!=='1':r.dataset.billStatus!=='已审核'||(r.dataset.synced!=='1'&&Number(r.dataset.remainQty)<=0));
  if(invalid.length){
   const reason=statusOnly?'所选明细尚未同步到AMOS，请先同步单据内容。':'首次同步须已审核且剩余数量大于0；已同步过但尚未审核的明细，请单独勾选后同步。';
   window.xyKdPrompt(billPhrase(chosen)+'，同步到AMOS失败！',{error:true,detail:reason});return;
  }
  last=build(chosen,statusOnly);mark(chosen);show(billPhrase(chosen)+'，同步到AMOS成功！');
 }
 window.act=function(action,...args){
  if(action==='同步到AMOS'){const chosen=selected();return send(chosen.length>0&&chosen.every(r=>r.dataset.synced==='1')&&chosen.some(r=>r.dataset.billStatus!=='已审核'));}
  if(action==='仅同步状态')return send(true);
  if(action==='同步报文')return show('以下为发送给AMOS的内容，仅供核对。',last.length?last:build(selected(),false));
  if(action==='查看同步记录'){window.parent.postMessage({page:'日志内容'},'*');return;}
  if(action==='审核'){const chosen=selected();if(!chosen.length)return show('请先勾选要审核的单据。');last=[];chosen.forEach(r=>{r.dataset.billStatus='已审核';r.cells[3].textContent='已审核';});const linked=chosen.filter(r=>r.dataset.synced==='1');if(linked.length){last=build(linked,true);mark(linked);}return show(linked.length?'审核成功，状态已发送到AMOS。内容有修改时，请再点击“同步到AMOS”。':'审核成功。如需发起询价，请点击“同步到AMOS”。');}
  if(action==='删除'){return window.xyConfirmDelete(chosen=>{const byId=new Map();chosen.forEach(r=>{if(!byId.has(r.dataset.fid))byId.set(r.dataset.fid,[]);byId.get(r.dataset.fid).push(r.dataset.entry);});const now=new Date().toISOString();last=[...byId].map(([fid,ids])=>({occurredAt:now,data:{context,requisitionId:fid,deletionScope:'entries',entryIds:ids,deletedAt:now}}));chosen.forEach(r=>r.remove());document.getElementById('rowCount').textContent=rows().length;window.updateSel();window.xyKdPrompt('单据删除成功，并同步到AMOS。');});}
  const messages={过滤:'已按当前条件查询。',刷新:'列表已刷新。',重置过滤:'查询条件已重置。',保存方案:'查询方案已保存。',提交:'提交成功。',退出:'当前为演示页面。'};
  if(action==='提交'&&!selected().length)return show('请先勾选要提交的单据。');
  if(messages[action])return show(messages[action]);
  if(['新增','下推','关联查询','业务操作','选项'].includes(action))return window.xyKdDialog(action,'<div class="xy-tip">'+action+'功能仅作界面演示。</div>',{});
  return oldAct(action,...args);
 };
 const zero=rows().find(r=>r.dataset.entry==='13');zero.querySelector('[data-sync-status]').textContent='已同步过 · 剩余数量为0';
})();
