import React, { useState, useRef } from 'react'
import './VideoUpload.css'

export default function VideoUpload({ onAnalyze }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isDragOver, setIsDragOver] = useState(false)
  const inputRef = useRef(null)

  const handleFileChange = (event) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0])
    }
  }

  // Real drag-and-drop handlers
  const handleDragOver = (event) => {
    event.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = () => {
    setIsDragOver(false)
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setIsDragOver(false)
    const droppedFile = event.dataTransfer.files[0]
    if (droppedFile) {
      setSelectedFile(droppedFile)
    }
  }

  const handleAnalyzeClick = async () => {
    if (!selectedFile) return
    setIsAnalyzing(true)
    try {
      await onAnalyze(selectedFile)
      // Clear selection after analysis so user can easily run another
      setSelectedFile(null)
      if (inputRef.current) inputRef.current.value = ''
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="upload-container">
      <div
        className={`drag-area${isDragOver ? ' drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <p>Drag and drop a video file here, or click to select</p>
        <input
          ref={inputRef}
          type="file"
          accept="video/mp4,video/webm,video/quicktime,video/*"
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
          <p className="loading-text">Analyzing frames…</p>
        </div>
      )}
    </div>
  )
}
