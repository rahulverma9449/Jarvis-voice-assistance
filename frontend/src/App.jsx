import { useCallback, useEffect, useRef, useState } from 'react'
import JarvisRobot from './components/JarvisRobot'
import Sidebar from './components/Sidebar'
import CommandCenter from './components/CommandCenter'
import QuickActions from './components/QuickActions'
import SystemMonitor from './components/SystemMonitor'
import HistoryPanel from './components/HistoryPanel'
import BrowserDataPanel from './components/BrowserDataPanel'
import CommandLibrary from './components/CommandLibrary'
import FoodScanner from './components/FoodScanner'
import WorkspacePanel from './components/WorkspacePanel'
import './App.css'

export default function App() {
  const [command, setCommand] = useState('')
  const [reply, setReply] = useState('All systems are ready. Tap the microphone or say “Hi Jarvis”.')
  const [status, setStatus] = useState('connecting')
  const [listening, setListening] = useState(false)
  const [voiceSupported, setVoiceSupported] = useState(false)
  const [wakeEnabled, setWakeEnabled] = useState(false)
  const [busy, setBusy] = useState(false)
  const [history, setHistory] = useState([])
  const [browserData, setBrowserData] = useState([])
  const [capabilities, setCapabilities] = useState([])
  const [categories, setCategories] = useState([])
  const [system, setSystem] = useState(null)
  const [generatedImage, setGeneratedImage] = useState(null)
  const [scannerOpen, setScannerOpen] = useState(false)
  const [timer, setTimer] = useState(null)
  const [workspaceData, setWorkspaceData] = useState({ summary: null, notes: [], reminders: [], suggestions: [] })
  const recognitionRef = useRef(null)
  const busyRef = useRef(false)
  const wakeEnabledRef = useRef(false)
  const awaitingCommandRef = useRef(false)
  const speakingRef = useRef(false)
  const sendCommandRef = useRef(null)
  const startRecognitionRef = useRef(null)

  const loadData = useCallback(async () => {
    const requests = [
      fetch('/api/history?limit=12').then((r) => r.ok ? r.json() : []),
      fetch('/api/browser-data?limit=12').then((r) => r.ok ? r.json() : []),
      fetch('/api/capabilities').then((r) => r.ok ? r.json() : { items: [] }),
      fetch('/api/capabilities/categories').then((r) => r.ok ? r.json() : []),
      fetch('/api/system').then((r) => r.ok ? r.json() : null),
      fetch('/api/v2/analytics/summary').then((r) => r.ok ? r.json() : null),
      fetch('/api/v2/notes').then((r) => r.ok ? r.json() : []),
      fetch('/api/v2/reminders').then((r) => r.ok ? r.json() : []),
      fetch('/api/v2/commands/suggestions?limit=6').then((r) => r.ok ? r.json() : []),
    ]
    try {
      const [recent, browser, catalog, groups, machine, summary, notes, reminders, suggestions] = await Promise.all(requests)
      setHistory(recent.reverse())
      setBrowserData(browser.reverse())
      setCapabilities(catalog.items)
      setCategories(groups)
      setSystem(machine)
      setWorkspaceData({ summary, notes, reminders, suggestions })
    } catch { /* Keep the current view while reconnecting. */ }
  }, [])

  const startRecognition = useCallback(() => {
    if (!recognitionRef.current || speakingRef.current) return
    try { recognitionRef.current.start() } catch { /* Recognition is already active. */ }
  }, [])
  startRecognitionRef.current = startRecognition

  const speak = useCallback((text) => {
    if (!('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()
    speakingRef.current = true
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'en-IN'
    utterance.rate = 1.04
    utterance.pitch = 0.94
    const voices = window.speechSynthesis.getVoices()
    utterance.voice = voices.find((voice) => /en-IN|Google UK English Male|Microsoft Ravi/i.test(`${voice.lang} ${voice.name}`)) || voices.find((voice) => voice.lang.startsWith('en')) || null
    utterance.onend = () => {
      speakingRef.current = false
      if (wakeEnabledRef.current) window.setTimeout(() => startRecognitionRef.current?.(), 200)
    }
    utterance.onerror = () => { speakingRef.current = false }
    window.speechSynthesis.speak(utterance)
  }, [])

  const startTimer = useCallback((seconds) => {
    const endsAt = Date.now() + seconds * 1000
    setTimer({ seconds, remaining: seconds, endsAt })
  }, [])

  const sendCommand = useCallback(async (value) => {
    const cleanCommand = (value ?? '').trim()
    if (!cleanCommand || busyRef.current) return
    busyRef.current = true
    setBusy(true)
    setCommand(cleanCommand)
    setReply('Thinking through your request…')
    try {
      const response = await fetch('/api/command', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ command: cleanCommand }) })
      if (!response.ok) throw new Error('Backend request failed')
      const data = await response.json()
      setReply(data.reply)
      setStatus('online')
      if (data.action === 'scan_food') setScannerOpen(true)
      if (data.action === 'show_image' && data.url) setGeneratedImage({ url: data.url, prompt: cleanCommand })
      if (data.action === 'open_url' && data.url) window.open(data.url, '_blank', 'noopener,noreferrer')
      if (data.action === 'start_timer' && data.url) startTimer(Number(data.url))
      speak(data.reply)
      const recent = await fetch('/api/history?limit=12').then((r) => r.json())
      setHistory(recent.reverse())
    } catch {
      setStatus('offline')
      setReply('I cannot reach the Jarvis API. The backend may need to be restarted.')
    } finally {
      busyRef.current = false
      setBusy(false)
    }
  }, [speak, startTimer])
  sendCommandRef.current = sendCommand

  useEffect(() => {
    fetch('/api/health').then((response) => {
      if (!response.ok) throw new Error()
      setStatus('online')
    }).catch(() => setStatus('offline'))
    loadData()
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) return
    setVoiceSupported(true)
    const recognition = new SpeechRecognition()
    recognition.lang = 'en-IN'
    recognition.interimResults = true
    recognition.continuous = false
    recognition.maxAlternatives = 3
    recognition.onstart = () => setListening(true)
    recognition.onresult = (event) => {
      let transcript = ''
      let final = false
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        transcript += event.results[i][0].transcript
        final ||= event.results[i].isFinal
      }
      transcript = transcript.trim()
      setCommand(transcript)
      if (!final) return
      const normalized = transcript.toLowerCase()
      if (wakeEnabledRef.current && /\b(hi|hey|hello)\s+jarvis\b/.test(normalized)) {
        const remainder = transcript.replace(/^.*?\b(hi|hey|hello)\s+jarvis\b[,.]?\s*/i, '').trim()
        if (remainder) sendCommandRef.current?.(remainder)
        else {
          awaitingCommandRef.current = true
          setReply('I’m listening. What can I do for you?')
          speak('Hi Rahul. What can I do for you?')
          fetch('/api/wake', { method: 'POST' }).catch(() => {})
        }
      } else if (wakeEnabledRef.current && awaitingCommandRef.current) {
        awaitingCommandRef.current = false
        sendCommandRef.current?.(transcript)
      } else if (!wakeEnabledRef.current) sendCommandRef.current?.(transcript)
    }
    recognition.onend = () => {
      setListening(false)
      if (wakeEnabledRef.current && !speakingRef.current) window.setTimeout(() => startRecognitionRef.current?.(), 300)
    }
    recognition.onerror = (event) => {
      setListening(false)
      if (['not-allowed', 'service-not-allowed'].includes(event.error)) {
        wakeEnabledRef.current = false
        setWakeEnabled(false)
        setReply('Microphone access is blocked. Allow microphone permission in Chrome or Edge, then tap the mic again.')
      }
    }
    recognitionRef.current = recognition
    return () => { wakeEnabledRef.current = false; recognition.abort(); window.speechSynthesis?.cancel() }
  }, [loadData, speak])

  useEffect(() => {
    if (!timer) return
    const tick = window.setInterval(() => {
      const remaining = Math.max(0, Math.ceil((timer.endsAt - Date.now()) / 1000))
      setTimer((current) => current ? { ...current, remaining } : null)
      if (remaining === 0) {
        window.clearInterval(tick)
        setReply('Your timer is complete.')
        speak('Rahul, your timer is complete.')
      }
    }, 250)
    return () => window.clearInterval(tick)
  }, [timer?.endsAt, speak])

  const toggleWake = () => {
    if (!recognitionRef.current) { setReply('Voice recognition requires Chrome or Microsoft Edge.'); return }
    const enabled = !wakeEnabledRef.current
    wakeEnabledRef.current = enabled
    setWakeEnabled(enabled)
    awaitingCommandRef.current = false
    if (enabled) { setReply('Always-listening mode is active. Say “Hi Jarvis”.'); startRecognition() }
    else { recognitionRef.current.abort(); setReply('Wake-word mode is off. Tap the mic whenever you need me.') }
  }
  const listenOnce = () => {
    if (!recognitionRef.current) { setReply('Voice recognition requires Chrome or Microsoft Edge.'); return }
    if (listening) { recognitionRef.current.stop(); return }
    setReply('Listening…')
    startRecognition()
  }

  const timerText = timer ? `${String(Math.floor(timer.remaining / 60)).padStart(2, '0')}:${String(timer.remaining % 60).padStart(2, '0')}` : null

  return <div className="app-shell">
    <div className="aurora one" /><div className="aurora two" /><Sidebar status={status} capabilityCount={capabilities.length} />
    <main className="workspace">
      <header className="topbar"><div><p className="eyebrow">PERSONAL INTELLIGENCE SYSTEM <span>2.0</span></p><h1>Good day, <em>Rahul.</em></h1></div><div className="top-actions"><span className={`connection ${status}`}><i /> {status}</span><button onClick={() => document.getElementById('command-library')?.scrollIntoView({ behavior: 'smooth' })}>Explore capabilities</button></div></header>
      <section className="dashboard-grid">
        <FoodScanner open={scannerOpen} onClose={() => setScannerOpen(false)} />
        <section id="overview" className="hero-card panel"><div className="hero-copy"><span className="kicker">{listening ? 'VOICE CHANNEL OPEN' : wakeEnabled ? 'WAKE WORD ARMED' : 'JARVIS IS READY'}</span><h2>Your ideas.<br /><em>Amplified.</em></h2><p>{reply}</p><div className="hero-chips"><span><i /> {capabilities.length || '100+'} capabilities</span><span><i /> {Object.values(system || {}).length ? 'System linked' : 'Connecting'}</span>{timerText && <button onClick={() => setTimer(null)}>◷ {timerText} ×</button>}</div>{generatedImage && <a className="generated-preview" href={generatedImage.url} target="_blank" rel="noreferrer"><img src={generatedImage.url} alt={generatedImage.prompt} /><span>View generated image ↗</span></a>}</div><JarvisRobot listening={listening} busy={busy} /></section>
        <SystemMonitor status={status} voiceSupported={voiceSupported} system={system} />
        <QuickActions onAction={sendCommand} disabled={busy} />
        <HistoryPanel history={history} onRefresh={loadData} />
        <BrowserDataPanel records={browserData} onRefresh={loadData} />
        <WorkspacePanel data={workspaceData} onRefresh={loadData} onRun={sendCommand} />
        <div id="command-library"><CommandLibrary capabilities={capabilities} categories={categories} onRun={sendCommand} disabled={busy} /></div>
      </section>
      <CommandCenter command={command} setCommand={setCommand} onSend={() => sendCommand(command)} onListen={listenOnce} onToggleWake={toggleWake} listening={listening} wakeEnabled={wakeEnabled} busy={busy} voiceSupported={voiceSupported} />
      <footer><span>JARVIS / LOCAL SECURE RUNTIME</span><span>{voiceSupported ? 'VOICE READY' : 'TEXT MODE'} · {new Date().getFullYear()}</span></footer>
    </main>
  </div>
}
