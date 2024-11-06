import React, { useEffect, useRef, useState } from 'react';
import LabelVariationsModal from './LabelVariationsModal'; // Import the modal component

function findTextForCoordinates(blobCoordinates, mergedTexts) {
  const [x1, y1, width1, height1] = blobCoordinates;
  for (const { coordinates: [x2, y2, width2, height2], text } of mergedTexts) {
      // This is a simple overlap check, you might need a more sophisticated comparison
      if (x1 === x2 && y1 === y2 && width1 === width2 && height1 === height2) {
          console.log("Matching text found for coordinates:", blobCoordinates);
          return text;
      }
  }
  console.log("No matching text found for coordinates:", blobCoordinates);
  return null; // No matching text found
}

function InteractiveAnnotatedImage({ imagePath, blobs, mergedTexts, onSelectionComplete,  onLabelVariationsUpdate }) {
  const imageRef = useRef(null);
  const [scaleFactor, setScaleFactor] = useState(1);
  const [selectedPairs, setSelectedPairs] = useState([]);
  const [currentPair, setCurrentPair] = useState([]);
  const [selectionCount, setSelectionCount] = useState({});
  const [isVariationsModalOpen, setIsVariationsModalOpen] = useState(false);
  const [currentLabelIndex, setCurrentLabelIndex] = useState(null); // Track the current label for variations
  const [currentLabelText, setCurrentLabelText] = useState('');
  const [labelVariations, setLabelVariations] = useState({}); // Store label variations
  
  // This function might be triggered when a pair is fully selected
  const openLabelVariationsModal = (labelText) => {
    setCurrentLabelText(labelText); // Set the actual text, not the index
    setIsVariationsModalOpen(true);
  };



  const handleSaveVariations = (labelText, variationsArray) => {
    // Update labelVariations state to include new variations for the labelText
    setLabelVariations(prevVariations => ({
      ...prevVariations,
      [labelText]: variationsArray // Use labelText as key
    }));
    setIsVariationsModalOpen(false);
  };

  const handleCancelModal = () => {
    setIsVariationsModalOpen(false); // Close the modal on cancel
  };

  useEffect(() => {
    onSelectionComplete(selectedPairs);
    // Only call onLabelVariationsUpdate if it's defined
    if (onLabelVariationsUpdate) {
      onLabelVariationsUpdate(labelVariations); // Update parent component with label variations
    }
  }, [selectedPairs, labelVariations, onSelectionComplete, onLabelVariationsUpdate]);

  useEffect(() => {
    const calculateScaleFactor = () => {
      if (imageRef.current) {
        const naturalWidth = imageRef.current.naturalWidth;
        const displayWidth = imageRef.current.clientWidth;
        if (naturalWidth && displayWidth) {
          setScaleFactor(displayWidth / naturalWidth);
        }
      }
    };

    if (imageRef.current) {
      if (imageRef.current.complete) {
        calculateScaleFactor();
      } else {
        imageRef.current.onload = calculateScaleFactor;
      }
    }

    window.addEventListener('resize', calculateScaleFactor);
    return () => window.removeEventListener('resize', calculateScaleFactor);
  }, [imagePath]);

  useEffect(() => {
    onSelectionComplete(selectedPairs);
  }, [selectedPairs, onSelectionComplete]);

  const addSelection = (index) => {
    if (selectionCount[index] >= 2) return;

    const updatedCurrentPair = [...currentPair, index];
    const updatedSelectionCount = { ...selectionCount, [index]: (selectionCount[index] || 0) + 1 };

    if (updatedCurrentPair.length === 2) {
      setSelectedPairs([...selectedPairs, updatedCurrentPair]);
      setCurrentPair([]);
    } else {
      setCurrentPair(updatedCurrentPair);
    }
    setSelectionCount(updatedSelectionCount);

    if (updatedCurrentPair.length === 2) {
        // Assuming the first item is the index for the blob
        const blobCoordinates = blobs[updatedCurrentPair[0]].coordinates;
        // Find the matching text for these coordinates in mergedTexts
        const labelText = findTextForCoordinates(blobCoordinates, mergedTexts);
        if (labelText) {
            openLabelVariationsModal(labelText);
        }
    }
  };

  const undoSelection = () => {
    let lastSelectedIndex;
    if (currentPair.length > 0) {
      lastSelectedIndex = currentPair.pop();
      setCurrentPair([...currentPair]);
    } else if (selectedPairs.length > 0) {
      const lastPair = selectedPairs[selectedPairs.length - 1];
      lastSelectedIndex = lastPair.pop();
      if (lastPair.length === 0) {
        selectedPairs.pop();
      } else {
        selectedPairs[selectedPairs.length - 1] = lastPair;
      }
      setSelectedPairs([...selectedPairs]);
    }

    if (lastSelectedIndex !== undefined) {
      const updatedSelectionCount = { ...selectionCount };
      if (updatedSelectionCount[lastSelectedIndex] > 0) {
        updatedSelectionCount[lastSelectedIndex]--;
      }
      setSelectionCount(updatedSelectionCount);
    }
  };

  const getLabel = (index) => {
    const occurrences = selectedPairs.flat().filter(i => i === index).length + (currentPair.includes(index) ? 1 : 0);
    let label = '';

    selectedPairs.forEach((pair, pairIndex) => {
      pair.forEach((elementIndex, elementPosition) => {
        if (elementIndex === index) {
          label += `${pairIndex + 1}${elementPosition === 0 ? 'A' : 'B'} `;
        }
      });
    });

    if (currentPair.includes(index) && occurrences < 2) {
      label += `${selectedPairs.length + 1}A `;
    }

    return label.trim();
  };

  return (
    <>
    <button onClick={undoSelection} className="undo-button">Undo Selection</button>

    <div style={{ position: 'relative', display: 'inline-block' }}>
      <img ref={imageRef} src={imagePath} alt="Annotated Invoice" style={{ maxWidth: '100%' }} />
      <svg style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}>
        {blobs.map((blob, index) => {
          const [x, y, width, height] = blob.coordinates.map(coord => coord * scaleFactor);
          const isSelected = selectedPairs.flat().includes(index) || currentPair.includes(index);
          const label = getLabel(index);

          return (
            <g key={index} onClick={() => addSelection(index)}>
              <rect
                x={x} y={y} width={width} height={height}
                fill="none" stroke={isSelected ? 'blue' : 'red'} strokeWidth="2"
                style={{ pointerEvents: 'all', cursor: 'pointer' }}
              />
              {label && (
                <text
                  x={x + 5} y={y + 20}
                  fill="blue" fontSize="15"
                  style={{ pointerEvents: 'none' }}
                >
                  {label}
                </text>
              )}
            </g>

          );
        })}
      </svg>

    </div>
    {isVariationsModalOpen && (
      <LabelVariationsModal
        isOpen={isVariationsModalOpen}
        onSave={handleSaveVariations}
        onCancel={handleCancelModal}
        currentLabelText={currentLabelText}
      />
    )}
    </>
  );
}

export default InteractiveAnnotatedImage;
