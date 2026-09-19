const actions = [['◷', 'Time', 'What time is it?'], ['☁', 'Weather', 'What is the weather?'], ['◈', 'System', 'Check computer health'], ['◎', 'Focus', 'Start focus mode'], ['▣', 'Capture', 'Take a screenshot'], ['✦', 'Create', 'Generate image of a cinematic futuristic command center']]
export default function QuickActions({ onAction, disabled }) {
  return <section className="panel quick-actions"><div className="panel-heading"><span>QUICK LAUNCH</span><small>ONE TAP ACTIONS</small></div><div className="action-grid">{actions.map(([icon, label, command]) => <button key={label} disabled={disabled} onClick={() => onAction(command)}><b>{icon}</b><span>{label}</span><small>{command}</small></button>)}</div></section>
}
