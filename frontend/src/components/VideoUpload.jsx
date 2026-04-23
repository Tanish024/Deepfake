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
        <p>DROP_TARGET // VIDEO_INPUT_STREAM</p>
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
          <p>LOADED_PAYLOAD: {selectedFile.name}</p>
        </div>
      )}

      {selectedFile && !isAnalyzing && (
        <button className="analyze-button" onClick={handleAnalyzeClick}>
          BREACH_PROTOCOL
        </button>
      )}

      {isAnalyzing && (
        <div className="loading-state">
          <p className="loading-text glitch-text">EXTRACTING_FRAMES // NEURAL_NET_ENGAGED</p>
          <div className="progress-bar-container">
            <div className="progress-bar-fill"></div>
          </div>
        </div>
      )}
    </div>
  )
}
