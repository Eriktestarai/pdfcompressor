import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [downloadUrl, setDownloadUrl] = useState(null)
  const [error, setError] = useState(null)
  const [stats, setStats] = useState(null)
  const [mode, setMode] = useState('compress') // 'compress' or 'booklet'

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)

    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && droppedFile.type === 'application/pdf') {
      setFile(droppedFile)
      setError(null)
    } else {
      setError('Vänligen ladda upp en PDF-fil')
    }
  }

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile)
      setError(null)
    } else {
      setError('Vänligen välj en PDF-fil')
    }
  }

  const handleProcess = async () => {
    if (!file) return

    setIsProcessing(true)
    setError(null)
    setDownloadUrl(null)
    setStats(null)

    const formData = new FormData()
    formData.append('file', file)

    const endpoint = mode === 'booklet' ? '/convert-to-booklet' : '/convert'

    try {
      const response = await fetch(`https://pdfcompressor-backend.onrender.com${endpoint}`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Bearbetning misslyckades')
      }

      const data = await response.json()
      setDownloadUrl(`https://pdfcompressor-backend.onrender.com${data.download_url}`)
      setStats(data.stats)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleReset = () => {
    setFile(null)
    setDownloadUrl(null)
    setError(null)
    setStats(null)
  }

  return (
    <div className="app">
      <header>
        <h1>🗜️ PDF Komprimering</h1>
        <p>Komprimera PDF:er snabbt och enkelt</p>
        <div className="security-badge">
          🔒 Dina filer raderas automatiskt efter nedladdning
        </div>
      </header>

      <main>
        {!downloadUrl ? (
          <>
            <div className="mode-selector">
              <button
                className={`mode-btn ${mode === 'compress' ? 'active' : ''}`}
                onClick={() => setMode('compress')}
              >
                🗜️ Komprimera
              </button>
              <button
                className={`mode-btn ${mode === 'booklet' ? 'active' : ''}`}
                onClick={() => setMode('booklet')}
              >
                📖 Skapa Booklet
              </button>
            </div>

            <div className="mode-description">
              {mode === 'compress' ? (
                <p>Minska PDF-filstorlek med upp till 99%</p>
              ) : (
                <p>Skapa en utskriftsklar booklet från Gemini Storybook (A4 landscape)</p>
              )}
            </div>

            <div
              className={`drop-zone ${isDragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              {file ? (
                <div className="file-info">
                  <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="file-name">{file.name}</p>
                  <p className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                  <button className="change-file" onClick={handleReset}>
                    Välj annan fil
                  </button>
                </div>
              ) : (
                <div className="drop-zone-content">
                  <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p>Dra och släpp din PDF här</p>
                  <p className="or">eller</p>
                  <label className="file-select-btn">
                    Välj fil
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={handleFileSelect}
                      hidden
                    />
                  </label>
                </div>
              )}
            </div>

            {error && (
              <div className="error">
                <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {error}
              </div>
            )}

            {file && (
              <button
                className="convert-btn"
                onClick={handleProcess}
                disabled={isProcessing}
              >
                {isProcessing ? (
                  <>
                    <div className="spinner"></div>
                    {mode === 'booklet' ? 'Skapar booklet...' : 'Komprimerar...'}
                  </>
                ) : (
                  <>
                    {mode === 'booklet' ? '📖 Skapa Booklet' : '✨ Komprimera PDF'}
                  </>
                )}
              </button>
            )}
          </>
        ) : (
          <div className="success">
            <svg className="icon success-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2>{mode === 'booklet' ? 'Booklet Skapad! 📖' : 'PDF Komprimerad! 🎉'}</h2>
            <p>{mode === 'booklet' ? 'Din booklet är redo för utskrift' : 'Din PDF har komprimerats till en mindre storlek'}</p>
            {stats && (
              <div className="stats">
                {mode === 'booklet' ? (
                  <>
                    <p>📦 {stats.original_size_mb} MB → {stats.booklet_size_mb} MB</p>
                    <p>📄 {stats.pages} sidor • {stats.format}</p>
                    <p>🔽 {stats.reduction_percent}% minskning</p>
                  </>
                ) : (
                  <>
                    <p>📦 {stats.original_size_mb} MB → {stats.compressed_size_mb} MB</p>
                    <p>🔽 {stats.reduction_percent}% minskning i storlek</p>
                  </>
                )}
              </div>
            )}
            <div className="action-buttons">
              <a
                href={downloadUrl}
                download
                className="download-btn"
              >
                {mode === 'booklet' ? '📥 Ladda ner booklet' : '📥 Ladda ner komprimerad PDF'}
              </a>
              <button className="new-conversion-btn" onClick={handleReset}>
                {mode === 'booklet' ? 'Skapa en till' : 'Komprimera en till'}
              </button>
            </div>
          </div>
        )}
      </main>

      <footer>
        <p>PDF Komprimering</p>
      </footer>
    </div>
  )
}

export default App
