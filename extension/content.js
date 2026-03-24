// Content script — injected into every page at document_idle.
// Finds the first <video> element, downloads its source, and sends it to the
// Deepfake Shield backend as a file upload. Shows a result badge on the video.

const BACKEND_URL = 'http://localhost:5000/analyze';

// ─── Badge helpers ────────────────────────────────────────────────────────────

// Creates and positions a badge in the top-left corner of a video element.
// Returns the badge element so it can be updated later.
function createBadge(videoElement) {
  const badge = document.createElement('div');

  // Wrap the video in a positioned container so the badge can be placed on top.
  // Only wrap if the video's parent isn't already our wrapper.
  const parent = videoElement.parentElement;
  const wrapper = document.createElement('div');
  wrapper.style.cssText = 'position:relative;display:inline-block;';

  parent.insertBefore(wrapper, videoElement);
  wrapper.appendChild(videoElement);
  wrapper.appendChild(badge);

  // Base badge styles — no inline colour yet, that is set per-state.
  badge.style.cssText = [
    'position:absolute',
    'top:8px',
    'left:8px',
    'padding:4px 10px',
    'border-radius:4px',
    'font-size:13px',
    'font-weight:bold',
    'font-family:sans-serif',
    'pointer-events:none',
    'z-index:9999',
    'opacity:0.92',
  ].join(';');

  return badge;
}

// Updates the badge text and colour for the "analysing" state.
function setBadgeLoading(badge) {
  badge.textContent = '🔍 Analyzing...';
  badge.style.background = '#6b7280'; // grey
  badge.style.color = '#ffffff';
}

// Updates the badge text and colour once a result is available.
function setBadgeResult(badge, verdict, confidence) {
  if (verdict === 'FAKE') {
    badge.textContent = '⚠️ FAKE – ' + confidence + '% confidence';
    badge.style.background = '#dc2626'; // red
    badge.style.color = '#ffffff';
  } else {
    badge.textContent = '✅ REAL – ' + confidence + '% confidence';
    badge.style.background = '#16a34a'; // green
    badge.style.color = '#ffffff';
  }
}

// Updates the badge when something goes wrong.
function setBadgeError(badge, message) {
  badge.textContent = '❌ ' + message;
  badge.style.background = '#374151'; // dark grey
  badge.style.color = '#ffffff';
}

// ─── Video fetching ───────────────────────────────────────────────────────────

// Downloads the video from the given URL and returns a Blob.
// Returns null if the fetch fails.
async function fetchVideoBlob(videoSrc) {
  try {
    const response = await fetch(videoSrc);
    if (!response.ok) {
      console.warn('[Deepfake Shield] Could not fetch video:', response.status);
      return null;
    }
    const blob = await response.blob();
    return blob;
  } catch (err) {
    console.warn('[Deepfake Shield] Fetch error:', err);
    return null;
  }
}

// ─── Backend communication ────────────────────────────────────────────────────

// Sends the video blob to the backend as multipart/form-data (same format as the
// main frontend upload). Returns the parsed JSON result, or null on failure.
async function sendToBackend(videoBlob, filename) {
  try {
    const formData = new FormData();
    formData.append('video', videoBlob, filename);

    const response = await fetch(BACKEND_URL, {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      console.warn('[Deepfake Shield] Backend error:', data.error);
      return null;
    }

    return data;
  } catch (err) {
    console.warn('[Deepfake Shield] Backend request failed:', err);
    return null;
  }
}

// ─── Main ─────────────────────────────────────────────────────────────────────

// Entry point — finds the first video, attaches a badge, and runs analysis.
async function analyzeFirstVideo() {
  // Step 1: Find the first <video> element on the page.
  const videoElement = document.querySelector('video');

  if (!videoElement) {
    console.debug('[Deepfake Shield] No <video> element found on this page.');
    return;
  }

  // Step 2: Get the video src URL (currentSrc is the one actually playing;
  // it falls back to the src attribute if currentSrc is empty).
  const videoSrc = videoElement.currentSrc || videoElement.getAttribute('src');

  if (!videoSrc) {
    console.debug('[Deepfake Shield] Video element has no src.');
    return;
  }

  console.debug('[Deepfake Shield] Found video src:', videoSrc);

  // Attach the badge to the video element and show the loading state.
  const badge = createBadge(videoElement);
  setBadgeLoading(badge);

  // Step 3: Download the video as a binary blob.
  const videoBlob = await fetchVideoBlob(videoSrc);

  if (!videoBlob) {
    setBadgeError(badge, 'Could not load video');
    return;
  }

  // Derive a filename with an extension so the backend can detect the codec.
  const srcPath = videoSrc.split('?')[0]; // strip query string
  const detectedExtension = srcPath.substring(srcPath.lastIndexOf('.')) || '.mp4';
  const uploadFilename = 'video' + detectedExtension;

  // Step 4: POST the blob to the backend and get the analysis result.
  const result = await sendToBackend(videoBlob, uploadFilename);

  if (!result || result.error) {
    const errorMessage = (result && result.error) ? result.error : 'Analysis failed';
    setBadgeError(badge, errorMessage);
    return;
  }

  // Step 5: Update the badge with the verdict.
  setBadgeResult(badge, result.verdict, result.confidence);
  console.debug('[Deepfake Shield] Result:', result);
}

// Kick off analysis.
analyzeFirstVideo();
