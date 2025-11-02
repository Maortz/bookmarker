import React, { useState, useEffect } from 'react';

function App() {
  const [tempWidth, setTempWidth] = useState(21);
  const [tempHeight, setTempHeight] = useState(29.7);
  const [tempFont, setTempFont] = useState(15.7);
  const [year, setYear] = useState('');

  const [width, setWidth] = useState(21);
  const [height, setHeight] = useState(29.7);
  const [font, setFont] = useState(15.7);

  const [html, setHtml] = useState('');

  const [yearOptions, setYearOptions] = useState([]);

  const toHebYear = async (date) => {
    try {
      const today = date.toISOString().slice(0, 10); // format YYYY-MM-DD
      const res = await fetch(`https://www.hebcal.com/converter?cfg=json&date=${today}&g2h=1&strict=1`);
      const data = await res.json();

      if (data && data.heDateParts && data.heDateParts.y) {
        const year = data.heDateParts.y
        const currentYear = year.slice(0, -2) + year.slice(-1)
        return "ה" + currentYear
      }
    } catch (e) {
      console.error('Error fetching Hebrew year:', e);
      return null
    }
  }


  useEffect(() => {
    // Fetch the current Hebrew year from Hebcal API
    const fetchCurrentHebrewYear = async () => {
      const today = new Date()
      const years = [];
      today.setFullYear(today.getFullYear() - 1)
      years.push(await toHebYear(today)) // prev
      years.push(await toHebYear(new Date())) // this year
      today.setFullYear(today.getFullYear() + 2); // next
      years.push(await toHebYear(today))
      setYearOptions(years);
      setYear(years[1]);
    };

    fetchCurrentHebrewYear();
  }, []);

  useEffect(() => {
    const url = `https://bookmarkers-service.onrender.com/bookmarker/tanah_yomi?width=${width}&height=${height}&font=${font}&year=${year}`;
    const fetchHtml = () => {
      if (!year)
        return
      fetch(url)
        .then(res => res.text())
        .then(data => setHtml(data));
    };

    fetchHtml();
  }, [width, height, font, year]);

  const handleWidthChange = (e) => setTempWidth(e.target.value);
  const handleWidthCommit = () => setWidth(tempWidth);

  const handleHeightChange = (e) => setTempHeight(e.target.value);
  const handleHeightCommit = () => setHeight(tempHeight);

  const handleFontChange = (e) => setTempFont(e.target.value);
  const handleFontCommit = () => setFont(tempFont);

  const handleYearChange = (e) => setYear(e.target.value);

  const sliderStyle = { width: '300px', margin: '10px 0' };

  return (
    <div>
      <div dir="rtl" className="controls" style={{ marginBottom: 20 }}>
        <label>
          רוחב:
          <input
            type="range"
            min="10"
            max="29.7"
            step="0.1"
            value={tempWidth}
            onChange={handleWidthChange}
            onMouseUp={handleWidthCommit}
            onTouchEnd={handleWidthCommit}
            style={sliderStyle}
          />
          {tempWidth}
        </label>

        <br />
        <label>
          גובה:
          <input
            type="range"
            min="10"
            max="29.7"
            step="0.1"
            value={tempHeight}
            onChange={handleHeightChange}
            onMouseUp={handleHeightCommit}
            onTouchEnd={handleHeightCommit}
            style={sliderStyle}
          />
          {tempHeight}
        </label>

        <br />
        <label>
          גודל פונט:
          <input
            type="range"
            min="8"
            max="48"
            step="0.5"
            value={tempFont}
            onChange={handleFontChange}
            onMouseUp={handleFontCommit}
            onTouchEnd={handleFontCommit}
            style={sliderStyle}
          />
          {tempFont}
        </label>

        <br />
        <label>
          שנה:
          <select value={year} onChange={handleYearChange} style={{ fontSize: '1rem', padding: 4, marginTop: 4 }}>
            {yearOptions.map(y => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </label>
      </div>

      <div
        className="printable-content"
        style={{ minHeight: 400 }}
        dangerouslySetInnerHTML={{ __html: html }}
      />
      <button
        onClick={() => window.print()}
        style={{
          position: 'fixed',
          top: '20px',
          left: '20px',
          padding: '10px 20px',
          fontSize: '1rem',
          cursor: 'pointer',
          borderRadius: '8px',
          border: '1px solid #333',
          background: '#f2f2f2',
          boxShadow: '0 2px 6px rgba(0,0,0,0.15)',
          zIndex: 1000
        }}
      >
        🖨️ הדפס
      </button>

      <style>{`
        @media print {
          @page {
            margin: 0;
          }
          body * {
            visibility: hidden;
            margin: 0 !important;
            padding: 0 !important;
          }
          .printable-content, .printable-content * {
            visibility: visible;
          }
          .printable-content {
            box-shadow: none;
            border: none;
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
          }
          button {
            display: none !important;
          }
        }
      `}</style>
    </div>
  );
}

export default App;
