const BASE=import.meta.env.VITE_API_BASE_URL||'http://localhost:5000';
async function request(path,options={}){const res=await fetch(BASE+path,{credentials:'include',headers:{'Content-Type':'application/json',...(options.headers||{})},...options});const data=await res.json().catch(()=>({}));if(!res.ok)throw new Error(data.error||'Request failed.');return data}
export const api={get:p=>request(p),post:(p,b)=>request(p,{method:'POST',body:JSON.stringify(b)}),put:(p,b)=>request(p,{method:'PUT',body:JSON.stringify(b)})};
