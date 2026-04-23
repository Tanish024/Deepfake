import React from 'react'
import './VerdictCard.css'

export default function VerdictCard({ verdict, confidence, suspicious_frames }) {
  const isFake = verdict === 'FAKE'
  const cardClassName = `verdict-card ${isFake ? 'fake-card' : 'real-card'}`

  return (
    <div className={cardClassName}>
      <div className="verdict-header">
        {isFake && <h2 className="fake-text">⚠ THREAT_DETECTED ⚠</h2>}
        {!isFake && <h2 className="real-text">✔ SAFE_ORIGIN ✔</h2>}
      </div>

      <div className="confidence-section">
        <label className="confidence-label" htmlFor="confidence-bar">PROBABILITY_MATRIX: {confidence}%</label>
        <progress 
            id="confidence-bar"
            className="confidence-progress" 
            value={confidence} 
            max="100"
        ></progress>
      </div>

      {suspicious_frames && suspicious_frames.length > 0 && (
        <div className="frames-section">
          <h3>CORRUPT_PACKETS_LOCATED:</h3>
          <ul className="frames-list">
            {suspicious_frames.map(frame => (
              <li key={frame} className="frame-item">IDX_#{frame}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
