export default function HistoryPanel({ history, onRefresh }) {
  return <section className="panel history-panel"><div className="panel-heading"><span>RECENT ACTIVITY</span><button onClick={onRefresh}>REFRESH</button></div><div className="history-list">{history.length ? history.map((item, index) => <article key={`${item.timestamp}-${index}`}><i /><div><strong>{item.command}</strong><p>{item.reply}</p></div><time>{new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</time></article>) : <p className="empty">No commands recorded yet.</p>}</div></section>
}
