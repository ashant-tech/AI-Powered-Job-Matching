'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function UploadCVPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [cvs, setCvs] = useState<any[]>([]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchCVs();
  }, [router]);

  const fetchCVs = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        // Fetch user's CVs
        const cvsResponse = await fetch(`http://localhost:8000/api/cv/user/${userData.id}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (cvsResponse.ok) {
          const cvsData = await cvsResponse.json();
          setCvs(cvsData);
        }
      }
    } catch (error) {
      console.error('Error fetching CVs:', error);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (validTypes.includes(selectedFile.type)) {
        setFile(selectedFile);
        setMessage('');
      } else {
        setMessage('Please upload a PDF or DOCX file');
        setFile(null);
      }
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setMessage('Please select a file to upload');
      return;
    }

    setUploading(true);
    setMessage('');

    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title || file.name);

      const response = await fetch('http://localhost:8000/api/cv/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        const cvData = await response.json();
        setMessage('CV uploaded successfully!');
        setFile(null);
        setTitle('');
        fetchCVs();
      } else {
        const errorData = await response.json();
        setMessage(errorData.detail || 'Upload failed');
      }
    } catch (error) {
      setMessage('Error uploading CV');
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyze = async (cvId: number) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/cv/${cvId}/analyze`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setMessage('CV analysis complete!');
        fetchCVs();
      } else {
        setMessage('Analysis failed');
      }
    } catch (error) {
      setMessage('Error analyzing CV');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">AI Job Matching</h1>
          <button
            onClick={() => router.push('/dashboard')}
            className="text-gray-600 hover:text-gray-900"
          >
            ← Back to Dashboard
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-2xl">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-2xl font-bold mb-6">Upload CV</h2>

          {message && (
            <div className={`mb-4 p-3 rounded ${message.includes('success') ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'}`}>
              {message}
            </div>
          )}

          <form onSubmit={handleUpload} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                CV Title
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="My Professional CV"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                CV File (PDF or DOCX)
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-500 transition">
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.docx"
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer"
                >
                  <div className="text-4xl mb-2">📄</div>
                  <div className="text-gray-600">
                    {file ? file.name : 'Click to upload or drag and drop'}
                  </div>
                  <div className="text-sm text-gray-400 mt-1">
                    PDF or DOCX files only
                  </div>
                </label>
              </div>
            </div>

            <button
              type="submit"
              disabled={!file || uploading}
              className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? 'Uploading...' : 'Upload CV'}
            </button>
          </form>
        </div>

        {/* Existing CVs */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">Your CVs</h3>
          {cvs.length === 0 ? (
            <p className="text-gray-600">No CVs uploaded yet</p>
          ) : (
            <div className="space-y-4">
              {cvs.map((cv) => (
                <div key={cv.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-semibold">{cv.title}</h4>
                      <p className="text-sm text-gray-600">
                        Uploaded: {new Date(cv.created_at).toLocaleDateString()}
                      </p>
                      {cv.skills && (
                        <p className="text-sm text-gray-600 mt-1">
                          Skills extracted: {JSON.parse(cv.skills).length}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={() => handleAnalyze(cv.id)}
                      className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition"
                    >
                      Analyze
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
