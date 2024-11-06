// LabelVariationsModal.js
import React, { useState } from 'react';

function LabelVariationsModal({ isOpen, onSave, onCancel, currentLabelText }) {
    const [variations, setVariations] = useState('');

    const handleSave = () => {
        onSave(currentLabelText, variations.split(',').map(v => v.trim())); // Pass currentLabelText and variations
        setVariations(''); // Reset for next use
    };

    const handleModalClick = (e) => {
        e.stopPropagation(); // Prevents click inside the modal from closing it
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onCancel}>
            <div className="modal" onClick={handleModalClick}>  
                <input
                    type="text"
                    value={variations}
                    onChange={(e) => setVariations(e.target.value)}
                    placeholder="Field label variations, separated by comma - e.g., Invoice, Bill, Receipt"
                />
                <button onClick={handleSave}>Save</button>
                <button onClick={onCancel}>No need</button>
            </div>
        </div>
    );
}

export default LabelVariationsModal;
