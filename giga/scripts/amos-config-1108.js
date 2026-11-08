'use strict';
(() => {
 const $=id=>document.getElementById(id),form=$('configForm'),feedback=$('feedback');
 function validate(){
  if(!form.reportValidity())return false;
  const errors=[];
  try{const url=new URL($('base').value.trim());if(url.protocol!=='https:'||url.username||url.password||url.search||url.hash||url.pathname!=='/')errors.push('请填写HTTPS服务根地址，不含账号、路径、查询参数或片段。');}catch{errors.push('请填写有效的HTTPS根地址。');}
  const ids=new Set();
  for(const line of $('organizations').value.trim().split(/\n/)){const parts=line.split('|').map(s=>s.trim());if(parts.length!==3||parts.some(s=>!s)||!/^[1-9]\d*$/.test(parts[0])){errors.push('组织范围须按每行「正整数ID | 编码 | 名称」填写。');break;}if(ids.has(parts[0])){errors.push('组织ID不能重复。');break;}ids.add(parts[0]);}
  for(const id of ['token','account','retryPolicy','alertOwner'])if(!$(id).value.trim())errors.push('令牌、账套、重试策略和告警责任不能为空。');
  feedback.className='status'+(errors.length?' error':'');if(errors.length){feedback.textContent=errors.join('\n');return false;}return true;
 }
 $('save').onclick=()=>{if(validate())feedback.textContent='演示配置检查通过，当前输入已保留在本页。未写入服务端或浏览器存储；刷新恢复示例。令牌未输出到日志。';};
 $('test').onclick=()=>{if(validate())feedback.textContent='本地格式检查通过（演示）。\n未发送网络请求：真实连通性、令牌有效性、账套／组织授权均未验证。\n新版接收适配待AMOS确认；实际请求即使返回202，也只表示通知已持久接收。';};
 form.onsubmit=e=>{e.preventDefault();$('save').click();};
})();
