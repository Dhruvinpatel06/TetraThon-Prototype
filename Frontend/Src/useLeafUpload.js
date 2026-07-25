import { useState } from 'react'
import { api } from './api'

export function useLeafUpload() {
  const [leafResult, setLeafResult] = useState(null)
  const [isClassifying, setIsClassifying] = useState(false)

  const handleLeafUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    if (!file.type.startsWith('image/')) {
      setLeafResult({ error: 'Selected file must be an image (JPEG, PNG, BMP)' })
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      setLeafResult({ error: 'File size exceeds 10MB limit' })
      return
    }

    setIsClassifying(true)
    setLeafResult(null)
    try {
      const result = await api.postLeafClassify(file)
      setLeafResult(result)
    } catch (err) {
      setLeafResult({ error: err.message || 'Classification failed' })
    } finally {
      setIsClassifying(false)
    }
  }

  return { leafResult, isClassifying, handleLeafUpload, setLeafResult }
}
