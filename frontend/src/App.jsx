import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import DataEditor from './pages/DataEditor';
import Communication from './pages/Communication';
import Settings from './pages/Settings';
import Planning from './pages/Planning';
import Login from './pages/Login';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import './App.css';

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="dados" element={<DataEditor />} />
        <Route path="planejamento" element={<Planning />} />
        <Route path="comunicacao" element={<Communication />} />
        <Route path="configuracoes" element={<Settings />} />
      </Route>
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <div className="app">
        <AppRoutes />
        <Toaster position="top-right" />
      </div>
    </AuthProvider>
  );
}

export default App;
