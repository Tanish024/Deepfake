import React from 'react'
import './VerdictCard.css'

// Displays the deepfake analysis verdict, confidence, and suspicious frame details
export default function VerdictCard({ verdict, confidence, suspicious_frames }) {
  let isFake = false
  if (verdict === 'FAKE') {
      isFake = true
  }
  
  let cardClassName = 'verdict-card '
  if (isFake) {
      cardClassName = cardClassName + 'fake-card'
  } else {
      cardClassName = cardClassName + 'real-card'
  }

  return (
    <div className={cardClassName}>
      <div className="verdict-header">
        {isFake && <h2 className="fake-text">⚠️ FAKE DETECTED</h2>}
        {!isFake && <h2 className="real-text">✅ REAL VIDEO</h2>}
      </div>

      <div className="confidence-section">
        <label className="confidence-label" htmlFor="confidence-bar">Confidence: {confidence}%</label>
        <progress 
            id="confidence-bar"
            className="confidence-progress" 
            value={confidence} 
            max="100"
        ></progress>
      </div>

      {suspicious_frames && suspicious_frames.length > 0 && (
        <div className="frames-section">
          <h3>Suspicious Frames Found:</h3>
          <ul className="frames-list">
            {suspicious_frames.map(frame => (
              <li key={frame} className="frame-item">Frame #{frame}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
