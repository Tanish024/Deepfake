import React, { useState } from 'react'
import { analyzeVideo } from './api/client'
import VideoUpload from './components/VideoUpload'
import VerdictCard from './components/VerdictCard'
import './App.css'

export default function App() {
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleAnalyze = async (file) => {
    setError(null)
    setResult(null)
    try {
      const responseData = await analyzeVideo(file)
      setResult(responseData)
    } catch (err) {
      let errorMessage = err.message
      if (!errorMessage) {
          errorMessage = 'CRITICAL FAILURE: ANALYSIS ABORTED'
      }
      setError(errorMessage)
    }
  }

  return (
    <div className="app-container">
      <div className="cyber-fluff-top pulsing">
        <span>SYS.CORE.OVR // SECURE TERMINAL</span>
        <span className="barcode">||| |||| | || |||||</span>
        <span>ACCESS: GRANTED</span>
      </div>

      <header className="app-header glitch-text">
        <h1>DEEPFAKE_SHIELD</h1>
        <p>FORENSIC VIDEO ANALYSIS v2.4</p>
      </header>

      <main className="app-main">
        <VideoUpload onAnalyze={handleAnalyze} />
        
        {error && (
          <div className="error-message glitch-text">
            <p>WARNING: {error}</p>
          </div>
        )}

        {result && (
          <VerdictCard 
            verdict={result.verdict}
            confidence={result.confidence}
            suspicious_frames={result.suspicious_frames}
          />
        )}
      </main>

      <footer className="app-footer">
        <span>ROOT@SYNTHETIC_ORACLE:~#</span>
        <span>Contact: <a href="mailto:tanishkhatri002@gmail.com" className="footer-link">tanishkhatri002@gmail.com</a></span>
        <span>STATUS: ONLINE</span>
      </footer>
    </div>
  )
}
