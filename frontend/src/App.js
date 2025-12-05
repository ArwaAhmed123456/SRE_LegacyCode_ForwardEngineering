import React from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import Home from './components/Home';
import Login from './components/Login';
import Cashier from './components/Cashier';
import Admin from './components/Admin';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Switch>
          <Route path="/" render={() => <Home />} />
          <Route path="/login" render={() => <Login />} />
          <Route path="/cashier" render={() => <Cashier />} />
          <Route path="/admin" render={() => <Admin />} />
        </Switch>
      </div>
    </Router>
  );
}

export default App;
