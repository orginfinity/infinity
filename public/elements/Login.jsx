import React, { useState } from 'react';


const Login = () =>
{
      const loginClick = async () => {
        try {
          const response = await fetch('https://api.example.com/data'); // Replace with your API URL
          const data = await response.json();
          console.log(data); // Process the API response
        } catch (error) {
          console.error('Error fetching data:', error);
        }
      };

      return (
        <div>
          <button onClick={loginClick}>
            Fetch Data
          </button>
        </div>
      );
    }

export default Login