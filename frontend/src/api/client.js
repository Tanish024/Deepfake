// Analyzes a video by posting it to the Flask backend endpoint
export const analyzeVideo = async (file) => {
  let apiUrl = import.meta.env.VITE_API_URL
  if (!apiUrl) {
    apiUrl = 'http://localhost:5000'
  }
  
  const formData = new FormData()
  formData.append('video', file)

  try {
    const response = await fetch(`${apiUrl}/analyze`, {
      method: 'POST',
      body: formData,
    })
    
    // Check if the response is ok (status in the range 200-299)
    if (!response.ok) {
        const errorData = await response.json()
        let errorMessage = errorData.error
        if (!errorMessage) {
            errorMessage = 'Server error occurred'
        }
        throw new Error(errorMessage)
    }
    
    return await response.json()
  } catch (error) {
    console.error('Error analyzing video:', error)
    throw error
  }
}
