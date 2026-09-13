'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { collaborationApi } from '../../services/collaborationApi';

type Collaboration = { id: number; name: string };

export default function CollaborationsPage() {
  const router = useRouter();
  const [collaborations, setCollaborations] = useState<Collaboration[]>([]);
  const [name, setName] = useState('My job search team');
  const [email, setEmail] = useState('');
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [inviteUrl, setInviteUrl] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!localStorage.getItem('token')) {
      router.push('/login');
      return;
    }
    collaborationApi.list()
      .then((items) => {
        setCollaborations(items);
        if (items[0]) setSelectedId(items[0].id);
      })
      .catch(() => setMessage('Could not load collaborations.'))
      .finally(() => setLoading(false));
  }, [router]);

  const createCollaboration = async () => {
    setMessage('');
    try {
      const collaboration = await collaborationApi.create(name);
      setCollaborations((current) => [...current, collaboration]);
      setSelectedId(collaboration.id);
      setMessage('Collaboration created. Invite someone to join it.');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Could not create collaboration.');
    }
  };

  const createInvitation = async () => {
    if (!selectedId || !email) return;
    setMessage('');
    try {
      const invitation = await collaborationApi.invite(selectedId, email);
      setInviteUrl(invitation.invite_url);
      setMessage('Invitation link created. Copy it and send it to your friend.');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Could not create invitation.');
    }
  };

  const copyLink = async () => {
    await navigator.clipboard.writeText(inviteUrl);
    setMessage('Invitation link copied.');
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;

  return (
    <main className="min-h-screen bg-gray-50 px-4 py-10">
      <div className="mx-auto max-w-2xl">
        <button onClick={() => router.push('/dashboard')} className="mb-6 text-indigo-600 hover:text-indigo-800">← Dashboard</button>
        <div className="rounded-lg bg-white p-8 shadow-md">
          <h1 className="mb-2 text-3xl font-bold text-gray-900">Collaborate with your team</h1>
          <p className="mb-8 text-gray-600">Create a shared space and invite a friend with a secure link.</p>

          {message && <div className="mb-5 rounded bg-indigo-50 p-3 text-indigo-700">{message}</div>}

          <section className="mb-8 border-b border-gray-200 pb-8">
            <h2 className="mb-3 text-lg font-semibold">Create a collaboration</h2>
            <div className="flex gap-3">
              <input value={name} onChange={(event) => setName(event.target.value)} className="min-w-0 flex-1 rounded border px-4 py-3" placeholder="Collaboration name" />
              <button onClick={createCollaboration} className="rounded bg-indigo-600 px-5 py-3 font-semibold text-white hover:bg-indigo-700">Create</button>
            </div>
          </section>

          <section>
            <h2 className="mb-3 text-lg font-semibold">Invite a friend</h2>
            {collaborations.length === 0 ? (
              <p className="text-gray-600">Create a collaboration first.</p>
            ) : (
              <>
                <select value={selectedId ?? ''} onChange={(event) => setSelectedId(Number(event.target.value))} className="mb-3 w-full rounded border px-4 py-3">
                  {collaborations.map((collaboration) => <option key={collaboration.id} value={collaboration.id}>{collaboration.name}</option>)}
                </select>
                <div className="flex gap-3">
                  <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} className="min-w-0 flex-1 rounded border px-4 py-3" placeholder="friend@example.com" />
                  <button onClick={createInvitation} className="rounded bg-emerald-600 px-5 py-3 font-semibold text-white hover:bg-emerald-700">Create link</button>
                </div>
                {inviteUrl && (
                  <div className="mt-4 flex gap-3">
                    <input readOnly value={inviteUrl} className="min-w-0 flex-1 rounded border bg-gray-50 px-4 py-3 text-sm" />
                    <button onClick={copyLink} className="rounded bg-gray-800 px-5 py-3 font-semibold text-white hover:bg-gray-900">Copy</button>
                  </div>
                )}
              </>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}