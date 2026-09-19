import { useMemo, useState } from 'react'

export default function CommandLibrary({ capabilities, categories, onRun, disabled }) {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('All')
  const visible = useMemo(() => capabilities.filter((item) => {
    const matchesCategory = category === 'All' || item.category === category
    const text = `${item.title} ${item.example} ${item.description}`.toLowerCase()
    return matchesCategory && text.includes(search.toLowerCase())
  }), [capabilities, category, search])
  return <section className="panel command-library">
    <div className="library-head"><div><span className="kicker">CAPABILITY MATRIX</span><h3>{capabilities.length || '100+'} things Jarvis can do</h3><p>Search, explore, or run any command instantly.</p></div><label className="command-search"><span>⌕</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search capabilities…" /></label></div>
    <div className="category-tabs"><button className={category === 'All' ? 'active' : ''} onClick={() => setCategory('All')}>All <b>{capabilities.length}</b></button>{categories.map((item) => <button className={category === item.name ? 'active' : ''} onClick={() => setCategory(item.name)} key={item.name}>{item.name} <b>{item.count}</b></button>)}</div>
    <div className="capability-grid">{visible.map((item) => <button type="button" className="capability-card" key={item.id} disabled={disabled} onClick={() => onRun(item.example)}><span className="cap-icon">{item.title.slice(0, 2).toUpperCase()}</span><span><strong>{item.title}</strong><small>{item.description}</small><code>“{item.example}”</code></span><i>↗</i></button>)}</div>
    {!visible.length && <p className="empty">No capabilities match that search.</p>}
  </section>
}
