import React, { useState } from 'react'
import './VideoUpload.css'

// Displays a drag-and-drop area for uploading a video and tracking its upload state
export default function VideoUpload({ onAnalyze }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  // Handles the file input change event
  const handleFileChange = (event) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0])
    }
  }

  // Triggers the analysis process
  const handleAnalyzeClick = async () => {
    if (selectedFile) {
      setIsAnalyzing(true)
      try {
        await onAnalyze(selectedFile)
      } finally {
        setIsAnalyzing(false)
      }
    }
  }

  return (
    <div className="upload-container">
      <div className="drag-area">
        <p>Drag and drop a video file here, or click to select</p>
        <input 
          type="file" 
          accept="video/mp4,video/x-m4v,video/*" 
          onChange={handleFileChange}
          disabled={isAnalyzing}
        />
      </div>
      
      {selectedFile && (
        <div className="file-info">
          <p>Selected File: {selectedFile.name}</p>
        </div>
      )}

      {selectedFile && !isAnalyzing && (
        <button className="analyze-button" onClick={handleAnalyzeClick}>
          Analyze Video
        </button>
      )}

      {isAnalyzing && (
        <div className="loading-state">
          <p className="loading-text">Analyzing 15 frames...</p>
        </div>
      )}
    </div>
  )
}
