import React, { useState } from 'react';
import { generatePodcast } from '../services/api';

function GeneratorPage() {
  const [formData, setFormData] = useState({
    blog: '',
    podcast_type: 'cohost',
    audience: 'global',
    language_style: 'english'
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await generatePodcast(formData);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate podcast');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">
          Generate Podcast from Blog
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Blog Content
            </label>
            <textarea
              value={formData.blog}
              onChange={(e) => setFormData({ ...formData, blog: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              rows="10"
              placeholder="Paste your blog content here..."
              required
              maxLength={10000}
            />
            <p className="text-sm text-gray-500 mt-1">
              {formData.blog.length} / 10000 characters
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Podcast Type
              </label>
              <select
                value={formData.podcast_type}
                onChange={(e) => setFormData({ ...formData, podcast_type: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="single">Single Host</option>
                <option value="cohost">Co-Host</option>
                <option value="multi">Multi-Speaker</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Audience
              </label>
              <select
                value={formData.audience}
                onChange={(e) => setFormData({ ...formData, audience: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="global">Global</option>
                <option value="india">India</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Language Style
              </label>
              <select
                value={formData.language_style}
                onChange={(e) => setFormData({ ...formData, language_style: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="english">English</option>
                <option value="hinglish">Hinglish</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !formData.blog}
            className="w-full bg-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
          >
            {loading ? 'Generating Podcast...' : 'Generate Podcast'}
          </button>
        </form>
      </div>

      {loading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <div>
              <p className="text-blue-800 font-medium">Processing your blog...</p>
              <p className="text-blue-600 text-sm">This may take 10-20 seconds</p>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {result && (
        <div className="bg-white rounded-lg shadow-lg p-6 space-y-4">
          <h3 className="text-xl font-bold text-gray-800">Podcast Generated!</h3>
          
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Speakers</p>
                <p className="font-semibold">{result.metadata.speaker_count}</p>
              </div>
              <div>
                <p className="text-gray-600">Duration</p>
                <p className="font-semibold">{result.metadata.duration.toFixed(1)}s</p>
              </div>
              <div>
                <p className="text-gray-600">Words</p>
                <p className="font-semibold">{result.metadata.word_count}</p>
              </div>
              <div>
                <p className="text-gray-600">ID</p>
                <p className="font-semibold">#{result.id}</p>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-gray-700 mb-2">Audio Player</h4>
            <audio controls className="w-full" src={result.audio_url}>
              Your browser does not support audio playback.
            </audio>
            <a
              href={result.audio_url}
              download
              className="inline-block mt-2 text-purple-600 hover:text-purple-800 font-medium"
            >
              Download Podcast
            </a>
          </div>

          <div>
            <h4 className="font-semibold text-gray-700 mb-2">Script</h4>
            <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
              <pre className="whitespace-pre-wrap text-sm text-gray-800">
                {result.script}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default GeneratorPage;
