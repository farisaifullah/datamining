let fileData = null;

function uploadFile() {
  const input = document.getElementById('fileInput');
  if (!input.files.length) {
    alert('Pilih file CSV terlebih dahulu!');
    return;
  }
  const formData = new FormData();
  formData.append('file', input.files[0]);
  fetch('/upload', { method: 'POST', body: formData })
    .then(res => res.json())
    .then(data => {
      fileData = data;
      showPreview(data);
      document.querySelector('.mining-box').style.display = 'flex';
      document.getElementById('resetBtn').style.display = 'block';
      document.getElementById('result').innerHTML = "";
    })
    .catch(err => {
      document.getElementById('preview').innerHTML = "Gagal upload file. Pastikan format CSV benar.";
      document.querySelector('.mining-box').style.display = 'none';
      document.getElementById('resetBtn').style.display = 'none';
    });
}

function showPreview(data) {
  if (!data || !data.rows || !data.columns) {
    document.getElementById('preview').innerHTML = "Tidak ada data untuk preview.";
    return;
  }
  let html = '<div class="table-scroll"><table><thead><tr>';
  for (const col of data.columns) html += `<th>${col}</th>`;
  html += '</tr></thead><tbody>';
  for (const row of data.rows) {
    html += '<tr>';
    for (const col of data.columns) html += `<td>${row[col]}</td>`;
    html += '</tr>';
  }
  html += '</tbody></table></div>';
  html += '<p><strong>Preview 10 baris pertama data Titanic Anda.</strong></p>';
  document.getElementById('preview').innerHTML = html;
}

document.getElementById('method').addEventListener('change', function() {
  const method = this.value;
  document.getElementById('clusterCount').style.display = method === 'kmeans' ? 'inline-block' : 'none';
});

function runMining() {
  const method = document.getElementById('method').value;
  if (!method) {
    alert('Pilih metode data mining terlebih dahulu.');
    return;
  }
  let params = {};
  if (method === 'kmeans') {
    params.n_clusters = parseInt(document.getElementById('clusterCount').value) || 2;
  }
  fetch('/mining', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ method, params })
  })
    .then(res => res.json())
    .then(data => showResult(method, data))
    .catch(err => {
      document.getElementById('result').innerHTML = "Gagal melakukan analisis data mining.";
    });
}

function showResult(method, data) {
  let html = '';
  if (data.error) {
    html = `<div class="explain">${data.error}</div>`;
  } else if (method === "decision_tree") {
    html += `<h3>Klasifikasi (Decision Tree)</h3>
      <div class="explain">${data.explanation}</div>
      <div class="table-scroll"><table><thead><tr><th>Kolom</th><th>Pentingnya</th></tr></thead><tbody>`;
    for (const [col, val] of Object.entries(data.feature_importances)) {
      html += `<tr><td>${col}</td><td>${val.toFixed(3)}</td></tr>`;
    }
    html += '</tbody></table></div>';
    html += `<ul>
      <li>Semakin besar angka pada "Pentingnya", semakin berpengaruh kolom tersebut untuk memprediksi siapa yang selamat.</li>
      <li>Misal, kolom "Pclass" penting berarti kelas penumpang sangat mempengaruhi peluang selamat.</li>
    </ul>`;
  } else if (method === "kmeans") {
    html += `<h3>Clustering (K-Means)</h3>
      <div class="explain">${data.explanation}</div>
      <div class="table-scroll"><table><thead><tr><th>Penumpang ke-</th><th>Cluster</th></tr></thead><tbody>`;
    data.labels.forEach((label, i) => {
      html += `<tr><td>${i+1}</td><td>${label}</td></tr>`;
    });
    html += '</tbody></table></div>';
    html += `<ul>
      <li>Cluster adalah kelompok penumpang dengan data yang mirip.</li>
      <li>Angka cluster menunjukkan kelompok mana penumpang tersebut masuk.</li>
    </ul>`;
  } else if (method === "linear_regression") {
    html += `<h3>Regresi (Linear Regression)</h3>
      <div class="explain">${data.explanation}</div>
      <div class="table-scroll"><table><thead><tr><th>Kolom</th><th>Koefisien</th></tr></thead><tbody>`;
    for (const [col, val] of Object.entries(data.coeff)) {
      html += `<tr><td>${col}</td><td>${val.toFixed(3)}</td></tr>`;
    }
    html += '</tbody></table></div>';
    html += `<ul>
      <li>Koefisien positif: faktor menaikkan harga tiket.</li>
      <li>Koefisien negatif: faktor menurunkan harga tiket.</li>
      <li>Bandingkan angka untuk tahu faktor paling berpengaruh.</li>
    </ul>`;
  }
  // Tampilkan visualisasi jika ada
  if (data.visual) {
    html += `<div><img src="${data.visual}" style="max-width:100%;border-radius:10px;margin:12px 0;" alt="Visualisasi ${method}"></div>`;
  }
  document.getElementById('result').innerHTML = html;
}

function resetAll() {
  fileData = null;
  document.getElementById('fileInput').value = '';
  document.getElementById('preview').innerHTML = '';
  document.getElementById('result').innerHTML = '';
  document.querySelector('.mining-box').style.display = 'none';
  document.getElementById('resetBtn').style.display = 'none';
}