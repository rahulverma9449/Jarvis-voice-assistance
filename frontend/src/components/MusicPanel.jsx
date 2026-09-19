import { useState } from 'react'
export default function MusicPanel({ onPlay, disabled }) {
  const [track, setTrack] = useState('')
  const play = () => track.trim() && onPlay(`play music ${track}`)
  return <section className="panel music-panel"><div className="panel-heading"><span>MUSIC LINK</span><small>YOUTUBE MUSIC</small></div><div className="album-art"><span>♫</span></div><div className="track-copy"><strong>Ready to play</strong><small>Tell Jarvis what you want to hear</small></div><div className="music-controls"><input value={track} onChange={(event) => setTrack(event.target.value)} onKeyDown={(event) => event.key === 'Enter' && play()} placeholder="Song or artist" /><button disabled={disabled || !track.trim()} onClick={play}>PLAY</button></div></section>
}
