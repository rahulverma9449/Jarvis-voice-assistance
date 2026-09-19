export default function BrowserDataPanel({ records, onRefresh }) {
  return <section className="panel browser-data-panel"><div className="panel-heading"><span>LOCAL ATLASSIAN DATASTORE</span><button onClick={onRefresh}>SYNC VIEW</button></div>
    <div className="browser-records">{records.length ? records.map((item, index) => <article key={`${item.timestamp}-${index}`}>
      <span className={`source ${item.source}`}>{item.source}</span><div><strong>{item.command}</strong><p>{item.reply}</p></div><time>{new Date(item.timestamp).toLocaleString()}</time>{item.url ? <a href={item.url} target="_blank" rel="noreferrer">OPEN</a> : <span />}
    </article>) : <p className="empty">No Jira or Confluence data cached yet. Ask Jarvis to check a sprint or read Confluence.</p>}</div>
  </section>
}
