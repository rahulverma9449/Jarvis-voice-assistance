import { useEffect, useRef, useState } from 'react'

export default function FoodScanner({ open, onClose }) {
  const videoRef = useRef(null)
  const streamRef = useRef(null)
  const [error, setError] = useState('')
  const [captured, setCaptured] = useState(null)

  useEffect(() => {
    if (!open) return undefined
    let active = true
    setError('')
    setCaptured(null)
    navigator.mediaDevices?.getUserMedia({ video: { facingMode: 'environment' }, audio: false })
      .then((stream) => {
        if (!active) { stream.getTracks().forEach((track) => track.stop()); return }
        streamRef.current = stream
        if (videoRef.current) videoRef.current.srcObject = stream
      })
      .catch(() => setError('Camera access was denied or is unavailable.'))
    return () => {
      active = false
      streamRef.current?.getTracks().forEach((track) => track.stop())
      streamRef.current = null
    }
  }, [open])

  if (!open) return null

  const capture = () => {
    const video = videoRef.current
    if (!video || video.readyState < 2) return
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext('2d').drawImage(video, 0, 0)
    setCaptured(canvas.toDataURL('image/jpeg', 0.9))
  }

  return <section className="panel food-scanner" aria-label="Food and product scanner">
    <div className="panel-heading"><span>FOOD / PRODUCT SCANNER</span><button type="button" onClick={onClose} aria-label="Close scanner">CLOSE</button></div>
    {error ? <p className="scanner-message">{error}</p> : captured ? <img className="scanner-capture" src={captured} alt="Captured food or product" /> : <video ref={videoRef} autoPlay playsInline muted />}
    <div className="scanner-controls">{captured ? <button type="button" onClick={() => setCaptured(null)}>SCAN AGAIN</button> : <button type="button" onClick={capture} disabled={Boolean(error)}>CAPTURE ITEM</button>}</div>
  </section>
}
