/* Public cryptographic loader. No password or content is embedded in this file. */
(async () => {
  'use strict';
  const root=location.pathname.includes('/Sales-Stage-Optimization/')?'/Sales-Stage-Optimization/':'/';
  const aad=new TextEncoder().encode('DDN-GTM-site-v1');
  const storage='ddn-gtm-session-key:'+root;
  const decode=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
  const encode=b=>btoa(String.fromCharCode(...b));
  const form=document.getElementById('unlock-form');
  const button=document.getElementById('unlock-button');
  const message=document.getElementById('message');
  let envelope;
  const session={get(){try{return JSON.parse(sessionStorage.getItem(storage)||'null')}catch{return null}},set(v){try{sessionStorage.setItem(storage,JSON.stringify(v))}catch{}},clear(){try{sessionStorage.removeItem(storage)}catch{}}};
  async function decrypt(raw){
    const key=await crypto.subtle.importKey('raw',raw,'AES-GCM',false,['decrypt']);
    const bytes=await crypto.subtle.decrypt({name:'AES-GCM',iv:decode(envelope.iv),additionalData:aad},key,decode(envelope.ciphertext));
    const json=await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
    const data=JSON.parse(json);
    if(!data.files?.['index.html'])throw new Error('Invalid content');
    return data;
  }
  function render(data){
    const requested=decodeURIComponent(location.pathname.slice(root.length))||'index.html';
    const page=data.files[requested]?.type==='text/html'?requested:'index.html';
    const wantedDownload=data.files[requested]?.base64?requested:null;
    function download(name,filename){
      const file=data.files[name];if(!file?.base64)return;
      const url=URL.createObjectURL(new Blob([decode(file.base64)],{type:file.type}));
      const a=document.createElement('a');a.href=url;a.download=filename||name.split('/').pop();a.click();
      setTimeout(()=>URL.revokeObjectURL(url),30000);
    }
    let html=data.files[page].text;
    html=html.replace('<head>','<head><base href="'+root+page+'"><meta name="robots" content="noindex,nofollow,noarchive"><meta name="referrer" content="no-referrer">');
    const bar='<div id="access-session" style="display:flex;gap:16px;align-items:center;justify-content:flex-end;padding:8px 20px;background:#173e5b;color:white;font:13px system-ui;position:relative;z-index:9999"><span>Internal DDN · Password-protected session</span><button id="lock-site" style="padding:5px 12px;border:1px solid #acc5d8;border-radius:5px;background:transparent;color:white;cursor:pointer">Lock site</button></div>';
    html=html.replace(/(<body\b[^>]*>)/,'$1'+bar);
    document.open();document.write(html);document.close();
    document.addEventListener('click',event=>{
      const anchor=event.target.closest('a[href]');if(!anchor)return;
      const url=new URL(anchor.getAttribute('href'),document.baseURI);
      if(url.origin!==location.origin)return;
      const name=decodeURIComponent(url.pathname.slice(root.length));
      if(data.files[name]?.base64){event.preventDefault();event.stopImmediatePropagation();download(name,anchor.getAttribute('download'));}
    },true);
    document.getElementById('lock-site').addEventListener('click',()=>{session.clear();location.reload();});
    // Never leave decrypted content in a back/forward cache after locking.
    window.addEventListener('pageshow',e=>{if(e.persisted&&!session.get())location.reload();});
    if(wantedDownload){
      const notice=document.createElement('div');notice.style='padding:16px;background:#edf5fa;text-align:center';
      const a=document.createElement('a');a.href=root+wantedDownload;a.download=wantedDownload.split('/').pop();a.textContent='Download '+a.download;
      notice.append(a);document.getElementById('access-session').after(notice);
    }
  }
  async function unlock(event){
    event.preventDefault();button.disabled=true;message.textContent='Opening…';
    try{
      const password=document.getElementById('password').value;
      const material=await crypto.subtle.importKey('raw',new TextEncoder().encode(password),'PBKDF2',false,['deriveBits']);
      const raw=new Uint8Array(await crypto.subtle.deriveBits({name:'PBKDF2',salt:decode(envelope.salt),iterations:envelope.iterations,hash:'SHA-256'},material,256));
      const data=await decrypt(raw);
      session.set({salt:envelope.salt,key:encode(raw)});
      document.getElementById('password').value='';render(data);
    }catch{message.textContent='Unable to unlock. Check the password and try again.';button.disabled=false;}
  }
  try{
    if(!crypto.subtle||!window.DecompressionStream)throw new Error('Use a current browser over HTTPS.');
    const response=await fetch(root+'protected-content.json',{cache:'no-store'});
    if(!response.ok)throw new Error('The site could not be loaded. Please try again.');
    envelope=await response.json();
    if(envelope.version!==1||envelope.iterations!==600000)throw new Error('Unsupported site package.');
    const cached=session.get();
    if(cached?.salt===envelope.salt){
      try{render(await decrypt(decode(cached.key)));return;}catch{session.clear();}
    }else session.clear();
    form.addEventListener('submit',unlock);button.disabled=false;
  }catch(error){message.textContent=error.message;button.disabled=true;}
})();
