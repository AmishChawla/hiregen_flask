(function(){
  // ---- local progress storage
  var KEY='ai-rec-course-v1';
  var load=function(){
    try{ return JSON.parse(localStorage.getItem(KEY)||'{}'); }catch(e){ return {}; }
  };
  var save=function(o){
    try{ localStorage.setItem(KEY, JSON.stringify(o)); }catch(e){}
  };

  // ---- mark-as-read
  var btn=document.querySelector('[data-read-toggle]');
  if(btn){
    var id=btn.getAttribute('data-lesson'), st=load();
    var paint=function(){
      var done=!!st[id];
      btn.textContent=done?'\u2713 Read':'Mark as read';
      btn.classList.toggle('done',done);
      btn.setAttribute('aria-pressed',done?'true':'false');
    };
    paint();
    btn.addEventListener('click',function(){
      st=load(); if(st[id]){delete st[id]}else{st[id]=Date.now()} save(st); paint();
    });
  }

  // ---- progress summary
  var bar=document.querySelector('[data-progress]');
  if(bar){
    var total=parseInt(bar.getAttribute('data-total'),10),st2=load();
    var n=Object.keys(st2).length;
    var pct=total?Math.round(100*n/total):0;
    bar.querySelector('.pnum').textContent=n+' of '+total+' lessons read';
    bar.querySelector('.pfill').style.width=pct+'%';
    if(n===0){bar.querySelector('.pnum').textContent='No lessons marked read yet';}
    var reset=bar.querySelector('[data-reset]');
    if(reset){reset.addEventListener('click',function(){
      if(confirm('Clear your reading progress on this device?')){save({});location.reload();}
    });}
  }

  // ---- sidebar ticks
  var st3=load();
  document.querySelectorAll('.side .les a').forEach(function(a){
    var m=a.getAttribute('href').match(/module-(\d+)\/lesson-(\d+)/);
    if(m&&st3[m[1]+'-'+m[2]]){a.classList.add('read');}
  });

  // ---- quiz
  document.querySelectorAll('.quiz').forEach(function(qz){
    var items=qz.querySelectorAll('.qitem'), answered=0, right=0;
    items.forEach(function(it){
      it.querySelectorAll('.qopt').forEach(function(b){
        b.addEventListener('click',function(){
          if(it.classList.contains('answered'))return;
          it.classList.add('answered');
          var ok=b.getAttribute('data-c')==='1';
          b.classList.add(ok?'right':'wrong');
          if(!ok){it.querySelector('.qopt[data-c="1"]').classList.add('right');}
          it.querySelector('.qwhy').hidden=false;
          answered++; if(ok)right++;
          if(answered===items.length){
            var s=qz.querySelector('.qscore');
            s.hidden=false;
            s.textContent=right+' of '+items.length+'. '+
              (right===items.length?'Nothing to revisit.':
               right>=items.length-1?'Worth re-reading the one you missed.':
               'Worth another pass through this module.');
          }
        });
      });
    });
  });
})();
