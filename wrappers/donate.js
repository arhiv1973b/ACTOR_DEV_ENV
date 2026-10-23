// donate.js — copy-to-clipboard and helper for donate.html
(function(){
  function createToast(msg){
    var existing = document.getElementById('donate-toast');
    if(existing){ 
      existing.textContent = msg; 
      existing.style.opacity = '1'; 
      clearTimeout(existing._t); 
      existing._t = setTimeout(()=> {existing.style.opacity='0'}, 2500); 
      return; 
    }
    var t = document.createElement('div');
    t.id = 'donate-toast';
    t.textContent = msg;
    t.style.position = 'fixed';
    t.style.bottom = '80px';
    t.style.right = '16px';
    t.style.background = '#111';
    t.style.color = '#0f0';
    t.style.padding = '12px 16px';
    t.style.borderRadius = '6px';
    t.style.boxShadow = '0 4px 16px rgba(0,0,0,.8)';
    t.style.zIndex = 10000;
    t.style.transition = 'opacity .3s';
    t.style.fontFamily = 'monospace';
    t.style.fontSize = '13px';
    document.body.appendChild(t);
    t._t = setTimeout(()=> {t.style.opacity='0'}, 2500);
  }

  function copyToClipboard(text){
    if(!navigator.clipboard){
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.left = '-9999px';
      document.body.appendChild(ta);
      ta.select();
      try{
        document.execCommand('copy');
        createToast('✓ Скопировано в буфер');
      }catch(e){
        createToast('✗ Копирование не удалось');
      }
      ta.remove();
    } else {
      navigator.clipboard.writeText(text).then(
        function(){ createToast('✓ Скопировано в буфер'); },
        function(err){ createToast('✗ Ошибка копирования'); }
      );
    }
  }

  document.addEventListener('DOMContentLoaded', function(){
    // Copy bank details button
    var copyBankBtn = document.getElementById('copy-bank-btn');
    if(copyBankBtn){
      copyBankBtn.onclick = function(){
        var bankText = document.getElementById('bank-rect').innerText;
        copyToClipboard(bankText);
      };
    }

    // Copy payment purpose button
    var copyPurposeBtn = document.getElementById('copy-purpose-btn');
    if(copyPurposeBtn){
      copyPurposeBtn.onclick = function(){
        var purposeText = document.getElementById('payment-purpose').innerText;
        copyToClipboard(purposeText);
      };
    }

    // Show phishing warning
    var warnEl = document.getElementById('phish-warn');
    if(warnEl){ warnEl.style.display='block'; }
  });
})();
