import { useEffect, useState } from 'react';
import { clearTokens } from './api.js';
import AuthScreen from './components/AuthScreen.jsx';
import Dashboard from './components/Dashboard.jsx';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(
    Boolean(sessionStorage.getItem('access_token')),
  );

  useEffect(() => {
    function logOutWhenSessionExpires() {
      setIsLoggedIn(false);
    }

    window.addEventListener('session-expired', logOutWhenSessionExpires);
    return () => window.removeEventListener('session-expired', logOutWhenSessionExpires);
  }, []);

  function logOut() {
    clearTokens();
    setIsLoggedIn(false);
  }

  if (isLoggedIn) {
    return <Dashboard onLogout={logOut} />;
  }

  return <AuthScreen onLogin={() => setIsLoggedIn(true)} />;
}

export default App;
