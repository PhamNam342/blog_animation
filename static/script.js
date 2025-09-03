const dropzone = document.getElementById('dropzone');
const statusEl = document.getElementById('status');
const outImg = document.getElementById('outImg');
const downloadLink = document.getElementById('downloadLink');
const fileInput = document.getElementById('fileInput');
const convertBtn = document.getElementById('convertBtn');
const preview = document.getElementById('preview');
const actions = document.getElementById('actions');
const srcImg = document.getElementById('srcImg');
const result = document.getElementById('result');
const pickBtn = document.getElementById('pickBtn');
const shareBox = document.getElementById('shareBox');

let lastBlob = null; // để lưu ảnh đã convert

pickBtn.addEventListener("click", () => fileInput.click());

function setStatus(msg) {
  statusEl.textContent = msg || '';
}

fileInput.addEventListener('change', (e) => handleFiles(e.target.files));

dropzone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropzone.classList.add('dragover');
});
dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
dropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropzone.classList.remove('dragover');
  handleFiles(e.dataTransfer.files);
});

function handleFiles(files) {
  if (!files || !files[0]) return;
  const file = files[0];
  const url = URL.createObjectURL(file);
  srcImg.src = url;
  preview.classList.remove('hidden');
  actions.classList.remove('hidden');
  result.classList.add('hidden');
  outImg.src = '';
  downloadLink.style.display = 'none';
  shareBox.classList.add('hidden');
  lastBlob = null;
  setStatus('');
  convertBtn.onclick = () => uploadAndConvert(file);
}

async function uploadAndConvert(file) {
  setStatus('Đang xử lý...');
  convertBtn.disabled = true;
  try {
    const form = new FormData();
    form.append('image', file);
    const res = await fetch('/cartoonize', { method: 'POST', body: form });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || ('HTTP ' + res.status));
    }

    const blob = await res.blob();
    lastBlob = blob; // lưu lại để share
    const url = URL.createObjectURL(blob);
    outImg.src = url;
    outImg.alt = 'Kết quả';
    downloadLink.href = url;
    downloadLink.style.display = 'inline-block';
    result.classList.remove('hidden');
    shareBox.classList.remove('hidden');

    setStatus('Hoàn tất.');
  } catch (e) {
    outImg.alt = '❌ Lỗi: ' + e.message;
    setStatus('');
  } finally {
    convertBtn.disabled = false;
  }
}

document.getElementById('shareBtn').addEventListener('click', async () => {
  if (!lastBlob) return alert("Chưa có ảnh để chia sẻ");
  const formData = new FormData();
  const uniqueName = `cartoon_${crypto.randomUUID()}.png`;
  formData.append('image', lastBlob, uniqueName);

  formData.append('content', document.getElementById('shareContent').value);

  try {
    const res = await fetch('/share_to_blog', { method: 'POST', body: formData });
    if (res.ok) {
      alert('Ảnh đã chia sẻ lên blog!');
    } else {
      const text = await res.text();
      alert('Lỗi chia sẻ: ' + text);
    }
  } catch (err) {
    alert('❌ ' + err.message);
  }
});