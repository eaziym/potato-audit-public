import React, { useState } from 'react';
import axios from 'axios';

const FetchAnnouncementsForm = () => {
  const [company, setCompany] = useState('');
  const [year, setYear] = useState('');
  const [exchange, setExchange] = useState('SGX'); // Default to SGX
  const [downloadDir, setDownloadDir] = useState(''); // State for download directory

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      // Switching to a POST request to include more data securely
      const response = await axios.post('/fetch-announcements', {
        company,
        year,
        exchange, // Include the selected exchange in the data sent to the backend
        downloadDir, // Include the specified download directory
      });
      console.log(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Exchange selection */}
      <div>
        <label>
          Exchange:
          <select value={exchange} onChange={(e) => setExchange(e.target.value)}>
            <option value="SGX">SGX</option>
            <option value="ASX">ASX</option>
          </select>
        </label>
      </div>
      {/* Company name input */}
      <div>
        <label>
          Company Name:
          <input
            type="text"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            placeholder="Company Name"
          />
        </label>
      </div>
      {/* Year input */}
      <div>
        <label>
          Financial Year:
          <input
            type="text"
            value={year}
            onChange={(e) => setYear(e.target.value)}
            placeholder="Year"
          />
        </label>
      </div>
      {/* New: Download directory input */}
      <div>
        <label>
          Download Directory:
          <input
            type="text"
            value={downloadDir}
            onChange={(e) => setDownloadDir(e.target.value)}
            placeholder="Download Directory Path"
          />
        </label>
      </div>
      {/* Submit button */}
      <button type="submit">Fetch Yearly Announcements</button>
    </form>
  );
};

export default FetchAnnouncementsForm;
