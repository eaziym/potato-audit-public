// App.js
import React, { useEffect, useState, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import StaffBookingSystem from './StaffBookingSystem'; // Make sure to import your new component
import axios from 'axios';
import UploadForm from './UploadForm';
import FetchAnnouncementsForm from './FetchAnnouncementsForm';
import DirectoryInputForm from './DirectoryInputForm';
import InteractiveAnnotatedImage from './InteractiveAnnotatedImage';
import DataTable from './DataTable';
import './App.css';
import logo from './favicon.png'; 



function App() {
    const [processedImageInfo, setProcessedImageInfo] = useState({ filename: '', blobs: [], mergedTexts: []});
    const [selectedPairs, setSelectedPairs] = useState([]);
    const [directoryPath, setDirectoryPath] = useState(''); // Add directoryPath to state
    const [downloadDirectory, setDownloadDirectory] = useState(''); // New state for download directory input
    const [downloadKAMDirectory, setDownloadKAMDirectory] = useState(''); // New state for download directory input
    const [labelVariations, setLabelVariations] = useState({});
    const [isProcessing, setIsProcessing] = useState(false);
    const [progress, setProgress] = useState({ current: 0, total: 1, completed: false });
    const [processedData, setProcessedData] = useState([]);
    const [companies, setCompanies] = useState(''); // State for storing the list of companies
    const [announcements, setAnnouncements] = useState([]); // State for storing fetched announcements


    const handleFetchProcessReports = () => {
        axios.post('/fetch-process-reports', {
            downloadDir: downloadKAMDirectory
        }).then(response => {
            alert('Reports fetched and processed successfully.');
        }).catch(error => {
            console.error('Error fetching and processing reports:', error);
            alert('Failed to fetch and process reports.');
        });
    };

    const fetchProgress = useCallback(() => {
        axios.get('/progress')
            .then(response => {
                const { current, total } = response.data;
                setProgress(prevProgress => ({
                  ...prevProgress,
                  current,
                  total,
                  completed: current >= total
                }));
                if (current >= total) {
                    setIsProcessing(false);
                }
            })
            .catch(error => console.error("Failed to fetch progress", error));
    }, []);


    useEffect(() => {
        let interval = null;
        if (isProcessing) {
            interval = setInterval(fetchProgress, 1000);
        }
        return () => clearInterval(interval);
    }, [isProcessing, fetchProgress]);



    const handleDirectorySubmit = async (directoryPath) => {
        try {
            setDirectoryPath(directoryPath);

            // Adjust the endpoint as necessary. This should match your Flask route.
            const response = await axios.post('/process-directory', { directory: directoryPath });
            // Assuming the response contains both the filename and blobs data
            // Update this according to the actual structure of your response
            // Assuming your Flask endpoint now also returns merged texts along with blobs
            const { filename, blobs, mergedTexts } = response.data; 
            setProcessedImageInfo({ filename, blobs, mergedTexts }); // Update state with filename, blobs, and mergedTexts
        } catch (error) {
            console.error("Error processing directory:", error);
        }
    };

    const processedImagePath = processedImageInfo.filename ? `/processed-images/${processedImageInfo.filename}` : '';
    console.log("Processed Image Path:", processedImagePath);
    console.log("Processed Image Info:", processedImageInfo);
    
    console.log("Selected Pairs:", selectedPairs);
    console.log("Blobs:", processedImageInfo.blobs);
    console.log("Merged Texts:", processedImageInfo.mergedTexts);

    const handleProcessSelection = async () => {
        setIsProcessing(true);

        // Assuming `selectedPairs` contains the indexes of selected pairs,
        // and `processedImageInfo.blobs` contains the blobs data
        try {
            const response = await axios.post('/process-selected-pairs', {
                directoryPath,
                selectedPairs,
                blobs: processedImageInfo.blobs,
                mergedTexts: processedImageInfo.mergedTexts, 
                labelVariations, // Send label variations to the backend

            });
            console.log(response.data); // Handle response as needed
            fetchProgress();

        } catch (error) {
            console.error("Error sending selections:", error);
            setIsProcessing(false);

        }
    };
    

    useEffect(() => {
        if (progress.completed && directoryPath) {
            const queryParams = new URLSearchParams({ directory: directoryPath });
            axios.get(`/get-processed-info?${queryParams}`).then((response) => {
                setProcessedData(response.data);
            });
        }
    }, [progress.completed, directoryPath]);
    
    
      // Dynamically generate columns from processedData
      const columns = React.useMemo(() => {
        if (processedData.length > 0) {
            let cols = Object.keys(processedData[0]).map(key => ({
              Header: key.charAt(0).toUpperCase() + key.slice(1),
              accessor: key,
            }));
        
            // Find the 'File URL' column
            const urlColumn = cols.find(c => c.accessor === 'File URL');
            // Filter out the 'File URL' column from the original columns
            cols = cols.filter(c => c.accessor !== 'File URL');
            // Add the 'File URL' column at the end
            cols.push(urlColumn);
            
            return cols;
          }
          return [];
      }, [processedData]);

      const fetchAnnouncementsForToday = async () => {
        alert('Fetching announcements for yesterday...');
        try {
            const response = await axios.post('/fetch-todays-announcements', {
                companies: companies,
                downloadDir: downloadDirectory // Sending download directory to the backend
            });
            setAnnouncements(response.data); // Assuming the endpoint returns the list of announcements
            console.log("Fetched Announcements:", announcements);
        } catch (error) {
            console.error("Error fetching announcements:", error);
        }
    };


    return (
        <Router>
            <div className="App">
                <header>
                    <nav>
                        <ul>
                            <li>
                                <Link to="/">Home</Link>
                            </li>
                            <li>
                                <Link to="/booking">Staff Booking</Link>
                            </li>
                        </ul>
                    </nav>
                    <img src={logo} className="App-logo" alt="logo" />
                    <h1>Potato Audit</h1>
                </header>
                <Routes>
                    <Route path="/" element={
                        <>
 
                        <UploadForm />
                        <FetchAnnouncementsForm />

                        {/* Text area for entering multiple companies */}
                        <div>
                            <textarea
                                value={companies}
                                onChange={(e) => setCompanies(e.target.value)}
                                placeholder="Enter companies separated by comma"
                                rows="4" // Makes the textarea bigger
                                style={{ width: '100%', margin: '10px 0' }} // Ensures the textarea is fully visible and comfortably spaced
                            ></textarea>
                        </div>

                        {/* Input for specifying download directory */}
                        <div>
                            <input
                                type="text"
                                value={downloadDirectory}
                                onChange={(e) => setDownloadDirectory(e.target.value)}
                                placeholder="Enter download directory path"
                                style={{ width: '100%', margin: '10px 0' }} // Ensures the input is fully visible and comfortably spaced
                            />
                            <button onClick={fetchAnnouncementsForToday}>Fetch Yesterday's Announcements</button>
                        </div>

                        {/* KAM Download Directory Input */}
                        <div>
                            <input
                                type="text"
                                value={downloadKAMDirectory}
                                onChange={(e) => setDownloadKAMDirectory(e.target.value)}
                                placeholder="Enter download directory path"
                            />
                            <button onClick={handleFetchProcessReports}>Fetch and Process KAM Reports</button>
                        </div>

                        <DirectoryInputForm onDirectorySubmit={handleDirectorySubmit} />

                        <div className="invoice-image-container">
                            {processedImageInfo.filename && (
                                <InteractiveAnnotatedImage
                                    imagePath={`/processed-images/${processedImageInfo.filename}`}
                                    blobs={processedImageInfo.blobs}
                                    mergedTexts={processedImageInfo.mergedTexts}
                                    onSelectionComplete={setSelectedPairs}
                                    onLabelVariationsUpdate={setLabelVariations} // Handle label variations
                                    
                                />
                            )}
                        </div>
                        
                        {processedImageInfo.filename && selectedPairs.length > 0 && (
                        <button onClick={handleProcessSelection}>Process Selections</button>
                        )}

                        {(progress.current > 0 || progress.completed) && (
                            <>
                                <h2>Processing Progress</h2>
                                <progress value={progress.current} max={progress.total}></progress>
                                <p>{progress.current} of {progress.total} files processed</p>
                            </>
                        )}

                    <div className="table-container">
                        {progress.completed && (
                            <DataTable columns={columns} data={processedData} />
                        )}
                    </div>

                    </>
                    } />
                    <Route path="/booking" element={<StaffBookingSystem />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
