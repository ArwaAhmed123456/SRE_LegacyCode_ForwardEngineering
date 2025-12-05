import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Cashier.css';

function Cashier() {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    // Fetch products from backend
    fetch('http://localhost:8080/api/products')
      .then(response => response.json())
      .then(data => setProducts(data))
      .catch(error => console.error('Error fetching products:', error));
  }, []);

  const addToCart = (product) => {
    const existingItem = cart.find(item => item.id === product.id);
    if (existingItem) {
      setCart(cart.map(item =>
        item.id === product.id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
    setTotal(total + product.price);
  };

  const removeFromCart = (productId) => {
    const item = cart.find(item => item.id === productId);
    if (item) {
      if (item.quantity > 1) {
        setCart(cart.map(item =>
          item.id === productId
            ? { ...item, quantity: item.quantity - 1 }
            : item
        ));
      } else {
        setCart(cart.filter(item => item.id !== productId));
      }
      setTotal(total - item.price);
    }
  };

  const checkout = () => {
    alert('Checkout functionality to be implemented');
  };

  return (
    <div className="cashier-container">
      <h1>Cashier Dashboard</h1>
      <div className="cashier-content">
        <div className="products-section">
          <h2>Products</h2>
          <div className="products-grid">
            {products.map(product => (
              <div key={product.id} className="product-card">
                <h3>{product.name}</h3>
                <p>${product.price}</p>
                <button onClick={() => addToCart(product)}>Add to Cart</button>
              </div>
            ))}
          </div>
        </div>
        <div className="cart-section">
          <h2>Cart</h2>
          <ul>
            {cart.map(item => (
              <li key={item.id}>
                {item.name} - ${item.price} x {item.quantity}
                <button onClick={() => removeFromCart(item.id)}>Remove</button>
              </li>
            ))}
          </ul>
          <p>Total: ${total.toFixed(2)}</p>
          <button onClick={checkout}>Checkout</button>
        </div>
      </div>
      <Link to="/">Back to Home</Link>
    </div>
  );
}

export default Cashier;
