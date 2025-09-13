import React, { useState } from 'react';
import './App.css';

function App() {
  const [recipe, setRecipe] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // This will connect to your Python backend
      const response = await fetch('http://localhost:5000/api/recipe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ dish: recipe }),
      });
      
      const data = await response.json();
      console.log('Recipe generated:', data);
    } catch (error) {
      console.error('Error generating recipe:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🌱 Verde</h1>
        <p>Your vegetarian recipe companion for HackMIT 2025</p>
        
        <form onSubmit={handleSubmit} className="recipe-form">
          <input
            type="text"
            value={recipe}
            onChange={(e) => setRecipe(e.target.value)}
            placeholder="What dish would you like to make vegetarian?"
            className="recipe-input"
          />
          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? 'Generating...' : 'Generate Recipe'}
          </button>
        </form>
      </header>
    </div>
  );
}

export default App;
