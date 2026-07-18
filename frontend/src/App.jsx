import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './views/Dashboard';
import Scanner from './views/Scanner';
import Profile from './views/Profile';
import CoachChat from './views/CoachChat';
import Settings from './views/Settings';

export default function App() {
  // Navigation & Core config
  const [activeView, setActiveView] = useState('dashboard');
  const [apiHost, setApiHost] = useState(localStorage.getItem('api_host_url') || 'http://127.0.0.1:8000');
  const [token, setToken] = useState(localStorage.getItem('access_token') || '');

  // User States
  const [username, setUsername] = useState('demouser');
  const [profile, setProfile] = useState(null);
  
  // Dashboard & Logging States
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState([]);
  const [activeMeal, setActiveMeal] = useState(null);
  const [isLoadingScanner, setIsLoadingScanner] = useState(false);
  const [isCoachLoading, setIsCoachLoading] = useState(false);
  const [scannerError, setScannerError] = useState(null);
  
  // Chat History
  const [chatHistory, setChatHistory] = useState([
    {
      sender: 'coach',
      text: "Hello! I am your NutriVision AI Coach. Ask me anything about matching your meals to your athletic goals, adding protein, or pre-workout fuel options."
    }
  ]);

  // 1. AUTO LOGIN ON MOUNT
  const performAutoLogin = async () => {
    try {
      const response = await fetch(`${apiHost}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username_or_email: 'demouser',
          password: 'demopassword'
        })
      });

      if (response.ok) {
        const data = await response.json();
        const jwtToken = data.access_token;
        setToken(jwtToken);
        localStorage.setItem('access_token', jwtToken);
        console.log("Logged in automatically as demouser.");
        return jwtToken;
      } else {
        console.error("Auto login failed. Run seed.py first.");
      }
    } catch (err) {
      console.error("Failed to connect to backend server:", err);
    }
    return null;
  };

  const authenticatedFetch = async (url, options = {}) => {
    let currentToken = token;
    if (!currentToken) {
      currentToken = await performAutoLogin();
    }
    if (!currentToken) {
      throw new Error("No authentication token available");
    }

    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${currentToken}`
    };

    let res = await fetch(url, { ...options, headers });

    if (res.status === 401) {
      console.warn("Authentication failed (401). Retrying autologin...");
      localStorage.removeItem('access_token');
      const newToken = await performAutoLogin();
      if (newToken) {
        const retryHeaders = {
          ...options.headers,
          'Authorization': `Bearer ${newToken}`
        };
        res = await fetch(url, { ...options, headers: retryHeaders });
      }
    }
    return res;
  };

  useEffect(() => {
    if (!token) {
      performAutoLogin();
    }

    // Sync localStorage Gemini Key to backend privately
    const storedKey = localStorage.getItem('gemini_api_key');
    if (storedKey) {
      fetch(`${apiHost}/api/auth/sync-key`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: storedKey })
      })
      .then(res => {
        if (res.ok) {
          localStorage.removeItem('gemini_api_key');
          console.log("Gemini API key successfully synced to backend privately and removed from localStorage.");
        }
      })
      .catch(err => console.error("Sync API key error:", err));
    }
  }, [apiHost]);

  // 2. FETCH PROFILE & LOGS WHEN TOKEN AVAILABLE
  const fetchDashboardData = async () => {
    try {
      // Fetch Profile
      const profRes = await authenticatedFetch(`${apiHost}/api/athlete/profile`);
      if (profRes.ok) {
        const pData = await profRes.json();
        setProfile(pData);
      }

      // Fetch Today Summary
      const sumRes = await authenticatedFetch(`${apiHost}/api/analytics/summary`);
      if (sumRes.ok) {
        const sData = await sumRes.json();
        setSummary(sData);
      }

      // Fetch Trends
      const trendRes = await authenticatedFetch(`${apiHost}/api/analytics/trends`);
      if (trendRes.ok) {
        const tData = await trendRes.json();
        setTrends(tData);
      }
    } catch (err) {
      console.error("Failed to fetch dashboard data:", err);
    }
  };

  useEffect(() => {
    if (token) {
      fetchDashboardData();
    }
  }, [token, apiHost]);

  // 3. UPLOAD CUSTOM PLATE FILE
  const handleUploadFile = async (file) => {
    setIsLoadingScanner(true);
    setScannerError(null);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await authenticatedFetch(`${apiHost}/api/meals/upload`, {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const err = await res.json();
        setScannerError(err.detail || "Scan failed.");
        return;
      }

      const mealData = await res.json();
      setActiveMeal(mealData);
      
      // Refresh Dashboard stats
      fetchDashboardData();
    } catch (err) {
      setScannerError("Error scanning image. Make sure backend is running.");
      console.error(err);
    } finally {
      setIsLoadingScanner(false);
    }
  };

  // 4. CHOOSE TEMPLATE SCAN SIMULATION
  const handleSelectDemo = async (demoName) => {
    setIsLoadingScanner(true);
    setScannerError(null);
    try {
      // Create a 1x1 transparent pixel blob to satisfy UploadFile type constraints
      const canvas = document.createElement('canvas');
      canvas.width = 1;
      canvas.height = 1;
      const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
      const file = new File([blob], `${demoName}.jpg`, { type: 'image/jpeg' });

      const formData = new FormData();
      formData.append('file', file);

      const res = await authenticatedFetch(`${apiHost}/api/meals/upload`, {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const err = await res.json();
        setScannerError(err.detail || "Demo upload failed.");
        return;
      }

      const mealData = await res.json();
      setActiveMeal(mealData);
      
      // Refresh statistics
      fetchDashboardData();
    } catch (err) {
      setScannerError("Error generating demo meal.");
      console.error(err);
    } finally {
      setIsLoadingScanner(false);
    }
  };

  // 5. UPDATE PORTION WEIGHTS IN SCANNER
  const handleSavePortions = async (mealId, payload) => {
    try {
      const res = await authenticatedFetch(`${apiHost}/api/meals/${mealId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ food_items: payload })
      });

      if (!res.ok) {
        alert("Failed to update portion sizes.");
        return;
      }

      const updatedMeal = await res.json();
      setActiveMeal(updatedMeal);
      
      // Refresh statistics
      fetchDashboardData();
    } catch (err) {
      console.error("Portion save error:", err);
    }
  };

  // 5b. DELETE MEAL LOG ENTRY
  const handleDeleteMeal = async (mealId) => {
    try {
      const res = await authenticatedFetch(`${apiHost}/api/meals/${mealId}`, {
        method: 'DELETE'
      });

      if (!res.ok) {
        alert("Failed to delete meal log.");
        return;
      }

      if (activeMeal && activeMeal.id === mealId) {
        setActiveMeal(null);
      }

      // Refresh dashboard charts and today's stats immediately
      fetchDashboardData();
    } catch (err) {
      console.error("Delete meal error:", err);
    }
  };

  // 6. UPDATE ATHLETE PROFILE
  const handleUpdateProfile = async (updatedFields) => {
    try {
      const res = await authenticatedFetch(`${apiHost}/api/athlete/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updatedFields)
      });

      if (res.ok) {
        const newProf = await res.json();
        setProfile(newProf);
        
        // Refresh statistics (calculated targets will update)
        fetchDashboardData();
      }
    } catch (err) {
      console.error("Profile update error:", err);
    }
  };

  // 7. SEND CHAT COACH MESSAGE
  const handleSendChatMessage = async (msgText, currentHistory) => {
    setIsCoachLoading(true);
    try {
      // Map history to standard chat format expected by LLM service
      const historyPayload = currentHistory.slice(0, -1).map(h => ({
        sender: h.sender,
        text: h.text
      }));

      const res = await authenticatedFetch(`${apiHost}/api/athlete/coach-chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: msgText,
          history: historyPayload
        })
      });

      if (res.ok) {
        const data = await res.json();
        setChatHistory(prev => [
          ...prev,
          { sender: 'coach', text: data.reply }
        ]);
      } else {
        setChatHistory(prev => [
          ...prev,
          { sender: 'coach', text: "I'm having trouble connecting to my knowledge base right now. Please check if the server is running." }
        ]);
      }
    } catch (err) {
      console.error(err);
      setChatHistory(prev => [
        ...prev,
        { sender: 'coach', text: "Network connection lost. Please try again." }
      ]);
    } finally {
      setIsCoachLoading(false);
    }
  };

  // Handle click on dashboard meal card to inspect it in the visualizer
  const handleSelectMealFromLogs = (meal) => {
    if (meal) {
      setActiveMeal(meal);
      setActiveView('scanner');
    } else {
      // Clicked 'Scan First Meal' button
      setActiveMeal(null);
      setActiveView('scanner');
    }
  };

  return (
    <div className="app-container">
      <Navbar 
        activeView={activeView} 
        setActiveView={setActiveView} 
        username={username}
        sport={profile ? profile.sport : 'General Fitness'}
      />
      
      <main className="main-content">
        {/* View Header */}
        <header className="view-header">
          <div className="view-title">
            <h1>
              {activeView === 'dashboard' && 'Dashboard Overview'}
              {activeView === 'scanner' && 'AI Nutrition Scanner'}
              {activeView === 'profile' && 'Athlete Profile'}
              {activeView === 'coach' && 'AI Coach Chat'}
              {activeView === 'settings' && 'System Settings'}
            </h1>
            <p>
              {activeView === 'dashboard' && 'Daily nutritional metrics and athletic progress tracker.'}
              {activeView === 'scanner' && 'Locate food objects, estimate dimensions, and review portions.'}
              {activeView === 'profile' && 'Manage bodyweight targets and physical metrics.'}
              {activeView === 'coach' && 'Consult Gemma/Llama/Gemini for sport-specific meal coaching.'}
              {activeView === 'settings' && 'Configure developer APIs, LocalStorage keys, and databases.'}
            </p>
          </div>
        </header>

        {/* View Selection Router */}
        {activeView === 'dashboard' && (
          <Dashboard 
            summary={summary} 
            trends={trends} 
            onSelectMeal={handleSelectMealFromLogs}
            onDeleteMeal={handleDeleteMeal}
            apiHost={apiHost}
          />
        )}
        
        {activeView === 'scanner' && (
          <Scanner 
            activeMeal={activeMeal}
            setActiveMeal={setActiveMeal}
            onUploadFile={handleUploadFile}
            onSelectDemo={handleSelectDemo}
            onSavePortions={handleSavePortions}
            isLoading={isLoadingScanner}
            apiHost={apiHost}
            error={scannerError}
            setError={setScannerError}
          />
        )}

        {activeView === 'profile' && (
          <Profile 
            profile={profile} 
            onUpdateProfile={handleUpdateProfile} 
          />
        )}

        {activeView === 'coach' && (
          <CoachChat 
            onSendChatMessage={handleSendChatMessage}
            isCoachLoading={isCoachLoading}
            chatHistory={chatHistory}
            setChatHistory={setChatHistory}
          />
        )}

        {activeView === 'settings' && (
          <Settings 
            apiHost={apiHost}
            setApiHost={setApiHost}
          />
        )}
      </main>
    </div>
  );
}
