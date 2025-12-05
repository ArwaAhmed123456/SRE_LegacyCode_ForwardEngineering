import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

function Home() {
  return (
    <div className="home-container">
      <h1>Welcome to Point of Sale System</h1>
      <p>Select your role to continue:</p>
      <div className="button-container">
        <Link to="/login" className="button">Login</Link>
        <Link to="/cashier" className="button">Cashier</Link>
        <Link to="/admin" className="button">Admin</Link>
      </div>
    </div>
  );
}

export default Home;
