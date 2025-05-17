// frontend/src/App.jsx
import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import axios from "axios";

// Auth components
import Login from "./pages/Login";
import Register from "./pages/Register";
import ResetPassword from "./pages/ResetPassword";
import VerifyEmail from "./pages/VerifyEmail";

// Protected components
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";

// Auth context
const AuthContext = React.createContext();

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already authenticated
    axios
      .get("/api/user/")
      .then((response) => {
        setUser(response.data);
        setLoading(false);
      })
      .catch((error) => {
        setUser(null);
        setLoading(false);
      });
  }, []);

  const login = async (email, password) => {
    const response = await axios.post("/api/auth/login/", { email, password });
    return response.data;
  };

  const register = async (email, password) => {
    const response = await axios.post("/api/auth/register/", {
      email,
      password,
    });
    return response.data;
  };

  const logout = async () => {
    await axios.post("/api/auth/logout/");
    setUser(null);
  };

  const refreshAccessToken = async () => {
    await axios.post("/api/auth/refresh_token/");
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    refreshAccessToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

function RequireAuth({ children }) {
  const auth = React.useContext(AuthContext);

  if (auth.loading) {
    return <div>Loading...</div>;
  }

  if (!auth.user) {
    return <Navigate to="/" replace />;
  }

  return children;
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/reset-password/:token" element={<ResetPassword />} />
          <Route path="/verify-email/:token" element={<VerifyEmail />} />

          <Route
            path="/dashboard"
            element={
              <RequireAuth>
                <Dashboard />
              </RequireAuth>
            }
          />

          <Route
            path="/profile"
            element={
              <RequireAuth>
                <Profile />
              </RequireAuth>
            }
          />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
