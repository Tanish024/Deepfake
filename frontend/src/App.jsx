import React, { useState } from 'react'
import { analyzeVideo } from './api/client'
import VideoUpload from './components/VideoUpload'
import VerdictCard from './components/VerdictCard'
import './App.css'

// Main application component connecting the video upload and verdict display
export default function App() {
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  // Handles the video upload process internally updating state
  const handleAnalyze = async (file) => {
    setError(null)
    setResult(null)
    try {
      const responseData = await analyzeVideo(file)
      setResult(responseData)
    } catch (err) {
      let errorMessage = err.message
      if (!errorMessage) {
          errorMessage = 'Failed to analyze video.'
      }
      setError(errorMessage)
    }
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Deepfake Shield 🛡</h1>
        <p>Real-time deepfake video detection</p>
      </header>

      <main className="app-main">
        <VideoUpload onAnalyze={handleAnalyze} />
        
        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
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
    </div>
  )
}
