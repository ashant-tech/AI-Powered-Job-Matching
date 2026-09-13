'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { collaborationApi } from '../../../services/collaborationApi';

export default function AcceptCollaborationPage() {
  const router = useRouter();
  const [token, setToken] = useState('');
  const [invitation, setInvitation] = useState<{ collaboration_name: string; invitee_email: string } | null>(null);
  const [message, setMessage] = useState('Loading invitation...');

  useEffect(() => {
    const invitationToken = new URLSearchParams(window.location.search).get('token') || '';
    setToken(invitationToken);
    if (!invitationToken) {
      setMessage('This invitation link is missing its token.');
      return;
    }
    collaborationApi.getInvitation(invitationToken)
      .then(setInvitation)
      .catch((error) => setMessage(error instanceof Error ? error.message : 'Invalid invitation.'));
  }, []);

  const accept = async () => {
    if (!localStorage.getItem('token')) {
      router.push(`/login?returnTo=/collaborations/accept?token=${encodeURIComponent(token)}`);
      return;
    }
    try {
      await collaborationApi.accept(token);
      setMessage('You joined the collaboration successfully.');
      setTimeout(() => router.push('/collaborations'), 700);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Could not accept invitation.');
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 px-4 py-16">
      <div className="mx-auto max-w-lg rounded-lg bg-white p-8 text-center shadow-md">
        <h1 className="mb-3 text-3xl font-bold">Collaboration invitation</h1>
        {invitation ? <p className="mb-6 text-gray-600">You were invited to join <strong>{invitation.collaboration_name}</strong> as {invitation.invitee_email}.</p> : <p className="mb-6 text-red-600">{message}</p>}
        {invitation && <button onClick={accept} className="rounded bg-indigo-600 px-6 py-3 font-semibold text-white hover:bg-indigo-700">Accept invitation</button>}
        {invitation && message !== 'Loading invitation...' && <p className="mt-5 text-sm text-gray-600">{message}</p>}
      </div>
    </main>
  );
}