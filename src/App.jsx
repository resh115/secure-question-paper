import React from "react";
import { useEffect, useState } from 'react';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { auth } from './lib/firebase';
import { getCurrentUser } from './lib/api';
import Login from './pages/Login';
import SetterDashboard from './pages/SetterDashboard';
import ExaminerDashboard from './pages/ExaminerDashboard';
import AppLayout from './components/AppLayout';
import './styles.css';

export default function App() {
  const [firebaseUser, setFirebaseUser] = useState(null);
  const [appUser, setAppUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    return onAuthStateChanged(auth, async (user) => {
      setFirebaseUser(user);
      if (!user) {
        setAppUser(null); setLoading(false); return;
      }
      try {
        const profile = await getCurrentUser(user);
        setAppUser(profile);
      } catch (err) {
        setError(err.message);
        await signOut(auth);
      } finally { setLoading(false); }
    });
  }, []);

  async function logout() {
    await signOut(auth);
    setAppUser(null);
  }

  async function afterLogin(user) {
    try { setAppUser(await getCurrentUser(user)); }
    catch (err) { setError(err.message); await signOut(auth); }
  }

  if (loading) return <div className="boot-screen"><div className="loader-ring" /><span>Initializing secure session…</span></div>;
  if (!firebaseUser || !appUser) return <Login onLogin={afterLogin} />;

  const role = appUser.role;
  const isSetter = role === 'setter' || role === 'admin';
  const isExaminer = role === 'examiner' || role === 'admin';

  return (
    <AppLayout user={firebaseUser} role={role} onLogout={logout}>
      {error && <div className="error-box global-error">{error}</div>}
      {isSetter && !isExaminer && <SetterDashboard user={firebaseUser} />}
      {isExaminer && !isSetter && <ExaminerDashboard user={firebaseUser} />}
      {isSetter && isExaminer && <div className="admin-dual"><SetterDashboard user={firebaseUser} /><ExaminerDashboard user={firebaseUser} /></div>}
      {!isSetter && !isExaminer && <div className="glass-card access-denied"><h2>Role not configured</h2><p>Your Firebase identity is valid, but no supported application role is assigned.</p></div>}
    </AppLayout>
  );
}
