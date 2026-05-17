var _dialogCallback = null;

window.openDialog = function(message, title, onConfirm) {
  console.log('openDialog called:', message);
  document.getElementById('dialogBody').textContent = message;
  document.getElementById('dialogTitle').textContent = title || '\u63D0\u793A';
  document.getElementById('dialogMask').style.display = 'block';
  document.getElementById('dialogBox').style.display = 'flex';
  var btn = document.getElementById('dialogConfirmBtn');
  var newBtn = btn.cloneNode(true);
  btn.parentNode.replaceChild(newBtn, btn);
  newBtn.addEventListener('click', function () {
    console.log('Confirm button clicked');
    document.getElementById('dialogMask').style.display = 'none';
    document.getElementById('dialogBox').style.display = 'none';
    if (typeof onConfirm === 'function') {
      console.log('Executing callback');
      onConfirm();
    } else {
      console.log('No callback function');
    }
  });
};

window.closeDialog = function() {
  document.getElementById('dialogMask').style.display = 'none';
  document.getElementById('dialogBox').style.display = 'none';
};

document.addEventListener('DOMContentLoaded', function () {

  // ===== Toast Notification System =====
  function showToast(message, type) {
    type = type || 'success';
    var container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    var toast = document.createElement('div');
    toast.className = 'toast toast--' + type;
    toast.innerHTML = '<span class="toast-icon">' + (type === 'success' ? '\u2713' : '\u2715') + '</span><span>' + message + '</span>';
    container.appendChild(toast);
    setTimeout(function () {
      toast.classList.add('toast-exit');
      setTimeout(function () { toast.remove(); }, 300);
    }, 3500);
  }

  // Flash messages from server
  if (window._flashMessages && window._flashMessages.length > 0) {
    window._flashMessages.forEach(function (msg, i) {
      setTimeout(function () {
        showToast(msg.msg, msg.type === 'success' ? 'success' : 'error');
      }, i * 400 + 200);
    });
  }
  window.showToast = showToast;

  // ===== Login Form Validation =====
  var loginForm = document.querySelector('.login-card form');
  if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
      var username = loginForm.querySelector('input[name="username"]').value.trim();
      var password = loginForm.querySelector('input[name="password"]').value.trim();
      if (!username) { showToast('\u8BF7\u8F93\u5165\u7528\u6237\u540D', 'error'); e.preventDefault(); return; }
      if (!password) { showToast('\u8BF7\u8F93\u5165\u5BC6\u7801', 'error'); e.preventDefault(); return; }
    });
  }

  // ===== Edit Form Validation =====
  var editForm = document.querySelector('.card-body form');
  if (editForm) {
    var dateInput = editForm.querySelector('input[name="entry_date"]');
    if (dateInput) {
      dateInput.setAttribute('max', new Date().toISOString().split('T')[0]);
    }
    editForm.addEventListener('submit', function (e) {
      var fields = { name: '\u59D3\u540D', department: '\u90E8\u95E8', position: '\u804C\u52A1' };
      for (var key in fields) {
        var val = editForm.querySelector('input[name="' + key + '"]');
        if (val && !val.value.trim()) {
          showToast('\u8BF7\u8F93\u5165' + fields[key], 'error');
          e.preventDefault(); return;
        }
      }
      var entryDate = editForm.querySelector('input[name="entry_date"]');
      if (entryDate && !entryDate.value) {
        showToast('\u8BF7\u9009\u62E9\u5165\u804C\u65F6\u95F4', 'error');
        e.preventDefault(); return;
      }
      if (entryDate && new Date(entryDate.value) > new Date()) {
        showToast('\u5165\u804C\u65F6\u95F4\u4E0D\u80FD\u665A\u4E8E\u4ECA\u5929', 'error');
        e.preventDefault(); return;
      }
    });
  }

  // ===== Dialog Confirmations =====
  var approveLinks = document.querySelectorAll('a[href*="/approve/"]');
  console.log('Found approve links:', approveLinks.length);
  approveLinks.forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      var td = link.closest('tr').querySelector('td');
      var userName = td ? td.textContent.trim() : '';
      var href = link.getAttribute('href');
      console.log('Approve clicked, href:', href);
      window.openDialog('\u786E\u5B9A\u8981\u5C06\u5458\u5DE5\u3010' + userName + '\u3011\u7684\u4FE1\u606F\u5BA1\u6838\u901A\u8FC7\u5417\uFF1F', '\u786E\u8BA4\u5BA1\u6838\u901A\u8FC7', function () {
        console.log('Navigating to:', href);
        window.location.href = href;
      });
    });
  });

  var rejectLinks = document.querySelectorAll('a[href*="/reject/"]');
  console.log('Found reject links:', rejectLinks.length);
  rejectLinks.forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      var td = link.closest('tr').querySelector('td');
      var userName = td ? td.textContent.trim() : '';
      var href = link.getAttribute('href');
      console.log('Reject clicked, href:', href);
      window.openDialog('\u786E\u5B9A\u8981\u9A73\u56DE\u5458\u5DE5\u3010' + userName + '\u3011\u7684\u4FE1\u606F\uFF1F', '\u786E\u8BA4\u9A73\u56DE', function () {
        console.log('Navigating to:', href);
        window.location.href = href;
      });
    });
  });

  var reauditLinks = document.querySelectorAll('a[href*="/reaudit/"]');
  console.log('Found reaudit links:', reauditLinks.length);
  reauditLinks.forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      var td = link.closest('tr').querySelector('td');
      var userName = td ? td.textContent.trim() : '';
      var href = link.getAttribute('href');
      console.log('Reaudit clicked, href:', href);
      window.openDialog('\u786E\u5B9A\u8981\u5C06\u5458\u5DE5\u3010' + userName + '\u3011\u7684\u4FE1\u606F\u91CD\u65B0\u6253\u56DE\u5F85\u5BA1\u6838\u72B6\u6001\u5417\uFF1F', '\u786E\u8BA4\u91CD\u65B0\u5BA1\u6838', function () {
        console.log('Navigating to:', href);
        window.location.href = href;
      });
    });
  });

  var confirmLink = document.querySelector('a[href*="/confirm"]');
  if (confirmLink) {
    confirmLink.addEventListener('click', function (e) {
      e.preventDefault();
      var href = confirmLink.getAttribute('href');
      window.openDialog('\u786E\u8BA4\u540E\u5C06\u63D0\u4EA4\u5BA1\u6838\uFF0C\u8BF7\u7B49\u5F85\u7BA1\u7406\u5458\u5BA1\u6838\u3002\u662F\u5426\u7EE7\u7EED\uFF1F', '\u786E\u8BA4\u63D0\u4EA4', function () {
        window.location.href = href;
      });
    });
  }

});
