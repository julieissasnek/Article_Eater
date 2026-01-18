
(async function(){
  const res = await fetch('/interactions/review');
  const data = await res.json();
  const root = document.getElementById('list');
  root.innerHTML = '';
  for(const it of data.pending){
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `<h3>${it.t}</h3>
      <p><strong>Rule A:</strong> ${it.a} | <strong>Rule B:</strong> ${it.b}</p>
      <p><em>${it.notes||''}</em></p>`;
    root.appendChild(card);
  }
})();