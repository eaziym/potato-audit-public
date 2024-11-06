import React, { useState, useEffect } from 'react';

const BookingForm = ({ staffList, clientList, onSubmit, auditFees, setAuditFees  }) => {
    const [selectedStaff, setSelectedStaff] = useState('');
    const [selectedClient, setSelectedClient] = useState('');
    const [selectedFY, setSelectedFY] = useState('');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [auditFee, setAuditFee] = useState('');
    const [editFee, setEditFee] = useState(false);


    const getFinancialYears = () => {
        const currentYear = new Date().getFullYear();
        let years = [];
        for (let year = 2000; year <= currentYear; year++) {
            years.push(`FY${year}`);
        }
        return years;
    };

    const handleStaffSelection = (event) => {
        const selectedIndex = event.target.options.selectedIndex;
        const staffName = event.target.options[selectedIndex].getAttribute('data-name');
        const staffLevel = event.target.options[selectedIndex].getAttribute('data-level');
        setSelectedStaff({
            name: staffName,
            level: staffLevel
        });
    };

    useEffect(() => {
        if (selectedClient) {
            if (auditFees[selectedClient]) {
                setAuditFee(auditFees[selectedClient]);
                setEditFee(false);
            } else {
                setAuditFee('');
                setEditFee(true);
            }
        }
    }, [selectedClient, auditFees]);

    const handleAuditFeeChange = (e) => {
        if (editFee) {  // Ensure changes are only made if editing is enabled
            setAuditFee(e.target.value);
        }
    };

    const enableEditFee = () => {
        setEditFee(true);
    };

    const handleConfirmFee = () => {
        setEditFee(false);  // Disable editing when confirmed
        setAuditFees(prev => ({ ...prev, [selectedClient]: auditFee }));  // Update the global state if necessary
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit({
            staff: selectedStaff,
            client: selectedClient,
            financialYear: selectedFY,
            startDate,
            endDate,
            auditFee: auditFee // Always send the current audit fee
        });
        if (editFee) {
            setAuditFees(prev => ({ ...prev, [selectedClient]: auditFee }));
        }
    };

    return (
        <form onSubmit={handleSubmit} className="booking-form">
            {/* Staff Dropdown */}
            <div className="form-group">
                <label>
                    Staff:
                    <select value={selectedStaff.name} onChange={handleStaffSelection}>
                        <option value="">Select Staff</option>
                        {staffList.map((staff, index) => (
                            <option key={index} data-name={staff.name} data-level={staff.level} value={staff.name}>
                                {`${staff.name} (${staff.level})`}
                            </option>
                        ))}
                    </select>
                </label>
            </div>

            {/* Client Dropdown */}
            <div className="form-group">
                <label>
                    Client:
                    <select value={selectedClient} onChange={e => setSelectedClient(e.target.value)}>
                        <option value="">Select Client</option>
                        {clientList.map(clientName => (
                            <option key={clientName} value={clientName}>{clientName}</option>
                        ))}
                    </select>
                </label>
            </div>

            {/* Financial Year Dropdown */}
            <div className="form-group">
                <label>
                    Financial Year:
                    <select value={selectedFY} onChange={e => setSelectedFY(e.target.value)}>
                        <option value="">Select Financial Year</option>
                        {getFinancialYears().map(fy => (
                            <option key={fy} value={fy}>{fy}</option>
                        ))}
                    </select>
                </label>
            </div>

            {/* Date Inputs */}
            <div className="form-group">
                <label>Start Date: <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} /></label>
            </div>
            <div className="form-group">
                <label>End Date: <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} /></label>
            </div>

            {/* Audit Fee Input */}
            <div className="form-group">
                <label>
                    Audit Fee:
                    <input type="number" value={auditFee} onChange={handleAuditFeeChange} disabled={!editFee} step="0.01" />
                    {editFee ? (
                        <button type="button" onClick={handleConfirmFee}>Confirm Fee</button>
                    ) : (
                        <button type="button" onClick={() => enableEditFee()}>Wrong Fee?</button>
                    )}
                </label>
            </div>

            <button type="submit">Book</button>
        </form>
    );
};

export default BookingForm;
