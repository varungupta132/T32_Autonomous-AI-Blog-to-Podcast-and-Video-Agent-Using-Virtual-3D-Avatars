"""Patch index.html to add video generation UI."""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add video CSS before </style>
video_css = """
video{width:100%;border-radius:14px;margin-bottom:16px;background:#000}
.btn-video{background:linear-gradient(135deg,#f59e0b,#d97706);color:#fff;box-shadow:0 0 18px rgba(245,158,11,0.35)}
.btn-video:hover{box-shadow:0 0 28px rgba(245,158,11,0.55);transform:translateY(-1px)}
.btn-video:disabled{opacity:0.5;cursor:not-allowed;transform:none;box-shadow:none}
#video-progress-section{display:none;margin-top:20px}
#video-result-section{display:none;margin-top:20px}
.video-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.3);color:#fbbf24;font-size:0.75rem;padding:3px 10px;border-radius:50px;margin-left:8px}
"""
html = html.replace('</style>', video_css + '</style>', 1)

# 2. Add Generate Video button after download button in result-actions
video_btn = (
    '<div class="divider"></div>'
    '<div class="section-label">🎬 Avatar Video <span class="video-badge">✨ Free · GPU</span></div>'
    '<p style="font-size:0.82rem;color:var(--muted);margin-bottom:12px">Generate a real podcast video with talking avatars using Wav2Lip. Takes ~2-5 min.</p>'
    '<button class="btn btn-video btn-full" onclick="generateVideo()" id="gen-video-btn">🎬 Generate Avatar Video</button>'
    '<div id="video-status"></div>'
)
html = html.replace(
    '<a id="download-btn" class="btn btn-cyan" href="#" download>⬇️ Download MP3</a>',
    '<a id="download-btn" class="btn btn-cyan" href="#" download>⬇️ Download MP3</a>' + video_btn
)

# 3. Add video progress + result sections before /panel-studio comment
video_sections = """
        <!-- Video Progress -->
        <div id="video-progress-section" class="card">
          <div class="section-label">🎬 Generating Avatar Video</div>
          <div class="progress-label" id="video-progress-label">Initializing Wav2Lip...</div>
          <div class="progress-bar-wrap">
            <div class="progress-bar-fill" id="video-progress-bar" style="background:linear-gradient(90deg,#f59e0b,#d97706)"></div>
          </div>
          <p style="font-size:0.78rem;color:var(--muted);margin-top:8px">⚡ Using RTX 3050 GPU · This may take a few minutes</p>
        </div>

        <!-- Video Result -->
        <div id="video-result-section" class="card">
          <div class="section-label">🎬 Your Avatar Podcast Video is Ready</div>
          <div class="stats-row">
            <div class="stat-box"><div class="stat-val" id="vstat-segments">—</div><div class="stat-lbl">Segments</div></div>
            <div class="stat-box"><div class="stat-val" id="vstat-speakers">—</div><div class="stat-lbl">Speakers</div></div>
            <div class="stat-box"><div class="stat-val" id="vstat-size">—</div><div class="stat-lbl">Size</div></div>
          </div>
          <video id="result-video" controls></video>
          <div class="result-actions">
            <a id="video-download-btn" class="btn btn-video" href="#" download>⬇️ Download MP4</a>
            <button class="btn btn-ghost" onclick="newPodcast()">🎙️ New Podcast</button>
          </div>
        </div>
"""
html = html.replace(
    '    </div><!-- /panel-studio -->',
    video_sections + '    </div><!-- /panel-studio -->'
)

# 4. Add JS before </script>
video_js = """
// ── Generate Video ────────────────────────────────────────────────────────
async function generateVideo() {
  const script = document.getElementById('script-textarea').value.trim();
  const name = document.getElementById('file-name').value.trim() || 'podcast-episode';
  if (!script) { alert('Script is empty.'); return; }

  const btn = document.getElementById('gen-video-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Generating Video...';

  document.getElementById('video-progress-section').style.display = 'block';
  document.getElementById('video-result-section').style.display = 'none';
  document.getElementById('video-status').innerHTML = '';
  setVideoProgress(5, 'Generating audio segments...');

  let fakePct = 5;
  const msgs = ['Running Wav2Lip lip-sync...','Processing face detection...','Rendering avatar frames...','Composing video segments...','Mixing audio...','Almost done...'];
  const fakeTimer = setInterval(() => {
    if (fakePct < 85) {
      fakePct += Math.random() * 2.5;
      setVideoProgress(Math.min(fakePct, 85), msgs[Math.floor(fakePct / 15) % msgs.length]);
    }
  }, 3000);

  try {
    const res = await fetch('/api/generate-video', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ script, name, language: state.language })
    });
    const data = await res.json();
    clearInterval(fakeTimer);
    if (data.success) {
      setVideoProgress(100, '✅ Video ready!');
      showVideoResult(data);
    } else {
      setVideoProgress(0, '❌ ' + escapeText(data.error || 'Video generation failed'));
      document.getElementById('video-status').innerHTML = '<div class="status-msg error">' + escapeHTML(data.error || 'Failed') + '</div>';
      btn.disabled = false;
      btn.innerHTML = '🎬 Generate Avatar Video';
    }
  } catch (err) {
    clearInterval(fakeTimer);
    setVideoProgress(0, '❌ Network error');
    btn.disabled = false;
    btn.innerHTML = '🎬 Generate Avatar Video';
  }
}

function setVideoProgress(pct, label) {
  document.getElementById('video-progress-bar').style.width = pct + '%';
  document.getElementById('video-progress-label').textContent = label;
}

function showVideoResult(data) {
  document.getElementById('vstat-segments').textContent = data.total_segments || '—';
  document.getElementById('vstat-speakers').textContent = data.speakers || '—';
  document.getElementById('vstat-size').textContent = data.file_size || '—';
  const video = document.getElementById('result-video');
  video.src = '/api/stream-video/' + encodeURIComponent(data.filename);
  const dlBtn = document.getElementById('video-download-btn');
  dlBtn.href = '/api/download-video/' + encodeURIComponent(data.filename);
  dlBtn.download = data.filename;
  document.getElementById('video-result-section').style.display = 'block';
  const btn = document.getElementById('gen-video-btn');
  btn.disabled = false;
  btn.innerHTML = '🎬 Generate Avatar Video';
}
"""
html = html.replace('</script>', video_js + '</script>', 1)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done! New length:', len(html))
