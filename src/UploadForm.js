import React, { useState } from 'react';
import axios from 'axios';

const UploadForm = () => {
    const [files, setFiles] = useState([]);
    const [downloadDirectory, setDownloadDirectory] = useState('');

    const handleFilesChange = (event) => {
        setFiles(Array.from(event.target.files));
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (files.length === 0) return;

        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file);
        });
        formData.append('downloadDirectory', downloadDirectory);

        try {
            const response = await axios.post('/upload-docs', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            alert('Great! Files have been processed and saved to the specified directory.');
        } catch (error) {
            console.error(error);
            alert('Failed to process documents.');
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input type="file" multiple onChange={handleFilesChange} accept=".pdf,.png,.jpg,.jpeg" />
            <input
                type="text"
                value={downloadDirectory}
                onChange={e => setDownloadDirectory(e.target.value)}
                placeholder="Enter download directory path"
            />
            <button type="submit">Process Documents</button>
        </form>
    );
};

export default UploadForm;
