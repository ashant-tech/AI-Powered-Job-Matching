'use client';

import { useState } from 'react';

interface CVUploaderProps {
  onUpload: (file: File, title: string) => void;
  uploading?: boolean;
}

export default function CVUploader({ onUpload, uploading }: CVUploaderProps) {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (validTypes.includes(selectedFile.type)) {
        setFile(selectedFile);
      } else {
        alert('Please upload a PDF or DOCX file');
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (file) {
      onUpload(file, title || file.name);
      setFile(null);
      setTitle('');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4">Upload CV</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
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
            CV File
          </label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-indigo-500 transition">
            <input
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.docx"
              className="hidden"
              id="cv-file-upload"
            />
            <label
              htmlFor="cv-file-upload"
              className="cursor-pointer"
            >
              <div className="text-3xl mb-2">📄</div>
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
  );
}
