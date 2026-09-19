export default function JarvisRobot({ listening, busy }) {
  const mode = listening ? 'LISTENING' : busy ? 'THINKING' : 'READY'
  return <div className={`robot-stage ${listening ? 'listening' : ''} ${busy ? 'busy' : ''}`} aria-label={`Jarvis is ${mode.toLowerCase()}`}>
    <div className="robot-halo" /><div className="robot-scan" />
    <img src="/assets/jarvis-robot.png" alt="Jarvis futuristic AI robot" />
    <div className="robot-mode"><i /> {mode}</div>
  </div>
}
