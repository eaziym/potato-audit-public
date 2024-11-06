import React, { useState, useEffect } from 'react';
import axios from 'axios';
import BookingForm from './BookingForm';

const StaffBookingSystem = () => {
    const [staffList, setStaffList] = useState([]);
    const [clientList, setClientList] = useState([]);
    const [bookings, setBookings] = useState([]);
    const [auditFees, setAuditFees] = useState({}); // State to manage audit fees for each client
    const [rates, setRates] = useState({
        'AA': 180,
        'EA': 220,
        'SA1': 250,
        'SA2': 300,
        'AM': 360
    });

    useEffect(() => {
        const fetchStaffAndClients = async () => {
            const staffData = await axios.get('/api/staff');
            const clientData = await axios.get('/api/clients');
            if (clientData.data.clients) {
                setClientList(clientData.data.clients);
              }
            if (staffData.data.staff){
                setStaffList(staffData.data.staff);
            }
        };
        fetchStaffAndClients();
    }, []);

    const handleRateChange = (level, newRate) => {
        setRates(prevRates => ({
            ...prevRates,
            [level]: newRate
        }));
    };

    const handleBookingSubmit = async (bookingData) => {
        alert('Booking submitted!');
        const dataToSend = {
            ...bookingData,
            rates: rates
        };
        const response = await axios.post('/api/bookings', dataToSend);
        if (response.status === 200) {
            setBookings([...bookings, response.data]);
        }
    };

    return (
        <div>
            <h1>Staff Booking</h1>
            <h2>Hourly Rates</h2>
            {Object.entries(rates).map(([level, rate]) => (
                <div key={level}>
                    {level}: <input type="number" value={rate} onChange={(e) => handleRateChange(level, e.target.value)} />
                </div>
            ))}
            <BookingForm 
                staffList={staffList} 
                clientList={clientList} 
                onSubmit={handleBookingSubmit} 
                auditFees={auditFees} 
                setAuditFees={setAuditFees} // Pass the setAuditFees function
            />
        </div>
    );
};

export default StaffBookingSystem;
