// DirectoryInputForm.js

import React, { useState } from 'react';

function DirectoryInputForm({ onDirectorySubmit }) {
  const [directoryPath, setDirectoryPath] = useState('');

  const handleSubmit = (event) => {
      event.preventDefault();
      onDirectorySubmit(directoryPath);
  };

  return (
      <form onSubmit={handleSubmit}>
          <input
              type="text"
              value={directoryPath}
              onChange={(e) => setDirectoryPath(e.target.value)}
              placeholder="Enter directory path"
              required
          />
          <button type="submit">Process Invoice Directory</button>
      </form>
  );
}

export default DirectoryInputForm;
