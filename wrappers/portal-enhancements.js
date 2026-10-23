(function(){
  // Insert floating support badge and enhance external links
  function createBadge(){
    if(document.getElementById('support-badge')) return;
    var div = document.createElement('div');
    div.id = 'support-badge';
    div.style.position = 'fixed';
    div.style.right = '16px';
    div.style.bottom = '16px';
    div.style.zIndex = '9999';
    div.style.fontFamily = 'Arial, sans-serif';

    var a = document.createElement('a');
    a.href = 'wrappers/donate.html';
    a.textContent = 'Поддержать проект';
    a.style.display = 'inline-block';
    a.style.background = '#0066cc';
    a.style.color = '#fff';
    a.style.padding = '10px 14px';
    a.style.borderRadius = '6px';
    a.style.boxShadow = '0 2px 6px rgba(0,0,0,0.2)';
    a.style.textDecoration = 'none';
    a.style.fontSize = '13px';

    var close = document.createElement('button');
    close.textContent = '×';
    close.title = 'Скрыть';
    close.style.marginLeft = '8px';
    close.style.background = 'transparent';
    close.style.color = '#444';
    close.style.border = 'none';
    close.style.fontSize = '18px';
    close.style.cursor = 'pointer';

    close.onclick = function(){ div.style.display='none'; };

    div.appendChild(a);
    div.appendChild(close);
    document.body.appendChild(div);
  }

  function enhanceLinks(){
    // make external links open in a new tab and add noopener
    var anchors = document.getElementsByTagName('a');
    for(var i=0;i<anchors.length;i++){
      var a = anchors[i];
      try{
        var href = a.getAttribute('href');
        if(!href) continue;
        if(href.indexOf('http')===0 && a.target !== '_blank'){
          a.target = '_blank';
          a.rel = 'noopener noreferrer';
        }
      }catch(e){}
    }
  }

  if (document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', function(){ createBadge(); enhanceLinks(); });
  } else {
    createBadge(); enhanceLinks();
  }
})();
