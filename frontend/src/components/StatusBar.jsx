export default function StatusBar({ status }) {
  return <footer className="status-bar"><span><i className={status} /> VOICE LINK {status === 'online' ? 'ACTIVE' : 'STANDBY'}</span><span>JARVIS / LOCAL NETWORK</span><span>{new Date().getFullYear()} · SECURE SESSION</span></footer>
}
