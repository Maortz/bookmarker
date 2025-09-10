import React, { useState, useEffect } from 'react';

function App() {
  const [width, setWidth] = useState(21);
  const [height, setHeight] = useState(29.7);
  const [font, setFont] = useState(15.7);
  const [year, setYear] = useState('התשפו');
  const [html, setHtml] = useState('empty');

  
  useEffect(() => {
    const fetchHtml = async () => {
      const url = `https://bookmarkers-service.onrender.com/bookmarker/tanah_yomi?width=${width}&height=${height}&font=${font}&year=${year}`;
      try {
        const response = await fetch(url, {mode: 'no-cors'});
        const page = await response.text();
        setHtml(page);
      } catch (err) {
        alert(err);
      }
    };

    fetchHtml();
  }, [width, height, font, year]);

  return (
    <div>
      <label>
        רוחב:
        <input
          type="range"
          min="10"
          max="30"
          step="0.1"
          value={width}
          onChange={e => setWidth(e.target.value)}
        />
        {width}
      </label>
      <label>
        גובה:
        <input
          type="range"
          min="10"
          max="40"
          step="0.1"
          value={height}
          onChange={e => setHeight(e.target.value)}
        />
        {height}
      </label>
      <label>
        שנה:
        <input
          type="text"
          value={year}
          onChange={e => setYear(e.target.value)}
        />
      </label>
      <div>
        <button onClick={() => setFont(f => Math.max(8, f - 1))}>-</button>
        <span>גודל פונט: {font}</span>
        <button onClick={() => setFont(f => Math.min(48, parseFloat(f) + 1))}>+</button>
      </div>
      <hr />
      <div
        style={{ border: '1px solid #ccc', minHeight: 400 }}
        dangerouslySetInnerHTML={{ __html: html }}
        />
    </div>
  );
}

export default App;
