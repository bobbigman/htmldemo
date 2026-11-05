/* 金蝶-AMOS 采购对接演示 · 可点交互（对标星空列表） */
(function () {
  'use strict';

  var CSS = [
    '.xy-ov{position:fixed;inset:0;background:rgba(15,23,42,.45);display:flex;align-items:center;justify-content:center;z-index:99999;font-family:"Microsoft YaHei",sans-serif}',
    '.xy-dl{width:640px;max-width:94vw;max-height:88vh;display:flex;flex-direction:column;background:#fff;border-radius:4px;box-shadow:0 12px 40px rgba(0,0,0,.28);overflow:hidden}',
    '.xy-dl.wide{width:820px}',
    '.xy-dl-hd{background:#2d5afe;color:#fff;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;font-size:14px}',
    '.xy-x{cursor:pointer;opacity:.85;font-size:16px;padding:0 4px}',
    '.xy-x:hover{opacity:1}',
    '.xy-dl-bd{padding:16px;overflow:auto;font-size:13px;color:#333;line-height:1.7}',
    '.xy-dl-ft{background:#f5f6f7;border-top:1px solid #e3e5e8;padding:10px 14px;display:flex;justify-content:flex-end;gap:8px}',
    '.xy-btn{padding:6px 18px;border-radius:2px;border:1px solid #d0d5dd;background:#fff;cursor:pointer;font-size:13px}',
    '.xy-btn.p{background:#2d5afe;border-color:#2d5afe;color:#fff}',
    '.xy-btn.d{background:#c62828;border-color:#c62828;color:#fff}',
    '.xy-tip{background:#e8f0ff;border-left:3px solid #2d5afe;padding:8px 10px;color:#4a5a6a;font-size:12px;margin-bottom:12px}',
    '.xy-tip.warn{background:#fff8e8;border-left-color:#e65100}',
    '.xy-steps{margin:10px 0 0;padding-left:18px;color:#555}',
    '.xy-steps li{margin:4px 0}',
    '.xy-mono{font-family:Consolas,Monaco,monospace;font-size:12px;background:#0f172a;color:#e2e8f0;padding:10px;border-radius:4px;white-space:pre-wrap;max-height:360px;overflow:auto}',
    '.xy-toast{position:fixed;left:50%;bottom:40px;transform:translateX(-50%);background:#2c3e50;color:#fff;padding:8px 16px;border-radius:4px;z-index:100000;font-size:13px}',
    /* 对标金蝶：工具栏下左上角绿/红消息条 */
    '.xy-kd-msg{background:#e8f7e8;border-bottom:1px solid #b7e0b7;padding:12px 16px;font-family:"Microsoft YaHei",sans-serif}',
    '.xy-kd-msg.err{background:#fff2f0;border-bottom-color:#ffccc7}',
    '.xy-kd-msg-row{display:flex;gap:10px;align-items:flex-start}',
    '.xy-kd-msg-ico{width:22px;height:22px;border-radius:50%;background:#52c41a;color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;flex-shrink:0;line-height:1;margin-top:1px}',
    '.xy-kd-msg.err .xy-kd-msg-ico{background:#ff4d4f}',
    '.xy-kd-msg-body{flex:1;min-width:0}',
    '.xy-kd-msg-txt{color:#389e0d;font-size:13px;line-height:1.6}',
    '.xy-kd-msg.err .xy-kd-msg-txt{color:#cf1322}',
    '.xy-kd-msg-detail{margin-top:4px;color:#666;font-size:12px;line-height:1.6}',
    '.xy-kd-msg-ft{margin-top:8px;display:flex;align-items:center;gap:14px;flex-wrap:wrap}',
    '.xy-kd-msg-ft button{height:26px;padding:0 14px;border:1px solid #2d5afe;background:#fff;color:#2d5afe;border-radius:2px;cursor:pointer;font-size:12px}',
    '.xy-kd-msg-ft button:hover{background:#f0f5ff}',
    '.xy-kd-msg-link{color:#2d5afe;font-size:12px;cursor:pointer;text-decoration:none}',
    '.xy-kd-msg-link:hover{text-decoration:underline}',
    '.xy-kd-msg-link-hint{color:#888;font-size:12px}',
    /* 对标金蝶删除确认条（工具栏下黄底） */
    '.xy-kd-ask{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;flex-wrap:wrap;background:#fff8d6;border-bottom:1px solid #f0e2a8;padding:12px 16px;font-family:"Microsoft YaHei",sans-serif}',
    '.xy-kd-ask-main{display:flex;gap:10px;align-items:flex-start}',
    '.xy-kd-ask-ico{width:22px;height:22px;border-radius:50%;background:#fa8c16;color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;flex-shrink:0;line-height:1;margin-top:1px}',
    '.xy-kd-ask-q{color:#333;font-size:13px;line-height:1.5;margin-bottom:8px}',
    '.xy-kd-ask-btns{display:flex;gap:8px}',
    '.xy-kd-ask-btns button{height:26px;padding:0 14px;border:1px solid #d0d5dd;background:#fff;border-radius:2px;cursor:pointer;font-size:12px;color:#333}',
    '.xy-kd-ask-btns button:hover{border-color:#2d5afe;color:#2d5afe}',
    '.xy-kd-ask-help{color:#2d5afe;font-size:12px;cursor:pointer;white-space:nowrap;padding-top:2px;text-decoration:none}',
    '.xy-kd-ask-help:hover{text-decoration:underline}',
    '.xy-kd-ask-extra{width:100%;margin:4px 0 0 32px;padding:8px 10px;background:#fffef5;border:1px dashed #e8d58a;color:#666;font-size:12px;line-height:1.7;display:none}'
  ].join('');

  function ensureStyle() {
    if (document.getElementById('xy-style')) return;
    var s = document.createElement('style');
    s.id = 'xy-style';
    s.textContent = CSS;
    document.head.appendChild(s);
  }

  function closeDlg() {
    var ov = document.querySelector('.xy-ov');
    if (ov) ov.remove();
  }

  function closeDrawer() {
    var mask = document.querySelector('.xy-drawer-mask');
    var dr = document.querySelector('.xy-drawer');
    if (mask) mask.remove();
    if (dr) dr.remove();
  }

  var SYNC_LOG_FIELDS = [
    ['log.id', 'string', '是', '日志主键'],
    ['log.apiCode', 'string', '是', 'A-003 / A-007 / A-REQ-DEL / A-PO-DEL'],
    ['log.eventId', 'string', '是', '请求 id，重发不变'],
    ['log.idempotencyKey', 'string', '是', '与请求头一致'],
    ['log.operationId', 'string', '条件', '删除通知时必留；删后重发靠它'],
    ['log.formId', 'string', '是', 'PUR_Requisition / PUR_PurchaseOrder'],
    ['log.billFid', 'string', '是', '金蝶单据 FID；原单删了仍可查'],
    ['log.billNo', 'string', '否', '业务单号，删后检索靠它'],
    ['log.billGone', 'boolean', '否', '可选：标记原单是否已不在金蝶'],
    ['log.httpStatus', 'integer', '是', '202/400/401…'],
    ['log.recordPid', 'string', '否', 'AMOS 通知记录号'],
    ['log.requestBody', 'text', '是', '请求 JSON（含删除身份，重发直接用）'],
    ['log.responseBody', 'text', '否', '响应 JSON / 错误正文'],
    ['log.occurredAt', 'datetime', '是', '同步发生时间']
  ];

  /** 同步日志落库字段：内部技术参考抽屉（非会议） */
  function openLogFieldsDrawer() {
    ensureStyle();
    closeDrawer();
    var rows = SYNC_LOG_FIELDS.map(function (f) {
      return '<tr><td><code>' + f[0] + '</code></td><td>' + f[1] + '</td><td>' + f[2] + '</td><td>' + f[3] + '</td></tr>';
    }).join('');
    var mask = document.createElement('div');
    mask.className = 'xy-drawer-mask';
    var dr = document.createElement('div');
    dr.className = 'xy-drawer wide';
    dr.innerHTML =
      '<div class="xy-drawer-hd"><b>落库字段 · 内部参考</b><span class="xy-x" data-close>×</span></div>' +
      '<div class="xy-drawer-bd">' +
      '<div class="xy-tip">纯技术备忘，不对会议、不勾「纳入/待定」。权威底稿：<code>demo/data/sync_log_fields.json</code>。</div>' +
      '<table class="grid" style="min-width:0;table-layout:auto">' +
      '<thead><tr><th>字段</th><th>类型</th><th>必填</th><th>说明</th></tr></thead>' +
      '<tbody>' + rows + '</tbody></table>' +
      '</div>' +
      '<div class="xy-drawer-ft"><button type="button" class="xy-btn p" data-close>关闭</button></div>';
    document.body.appendChild(mask);
    document.body.appendChild(dr);
    function onClose() { closeDrawer(); }
    mask.addEventListener('click', onClose);
    dr.querySelectorAll('[data-close]').forEach(function (el) {
      el.addEventListener('click', onClose);
    });
  }

  /** 审核成功条接力：新增同步 / 修改同步 → 同一接口（演示说明，不写进用户正文） */
  function openAuditSameApiDrawer() {
    ensureStyle();
    closeDrawer();
    var isReq = (document.body.getAttribute('data-api') || 'A-003') === 'A-003';
    var billName = isReq ? '采购申请' : '采购订单';
    var syncName = isReq ? '申请询价/同步' : '订单同步';
    var mask = document.createElement('div');
    mask.className = 'xy-drawer-mask';
    var dr = document.createElement('div');
    dr.className = 'xy-drawer';
    dr.innerHTML =
      '<div class="xy-drawer-hd"><b>新增与修改怎么同步</b><span class="xy-x" data-close>×</span></div>' +
      '<div class="xy-drawer-bd">' +
      '<div class="xy-tip warn">这是给会议/演示看的说明，正式产品里用户只会看到「审核成功」，不会弹这段话。</div>' +
      '<div class="xy-tip">表上常把「新增后同步」和「修改后同步」写成两行；对 AMOS 仍是<strong>同一套' + syncName + '</strong>，不另开接口，也不另做「改单同步」按钮。</div>' +
      '<div style="margin-bottom:8px">说的是本列表里的' + billName + '。</div>' +
      '<ol class="xy-steps">' +
      '<li><strong>新增后同步</strong>：单据审核通过，系统自动通知 AMOS 来取。</li>' +
      '<li><strong>修改后同步</strong>：反审核改完再审（订单含变更后再审），还是同一套通知，AMOS 按单号重取最新内容。</li>' +
      '<li>界面只保留<strong>审核</strong>；点审核看到「已同步到AMOS」，这两种场景都已经覆盖到了。</li>' +
      '</ol>' +
      '<div class="xy-tip" style="margin-top:14px">细字段对照可到左轨「字段分析」，或申请/订单下的同步字段页。</div>' +
      '</div>' +
      '<div class="xy-drawer-ft">' +
      '<button type="button" class="xy-btn" data-close>关闭</button>' +
      '<button type="button" class="xy-btn p" data-open-fields>打开字段分析</button>' +
      '</div>';
    document.body.appendChild(mask);
    document.body.appendChild(dr);
    function onClose() { closeDrawer(); }
    mask.addEventListener('click', onClose);
    dr.querySelectorAll('[data-close]').forEach(function (el) {
      el.addEventListener('click', onClose);
    });
    var openFields = dr.querySelector('[data-open-fields]');
    if (openFields) {
      openFields.addEventListener('click', function () {
        closeDrawer();
        if (window.parent && window.parent !== window) {
          window.parent.postMessage({ page: '字段分析' }, '*');
        }
        toast('已打开字段分析');
      });
    }
  }

  /** 删除成功条「删除后同步日志怎么查」右侧抽屉（大白话，少技术词） */
  function openAfterDelDrawer() {
    ensureStyle();
    closeDrawer();
    var isReq = (document.body.getAttribute('data-del-api') || 'A-REQ-DEL') === 'A-REQ-DEL';
    var billName = isReq ? '采购申请' : '采购订单';
    var mask = document.createElement('div');
    mask.className = 'xy-drawer-mask';
    var dr = document.createElement('div');
    dr.className = 'xy-drawer';
    dr.innerHTML =
      '<div class="xy-drawer-hd"><b>删除后同步日志怎么查</b><span class="xy-x" data-close>×</span></div>' +
      '<div class="xy-drawer-bd">' +
      '<div class="xy-tip warn">单子删掉以后，单据上就看不到「同步好不好了」。要查有没有通知成功、要不要再发一次，请到<strong>同步日志</strong>，不用再翻原单。</div>' +
      '<div style="margin-bottom:8px">说的是本列表里的' + billName + '删除。</div>' +
      '<ol class="xy-steps">' +
      '<li>在列表点<strong>删除</strong>，金蝶里先删掉（这一行会从列表消失）。</li>' +
      '<li>系统接着告诉 AMOS「这单没了」。成也好败也好，都会先记一笔同步日志（带上单号，方便以后按单号查）。</li>' +
      '<li>如果通知没成功：打开「公共 → 同步日志」，用单号搜，勾选「原单已删除」且失败的那一行。</li>' +
      '<li>点<strong>手工重发</strong>再通知一次。按原来那次的编号重发，不会当成另一笔新业务。</li>' +
      '</ol>' +
      '<div class="xy-tip" style="margin-top:14px">列表只管删；删完以后查结果、补发，都在同步日志。</div>' +
      '</div>' +
      '<div class="xy-drawer-ft">' +
      '<button type="button" class="xy-btn" data-close>关闭</button>' +
      '<button type="button" class="xy-btn p" data-open-log>打开同步日志</button>' +
      '</div>';
    document.body.appendChild(mask);
    document.body.appendChild(dr);
    function onClose() { closeDrawer(); }
    mask.addEventListener('click', onClose);
    dr.querySelectorAll('[data-close]').forEach(function (el) {
      el.addEventListener('click', onClose);
    });
    var openLog = dr.querySelector('[data-open-log]');
    if (openLog) {
      openLog.addEventListener('click', function () {
        closeDrawer();
        if (window.parent && window.parent !== window) {
          window.parent.postMessage({ page: '同步日志' }, '*');
        }
        toast('已打开同步日志');
      });
    }
  }

  function dlg(title, bodyHtml, opts) {
    ensureStyle();
    closeDlg();
    opts = opts || {};
    var ov = document.createElement('div');
    ov.className = 'xy-ov';
    ov.innerHTML =
      '<div class="xy-dl' + (opts.wide ? ' wide' : '') + '">' +
      '<div class="xy-dl-hd"><b>' + title + '</b><span class="xy-x" data-x>×</span></div>' +
      '<div class="xy-dl-bd">' + bodyHtml + '</div>' +
      '<div class="xy-dl-ft">' +
      (opts.hideCancel ? '' : '<button type="button" class="xy-btn" data-x>' + (opts.cancelText || '关闭') + '</button>') +
      (opts.okText ? '<button type="button" class="xy-btn ' + (opts.danger ? 'd' : 'p') + '" data-ok>' + opts.okText + '</button>' : '') +
      '</div></div>';
    document.body.appendChild(ov);
    ov.addEventListener('click', function (e) {
      if (e.target === ov || e.target.getAttribute('data-x') != null) closeDlg();
      if (e.target.getAttribute('data-ok') != null) {
        if (opts.onOk) opts.onOk();
        else closeDlg();
      }
    });
  }

  function toast(msg) {
    ensureStyle();
    var t = document.createElement('div');
    t.className = 'xy-toast';
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(function () { t.remove(); }, 2000);
  }

  function closeKdMsg() {
    var el = document.querySelector('.xy-kd-msg');
    if (el) el.remove();
  }

  function insertBelowMenubar(el) {
    var host = document.querySelector('.menubar');
    if (host && host.parentNode) {
      if (host.nextSibling) host.parentNode.insertBefore(el, host.nextSibling);
      else host.parentNode.appendChild(el);
    } else {
      document.body.insertBefore(el, document.body.firstChild);
    }
  }

  /** 对标金蝶：工具栏下左上角消息条；成功不展示报文 */
  function kdPrompt(message, opts) {
    ensureStyle();
    closeDlg();
    closeKdMsg();
    closeKdAsk();
    opts = opts || {};
    var linkHtml = opts.linkText
      ? '<a href="javascript:;" class="xy-kd-msg-link" data-link>' + opts.linkText + '</a>' +
        (opts.linkHint ? '<span class="xy-kd-msg-link-hint">' + opts.linkHint + '</span>' : '')
      : '';
    var bar = document.createElement('div');
    bar.className = 'xy-kd-msg' + (opts.error ? ' err' : '');
    bar.innerHTML =
      '<div class="xy-kd-msg-row">' +
      '<div class="xy-kd-msg-ico">' + (opts.error ? '!' : '✓') + '</div>' +
      '<div class="xy-kd-msg-body">' +
      '<div class="xy-kd-msg-txt">' + message + '</div>' +
      (opts.detail ? '<div class="xy-kd-msg-detail">' + opts.detail + '</div>' : '') +
      '<div class="xy-kd-msg-ft"><button type="button" data-ok>确定</button>' + linkHtml + '</div>' +
      '</div></div>';
    insertBelowMenubar(bar);
    function done() {
      bar.remove();
      if (opts.onOk) opts.onOk();
    }
    bar.querySelector('[data-ok]').addEventListener('click', done);
    var link = bar.querySelector('[data-link]');
    if (link && opts.onLink) {
      link.addEventListener('click', function (e) {
        e.preventDefault();
        opts.onLink();
      });
    }
  }

  function billKindName() {
    var kind = document.body.getAttribute('data-bill-kind') || '';
    if (kind === 'po-change') return '采购订单变更单';
    var del = document.body.getAttribute('data-del-api') || '';
    if (del === 'A-PO-DEL' || document.body.getAttribute('data-api') === 'A-007') return '采购订单';
    return '采购申请单';
  }

  function billNosPhrase(rows) {
    var nos = [];
    (rows || []).forEach(function (tr) {
      var b = tr.getAttribute('data-bill') || '';
      if (b && nos.indexOf(b) < 0) nos.push(b);
    });
    if (!nos.length) return '所选';
    if (nos.length === 1) return "单据编号为 '" + nos[0] + "' 的" + billKindName();
    return "单据编号为 '" + nos[0] + "' 等 " + nos.length + ' 张' + billKindName();
  }

  function selectedRows() {
    return Array.prototype.slice.call(document.querySelectorAll('table.grid tbody tr')).filter(function (tr) {
      var ck = tr.querySelector('input[type=checkbox]');
      return ck && ck.checked;
    });
  }

  function remainQtyOf(tr) {
    var raw = tr.getAttribute('data-remain-qty');
    if (raw == null || raw === '') return null;
    var n = Number(raw);
    return isNaN(n) ? null : n;
  }

  function rowLabel(tr) {
    var bill = tr.getAttribute('data-bill') || '';
    var entry = tr.getAttribute('data-entry') || '';
    var fid = tr.getAttribute('data-fid') || '';
    if (!bill) {
      var tds = tr.querySelectorAll('td');
      bill = tds[1] ? tds[1].textContent.trim() : '';
    }
    var mat = '';
    var matCell = tr.querySelector('td:nth-child(9)');
    if (matCell) mat = matCell.textContent.trim();
    var parts = [bill];
    if (entry) parts.push('EntryId ' + entry);
    else if (fid) parts.push('FID ' + fid);
    if (mat) parts.push('（' + mat + '）');
    return parts.join(' / ');
  }

  function markSync(status, err, rows) {
    (rows || selectedRows()).forEach(function (tr) {
      var st = tr.querySelector('[data-sync-status]');
      var er = tr.querySelector('[data-sync-err]');
      if (st) {
        st.className = 'tag ' + (status === '成功' ? 'on' : status === '失败' ? 'err' : 'pend');
        st.textContent = status;
      }
      if (er) er.textContent = err || '-';
      if (status === '成功') tr.setAttribute('data-synced', '1');
      if (status === '未同步') tr.setAttribute('data-synced', '0');
    });
  }

  function updateCounts() {
    var rows = document.querySelectorAll('table.grid tbody tr');
    var checked = document.querySelectorAll('table.grid tbody input[type=checkbox]:checked');
    var rc = document.getElementById('rowCount');
    var sc = document.getElementById('selCount');
    if (rc) rc.textContent = rows.length;
    if (sc) sc.textContent = checked.length;
  }

  function samplePayload(kind, rows) {
    rows = rows || selectedRows();
    var first = rows[0];
    var fid = first ? (first.getAttribute('data-fid') || '101') : '101';
    var bill = first ? (first.getAttribute('data-bill') || '') : '';
    var entries = rows.map(function (tr) {
      return tr.getAttribute('data-entry');
    }).filter(Boolean);

    if (kind === 'A-003') {
      return {
        id: 'kd-inquiry-demo-001',
        type: 'inquiry.requested',
        schemaVersion: 1,
        occurredAt: '2026-11-05T04:00:00Z',
        subject: { type: 'purchase-requisition', pid: fid },
        sequence: 1,
        data: {
          title: '采购申请选中明细询价',
          selected: rows.map(function (tr) {
            return {
              requisitionId: tr.getAttribute('data-fid') || fid,
              entryId: tr.getAttribute('data-entry') || ''
            };
          })
        }
      };
    }
    if (kind === 'A-007') {
      return {
        id: 'kd-order-sync-demo-001',
        type: 'order.published',
        schemaVersion: 1,
        occurredAt: '2026-11-05T04:10:00Z',
        subject: { type: 'purchase-order', pid: fid },
        sequence: 1,
        data: { orderIds: rows.map(function (tr) { return tr.getAttribute('data-fid') || fid; }) }
      };
    }
    if (kind === 'A-REQ-DEL') {
      var scope = entries.length && entries.length < rows.length + 1 && entries.length > 0
        ? (rows.length === 1 || new Set(rows.map(function (r) { return r.getAttribute('data-fid'); })).size === 1 && entries.length
          ? 'entries' : 'document')
        : 'document';
      // 同 FID 多行勾选 → entries；整单唯一 FID 且用户意图整单 → 简化：勾选行带 entry 则 entries
      var sameFid = rows.every(function (tr) { return (tr.getAttribute('data-fid') || '') === fid; });
      scope = (sameFid && entries.length) ? 'entries' : 'document';
      var body = {
        id: 'kd-req-del-demo-001',
        type: 'requisition.deleted',
        schemaVersion: 1,
        occurredAt: '2026-11-05T04:20:00Z',
        subject: { type: 'purchase-requisition', pid: fid },
        sequence: 3,
        data: {
          formId: 'PUR_Requisition',
          requisitionId: fid,
          deletionScope: scope,
          sourceVersion: '3',
          deletedAt: '2026-11-05T04:19:58+08:00',
          operationId: 'kd-del-op-req-001',
          billNo: bill || undefined,
          reason: '用户在列表删除（演示）',
          operator: { sourceUserId: 'demo', displayName: 'demo' }
        }
      };
      if (scope === 'entries') body.data.entryIds = entries;
      return body;
    }
    if (kind === 'A-PO-DEL') {
      return {
        id: 'kd-po-del-demo-001',
        type: 'order.deleted',
        schemaVersion: 1,
        occurredAt: '2026-11-05T04:25:00Z',
        subject: { type: 'purchase-order', pid: fid },
        sequence: 2,
        data: {
          formId: 'PUR_PurchaseOrder',
          orderId: fid,
          deletionScope: 'document',
          sourceVersion: '2',
          deletedAt: '2026-11-05T04:24:58+08:00',
          operationId: 'kd-del-op-po-001',
          billNo: bill || undefined,
          reason: '用户在列表删除（演示）'
        }
      };
    }
    return {
      eventId: 'kd-inquiry-demo-001',
      recordPid: 'AMOS_NOTIFICATION_RECORD_ID',
      duplicate: false
    };
  }

  function syncToAmos() {
    var rows = selectedRows();
    if (!rows.length) {
      toast('请先勾选单据或明细');
      return;
    }
    var apiHint = document.body.getAttribute('data-api') || 'A-003';

    if (apiHint === 'A-003') {
      var blocked = [];
      var allowed = [];
      rows.forEach(function (tr) {
        var q = remainQtyOf(tr);
        if (q != null && q <= 0) blocked.push(tr);
        else allowed.push(tr);
      });
      if (blocked.length) {
        var lines = blocked.map(function (tr) {
          var q = remainQtyOf(tr);
          return '· ' + rowLabel(tr) + '，剩余数量=' + q;
        }).join('<br>');
        dlg(
          '拦截：无法创建询价',
          '<div class="xy-tip">条件：仅<strong>剩余数量 &gt; 0</strong> 的明细可发起 AMOS 询价（A-003）。</div>' +
          '<div>以下 <b>' + blocked.length + '</b> 行剩余数量 ≤ 0，已拦截，不会同步：</div>' +
          '<div style="margin-top:8px;color:#d9534f;line-height:1.8">' + lines + '</div>' +
          (allowed.length
            ? '<div style="margin-top:12px">其余 <b>' + allowed.length + '</b> 行剩余数量 &gt; 0，可继续同步。</div>'
            : '<div style="margin-top:12px">当前勾选行均不满足条件，请重新选择。</div>'),
          {
            wide: true,
            okText: allowed.length ? '仅同步合格行' : '',
            onOk: allowed.length ? function () {
              closeDlg();
              doSyncToAmos(apiHint, allowed);
            } : undefined
          }
        );
        return;
      }
    }

    doSyncToAmos(apiHint, rows);
  }

  /** 同步到AMOS：不弹确认，直接同步并出左上角成功条 */
  function doSyncToAmos(apiHint, rows) {
    markSync('成功', '-', rows);
    kdPrompt(billNosPhrase(rows) + '，同步到AMOS成功！');
  }

  /** 工具栏「审核」：不弹确认，直接审核成功并同步 AMOS */
  function auditThenAutoSync() {
    var rows = selectedRows();
    if (!rows.length) {
      toast('请先勾选要审核的单据');
      return;
    }
    var apiHint = document.body.getAttribute('data-api') || 'A-003';
    runAutoSyncAfterAudit(apiHint, rows);
  }

  function runAutoSyncAfterAudit(apiHint, rows) {
    var skipped = [];
    var synced = [];
    rows.forEach(function (tr) {
      if (apiHint === 'A-003') {
        var q = remainQtyOf(tr);
        if (q != null && q <= 0) skipped.push(tr);
        else synced.push(tr);
      } else {
        synced.push(tr);
      }
    });

    if (synced.length) markSync('成功', '-', synced);
    skipped.forEach(function (tr) {
      var er = tr.querySelector('[data-sync-err]');
      if (er) er.textContent = '自动略过：剩余数量≤0';
    });

    var sameApiLink = {
      linkText: '新增与修改怎么同步',
      linkHint: '同一接口，无新按钮',
      onLink: function () { openAuditSameApiDrawer(); }
    };

    if (!synced.length && skipped.length) {
      kdPrompt(billNosPhrase(rows) + '，审核成功！', Object.assign({
        detail: '没有可同步到 AMOS 的明细（剩余数量均为 0，已略过）。'
      }, sameApiLink));
      return;
    }

    var msg = billNosPhrase(synced.length ? synced : rows) + '，审核成功！已同步到AMOS。';
    var detail = skipped.length
      ? '另有 ' + skipped.length + ' 行剩余数量为 0，已略过，未同步到 AMOS。'
      : '';
    kdPrompt(msg, Object.assign({ detail: detail || undefined }, sameApiLink));
  }

  function delFieldMeta(delApi) {
    if (delApi === 'A-PO-DEL') {
      return {
        mod: 'po',
        page: '删除字段 A-PO-DEL',
        eventType: 'order.deleted',
        brief:
          '关键字段：<code>subject.pid</code> / <code>data.orderId</code>（原订单 FID）、' +
          '<code>deletionScope</code>、<code>sourceVersion</code>、<code>operationId</code>、<code>deletedAt</code>。'
      };
    }
    return {
      mod: 'req',
      page: '删除字段 A-REQ-DEL',
      eventType: 'requisition.deleted',
      brief:
        '关键字段：<code>subject.pid</code> / <code>data.requisitionId</code>（原申请 FID）、' +
        '<code>deletionScope</code>（document / entries）、<code>entryIds</code>（部分明细时）、' +
        '<code>sourceVersion</code>、<code>operationId</code>、<code>deletedAt</code>。'
    };
  }

  function closeKdAsk() {
    var bar = document.querySelector('.xy-kd-ask');
    if (bar) bar.remove();
  }

  /**
   * 删除确认：对标金蝶工具栏下黄底「是 / 否」；右侧「查看删除说明」
   */
  function deleteThenSyncAmos() {
    var rows = selectedRows();
    if (!rows.length) {
      toast('请先勾选要删除的单据');
      return;
    }
    var delApi = document.body.getAttribute('data-del-api') || '';
    var syncAfterDel = !!delApi;
    ensureStyle();
    closeDlg();
    closeKdMsg();
    closeKdAsk();

    var bar = document.createElement('div');
    bar.className = 'xy-kd-ask';
    bar.innerHTML =
      '<div class="xy-kd-ask-main">' +
      '<div class="xy-kd-ask-ico">!</div>' +
      '<div>' +
      '<div class="xy-kd-ask-q">你确认要删除选定的记录?</div>' +
      '<div class="xy-kd-ask-btns">' +
      '<button type="button" data-yes>是</button>' +
      '<button type="button" data-no>否</button>' +
      '</div>' +
      '</div></div>' +
      (syncAfterDel
        ? '<a href="javascript:;" class="xy-kd-ask-help" data-help>查看删除说明</a>' +
          '<div class="xy-kd-ask-extra" data-extra>' +
          '删除成功后会通知 AMOS。若通知失败，原单已不在，请到「同步日志」用单号查找并手工重发。' +
          '</div>'
        : '');

    insertBelowMenubar(bar);

    bar.querySelector('[data-no]').addEventListener('click', closeKdAsk);
    bar.querySelector('[data-yes]').addEventListener('click', function () {
      closeKdAsk();
      showDeleteProgress(delApi, rows);
    });
    var help = bar.querySelector('[data-help]');
    if (help) {
      help.addEventListener('click', function (e) {
        e.preventDefault();
        var extra = bar.querySelector('[data-extra]');
        if (extra) {
          extra.style.display = extra.style.display === 'block' ? 'none' : 'block';
        }
      });
    }
  }

  function showDeleteProgress(delApi, rows) {
    var phrase = billNosPhrase(rows);
    var syncAfterDel = !!delApi;
    setTimeout(function () {
      rows.forEach(function (tr) { tr.remove(); });
      updateCounts();
      if (syncAfterDel) {
        kdPrompt(phrase + '，删除成功！已同步到AMOS。', {
          linkText: '删除后同步日志怎么查',
          linkHint: '原单删掉后，失败通知去哪查',
          onLink: function () { openAfterDelDrawer(); }
        });
      } else {
        kdPrompt(phrase + '，删除成功！');
      }
    }, 280);
  }

  function clearSyncFlag() {
    var rows = selectedRows();
    if (!rows.length) {
      toast('请先勾选要取消标记的行');
      return;
    }
    dlg(
      '取消同步标记',
      '<div class="xy-tip">仅清除金蝶侧同步标记/状态，<b>不调用</b> AMOS 删除接口。</div>' +
      '<div>将对已选 ' + rows.length + ' 行恢复为「未同步」。</div>',
      {
        okText: '确认取消标记',
        onOk: function () {
          markSync('未同步', '-');
          closeDlg();
          kdPrompt('已取消同步标记。');
        }
      }
    );
  }

  function showPayload() {
    var apiHint = document.body.getAttribute('data-api') || 'A-003';
    var req = samplePayload(apiHint);
    var resp = samplePayload('resp');
    dlg(
      '同步报文',
      '<div class="xy-tip">展示最近一次请求与返回（演示数据）。正式环境从同步日志读取。</div>' +
      '<b>请求</b><div class="xy-mono">' + JSON.stringify(req, null, 2) + '</div>' +
      '<div style="height:10px"></div><b>返回（HTTP 202）</b><div class="xy-mono">' + JSON.stringify(resp, null, 2) + '</div>',
      { wide: true }
    );
  }

  function toggleCombo(btn) {
    var box = btn.closest('.combo');
    document.querySelectorAll('.combo.open').forEach(function (el) {
      if (el !== box) el.classList.remove('open');
    });
    box.classList.toggle('open');
  }

  document.addEventListener('click', function (e) {
    if (!e.target.closest('.combo')) {
      document.querySelectorAll('.combo.open').forEach(function (el) { el.classList.remove('open'); });
    }
  });

  window.act = function (text) {
    if (text === '同步到AMOS') return syncToAmos();
    if (text === '取消同步标记') return clearSyncFlag();
    if (text === '同步报文') return showPayload();
    if (text === '审核' || text === '审核 ▾') return auditThenAutoSync();
    if (text === '删除') return deleteThenSyncAmos();
    if (text === '打开组合菜单') {
      var btn = document.querySelector('.combo > .btn, .combo > .mi');
      if (btn) toggleCombo(btn);
      return;
    }
    if (text === '保存连接配置') {
      toast('已保存（演示，未真正写入）');
      return;
    }
    if (text === '刷新' || text === '过滤' || text === '重置过滤' || text === '保存方案') {
      toast(text + '（演示）');
      return;
    }
    if (text === '退出') {
      toast('退出当前列表（演示）');
      return;
    }
    if (text === '删除后同步日志怎么查') return openAfterDelDrawer();
    if (text === '新增与修改怎么同步') return openAuditSameApiDrawer();
    if (text === '落库字段') return openLogFieldsDrawer();
    if (text === '查询日志') {
      toast('已按单号/接口/结果过滤（演示）');
      return;
    }
    if (text === '手工重发') {
      var delFail = document.querySelector('tr[data-del-fail="1"] input[type=checkbox]:checked');
      dlg(
        '手工重发',
        delFail
          ? '<div class="xy-tip warn">这单已经在金蝶里删掉了，通知 AMOS 那次没成功。再发一次就行，不用打开原单。</div>' +
            '<div>系统会按<strong>原来那次</strong>的编号重发，不会当成另一笔新删除。</div>'
          : '<div class="xy-tip">对失败记录再发一次；沿用原来的编号，不另起一笔。</div>',
        {
          okText: '确认重发',
          onOk: function () {
            closeDlg();
            if (delFail) {
              var cells = document.querySelectorAll('tr[data-del-fail="1"] td');
              if (cells[6]) cells[6].innerHTML = '<span class="tag on">成功</span>';
              if (cells[7]) cells[7].innerHTML = '<code>REC-90101</code>';
              kdPrompt("单据编号为 'CGSQ2611050001' 的采购申请单，同步到AMOS成功！");
            } else {
              kdPrompt('同步到AMOS成功！');
            }
          }
        }
      );
      return;
    }
    if (text === '模拟取出金蝶字段') {
      var api = document.body.getAttribute('data-api') || '';
      var src = api === 'A-007'
        ? 'docs/kingdeeXml/采购订单.xml → demo/data/fields_PUR_PurchaseOrder.json'
        : 'docs/kingdeeXml/采购申请单.xml → demo/data/fields_PUR_Requisition.json';
      dlg(
        '模拟取出金蝶字段',
        '<div class="xy-tip">不连账套。从 FormMetadata XML 解析 Key/Name/EntityKey，再与第三方事件字段对照。</div>' +
        '<div>来源：<b>' + src + '</b></div>' +
        '<div style="margin-top:8px">规则：金蝶 POST 只带 FID/EntryId 等身份；物料、数量、价税等由 AMOS 读金蝶账套取出。</div>',
        { wide: true }
      );
      return;
    }
    if (text === '导出会议确认') {
      var fieldRows = Array.prototype.slice.call(document.querySelectorAll('[data-field-row]'));
      var lines = ['字段,类型,必填,会议结论'];
      fieldRows.forEach(function (tr) {
        var path = tr.getAttribute('data-path') || '';
        var type = tr.getAttribute('data-type') || '';
        var req = tr.getAttribute('data-req') || '';
        var sel = tr.querySelector('select');
        var verdict = sel ? sel.value : '待定';
        lines.push([path, type, req, verdict].join(','));
      });
      dlg('会议字段确认导出', '<div class="xy-tip">可复制到会议纪要。正式可用 CSV 另存。</div><div class="xy-mono">' + lines.join('\n') + '</div>', { wide: true });
      return;
    }
    dlg(text, '<div class="xy-tip">静态演示动作（对标金蝶工具栏）。</div><div>动作：<b>' + text + '</b></div>');
  };

  window.xyToast = toast;
  window.toggleCombo = toggleCombo;

  window.addEventListener('message', function () {});
})();
