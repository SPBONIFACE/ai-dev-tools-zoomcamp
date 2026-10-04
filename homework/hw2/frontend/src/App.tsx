import { useState, useEffect } from 'react';
import { HostDashboard } from './pages/HostDashboard';
import { GuestTracker } from './pages/GuestTracker';

export function App() {
  const [currentPartyId, setCurrentPartyId] = useState<string | null>(() => {
    // Check hash for direct link e.g. #/waitlist/p-101
    const hash = window.location.hash;
    const match = hash.match(/#\/?waitlist\/([^/]+)/);
    return match ? match[1] : null;
  });

  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash;
      const match = hash.match(/#\/?waitlist\/([^/]+)/);
      setCurrentPartyId(match ? match[1] : null);
    };

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const handleOpenGuestView = (partyId: string) => {
    window.location.hash = `/waitlist/${partyId}`;
    setCurrentPartyId(partyId);
  };

  const handleBackToDashboard = () => {
    window.location.hash = '';
    setCurrentPartyId(null);
  };

  if (currentPartyId) {
    return <GuestTracker partyId={currentPartyId} onBackToDashboard={handleBackToDashboard} />;
  }

  return <HostDashboard onOpenGuestView={handleOpenGuestView} />;
}

export default App;
