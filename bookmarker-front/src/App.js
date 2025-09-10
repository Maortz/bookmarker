import React, { useState, useEffect } from 'react';

function App() {
  const [tempWidth, setTempWidth] = useState(21);
  const [tempHeight, setTempHeight] = useState(29.7);
  const [tempFont, setTempFont] = useState(15.7);
  const [year, setYear] = useState('התשפו');

  const [width, setWidth] = useState(21);
  const [height, setHeight] = useState(29.7);
  const [font, setFont] = useState(15.7);

  const [html, setHtml] = useState('');

  const fetchHtml = () => {
    const url = `https://bookmarkers-service.onrender.com/bookmarker/tanah_yomi?width=${width}&height=${height}&font=${font}&year=${year}`;
    fetch(url)
      .then(res => res.text())
      .then(data => setHtml(data));
  };

  useEffect(() => {
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
            <option value="התשפו">התשפו</option>
            <option value="התשפז">התשפז</option>
            <option value="התשפח">התשפח</option>
            <option value="התשפט">התשפט</option>
            {/* Add more year options as needed */}
          </select>
        </label>
      </div>

      <div
        className="printable-content"
        style={{ border: '1px solid #ccc', minHeight: 400, fontSize: font}}
        dangerouslySetInnerHTML={{ __html: html }}
      />

      <style>{`
        @media print {
          body * {
            visibility: hidden;
          }
          .printable-content, .printable-content * {
            visibility: visible;
          }
          .printable-content {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            direction: rtl;
          }
        }
      `}</style>
    </div>
  );
}

export default App;
