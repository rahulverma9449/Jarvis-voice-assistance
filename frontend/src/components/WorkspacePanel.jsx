import { useState } from 'react'

export default function WorkspacePanel({ data, onRefresh, onRun }) {
  const [note, setNote] = useState('')
  const [reminder, setReminder] = useState('')
  const request = async (url, options) => {
    const response = await fetch(url, options)
    if (!response.ok) throw new Error('Workspace request failed')
    await onRefresh()
  }
  const addNote = () => {
    if (!note.trim()) return
    request('/api/v2/notes', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title: note.trim().slice(0, 50), content: note.trim() }) }).then(() => setNote('')).catch(() => {})
  }
  const addReminder = () => {
    if (!reminder.trim()) return
    const due = new Date(Date.now() + 60 * 60 * 1000)
    request('/api/v2/reminders', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title: reminder.trim(), due_at: due.toISOString() }) }).then(() => setReminder('')).catch(() => {})
  }
  return <section className="panel workspace-panel">
    <div className="panel-heading"><span>JARVIS PRO WORKSPACE</span><small>20 MARKET-READY APIs</small></div>
    <div className="workspace-stats"><article><strong>{data.summary?.total_commands || 0}</strong><span>Commands handled</span></article><article><strong>{data.summary?.unique_commands || 0}</strong><span>Unique requests</span></article><article><strong>{data.notes.length}</strong><span>Smart notes</span></article><article><strong>{data.reminders.length}</strong><span>Open reminders</span></article></div>
    <div className="workspace-columns">
      <div><div className="workspace-title"><span>QUICK NOTES</span><small>Stored locally</small></div><div className="mini-form"><input value={note} onChange={(event) => setNote(event.target.value)} onKeyDown={(event) => event.key === 'Enter' && addNote()} placeholder="Capture an idea…" /><button onClick={addNote}>+</button></div><div className="workspace-list">{data.notes.slice(0, 3).map((item) => <article key={item.id}><button onClick={() => request(`/api/v2/notes/${item.id}`, { method: 'DELETE' })}>×</button><strong>{item.title}</strong><p>{item.content}</p></article>)}{!data.notes.length && <p className="workspace-empty">Your saved ideas will appear here.</p>}</div></div>
      <div><div className="workspace-title"><span>REMINDERS</span><small>Defaults to one hour</small></div><div className="mini-form"><input value={reminder} onChange={(event) => setReminder(event.target.value)} onKeyDown={(event) => event.key === 'Enter' && addReminder()} placeholder="Remind me to…" /><button onClick={addReminder}>+</button></div><div className="workspace-list">{data.reminders.slice(0, 3).map((item) => <article key={item.id}><button onClick={() => request(`/api/v2/reminders/${item.id}`, { method: 'DELETE' })}>×</button><strong>{item.title}</strong><p>{new Date(item.due_at).toLocaleString()}</p></article>)}{!data.reminders.length && <p className="workspace-empty">Nothing pending. You are all clear.</p>}</div></div>
      <div><div className="workspace-title"><span>SMART SUGGESTIONS</span><small>Run instantly</small></div><div className="suggestion-list">{data.suggestions.slice(0, 4).map((item) => <button key={item.id} onClick={() => onRun(item.example)}><span>{item.title}<small>{item.example}</small></span><i>↗</i></button>)}</div></div>
    </div>
  </section>
}
