import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Admin.css';

function Admin() {
  const [employees, setEmployees] = useState([]);
  const [products, setProducts] = useState([]);
  const [newEmployee, setNewEmployee] = useState({ name: '', role: '' });
  const [newProduct, setNewProduct] = useState({ name: '', stock: '', price: '' });

  useEffect(() => {
    // Fetch employees and products from backend
    fetch('http://localhost:8080/api/employees')
      .then(response => response.json())
      .then(data => setEmployees(data))
      .catch(error => console.error('Error fetching employees:', error));

    fetch('http://localhost:8080/api/products')
      .then(response => response.json())
      .then(data => setProducts(data))
      .catch(error => console.error('Error fetching products:', error));
  }, []);

  const addEmployee = () => {
    if (newEmployee.name && newEmployee.role) {
      fetch('http://localhost:8080/api/employees', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newEmployee),
      })
      .then(response => response.json())
      .then(data => {
        setEmployees([...employees, data]);
        setNewEmployee({ name: '', role: '' });
      })
      .catch(error => console.error('Error adding employee:', error));
    }
  };

  const addProduct = () => {
    if (newProduct.name && newProduct.stock && newProduct.price) {
      fetch('http://localhost:8080/api/products', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newProduct,
          stock: parseInt(newProduct.stock),
          price: parseFloat(newProduct.price)
        }),
      })
      .then(response => response.json())
      .then(data => {
        setProducts([...products, data]);
        setNewProduct({ name: '', stock: '', price: '' });
      })
      .catch(error => console.error('Error adding product:', error));
    }
  };

  const generateReport = () => {
    alert('Sales report generation to be implemented');
  };

  return (
    <div className="admin-container">
      <h1>Admin Panel</h1>
      <div className="admin-sections">
        <div className="section">
          <h2>Employee Management</h2>
          <div className="add-form">
            <input
              type="text"
              placeholder="Employee Name"
              value={newEmployee.name}
              onChange={(e) => setNewEmployee({ ...newEmployee, name: e.target.value })}
            />
            <input
              type="text"
              placeholder="Role"
              value={newEmployee.role}
              onChange={(e) => setNewEmployee({ ...newEmployee, role: e.target.value })}
            />
            <button onClick={addEmployee}>Add Employee</button>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Role</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {employees.map(employee => (
                <tr key={employee.id}>
                  <td>{employee.id}</td>
                  <td>{employee.name}</td>
                  <td>{employee.role}</td>
                  <td>
                    <button className="edit-button">Edit</button>
                    <button className="delete-button">Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="section">
          <h2>Inventory Management</h2>
          <div className="add-form">
            <input
              type="text"
              placeholder="Product Name"
              value={newProduct.name}
              onChange={(e) => setNewProduct({ ...newProduct, name: e.target.value })}
            />
            <input
              type="number"
              placeholder="Stock"
              value={newProduct.stock}
              onChange={(e) => setNewProduct({ ...newProduct, stock: e.target.value })}
            />
            <input
              type="number"
              step="0.01"
              placeholder="Price"
              value={newProduct.price}
              onChange={(e) => setNewProduct({ ...newProduct, price: e.target.value })}
            />
            <button onClick={addProduct}>Add Product</button>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Stock</th>
                <th>Price</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {products.map(product => (
                <tr key={product.id}>
                  <td>{product.id}</td>
                  <td>{product.name}</td>
                  <td>{product.stock}</td>
                  <td>${product.price}</td>
                  <td>
                    <button className="edit-button">Edit</button>
                    <button className="delete-button">Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="section">
          <h2>Reports</h2>
          <button onClick={generateReport} className="report-button">Generate Sales Report</button>
          <div className="report-container">
            <p>Report functionality to be implemented</p>
          </div>
        </div>
      </div>
      <Link to="/">Back to Home</Link>
    </div>
  );
}

export default Admin;
