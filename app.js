const form = document.querySelector('#screen-form');
const input = document.querySelector('#resumes');
const dropzone = document.querySelector('#dropzone');
const fileList = document.querySelector('#file-list');
const resultsSection = document.querySelector('#results-section');

function showFiles(files) {
  fileList.innerHTML = Array.from(files).map(file => `<span class="file-chip">${file.name}</span>`).join('');
}
input.addEventListener('change', () => showFiles(input.files));
['dragenter', 'dragover'].forEach(event => dropzone.addEventListener(event, e => { e.preventDefault(); dropzone.classList.add('dragover'); }));
['dragleave', 'drop'].forEach(event => dropzone.addEventListener(event, e => { e.preventDefault(); dropzone.classList.remove('dragover'); }));
dropzone.addEventListener('drop', e => { input.files = e.dataTransfer.files; showFiles(input.files); });

form.addEventListener('submit', async event => {
  event.preventDefault();
  const button = document.querySelector('#submit-button');
  button.disabled = true;
  button.innerHTML = 'Analyzing resumes <span>...</span>';
  try {
    const response = await fetch('/api/screen', { method: 'POST', body: new FormData(form) });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || 'Screening failed.');
    renderResults(payload.results);
  } catch (error) {
    window.alert(error.message);
  } finally {
    button.disabled = false;
    button.innerHTML = 'Screen candidates <span>→</span>';
  }
});

function renderResults(results) {
  document.querySelector('#result-count').textContent = `${results.length} candidate${results.length === 1 ? '' : 's'}`;
  document.querySelector('#top-score').textContent = `${results[0]?.score || 0}%`;
  document.querySelector('#strong-count').textContent = results.filter(result => result.score >= 75).length;
  document.querySelector('#results-list').innerHTML = results.map(result => `
    <article class="result-row">
      <span class="rank">0${result.rank}</span>
      <div><div class="candidate-name">${result.name}</div><div class="candidate-sub">${result.size.toLocaleString()} characters parsed · ${result.similarity}% semantic similarity</div></div>
      <div class="meter"><span style="width:${result.score}%"></span></div>
      <div class="score">${result.score}%<div class="status">${result.status}</div></div>
      <div class="tags">${result.matched_skills.map(skill => `<span class="tag">${skill}</span>`).join('')}${result.missing_skills.slice(0, 3).map(skill => `<span class="tag missing">− ${skill}</span>`).join('')}</div>
    </article>`).join('');
  resultsSection.classList.remove('hidden');
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
