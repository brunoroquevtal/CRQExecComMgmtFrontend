import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import DataEditor from './pages/DataEditor';
import Communication from './pages/Communication';
import Settings from './pages/Settings';
import Planning from './pages/Planning';
import UserManagement from './pages/UserManagement';
import HiddenActivities from './pages/HiddenActivities';
import Login from './pages/Login';
import Signup from './pages/Signup';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import './App.css';

function ProtectedRoute({ children, requiredRole = null, requiredAnyRole = null }) {
  const { isAuthenticated, loading, hasRole, hasAnyRole } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-vtal-secondary"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  // Verificar role específica
  if (requiredRole && !hasRole(requiredRole)) {
    return <Navigate to="/dashboard" />;
  }

  // Verificar se tem uma das roles
  if (requiredAnyRole && !hasAnyRole(requiredAnyRole)) {
    return <Navigate to="/dashboard" />;
  }

  return children;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
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
        <Route 
          path="dados" 
          element={
            <ProtectedRoute requiredAnyRole={['lider_mudanca', 'administrador']}>
              <DataEditor />
            </ProtectedRoute>
          } 
        />
        <Route path="planejamento" element={<Planning />} />
        <Route path="comunicacao" element={<Communication />} />
        <Route 
          path="usuarios" 
          element={
            <ProtectedRoute requiredRole="administrador">
              <UserManagement />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="atividades-ocultas" 
          element={
            <ProtectedRoute requiredAnyRole={['lider_mudanca', 'administrador']}>
              <HiddenActivities />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="configuracoes" 
          element={
            <ProtectedRoute requiredRole="administrador">
              <Settings />
            </ProtectedRoute>
          } 
        />
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
