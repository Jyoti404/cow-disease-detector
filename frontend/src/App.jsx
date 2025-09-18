import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [symptoms, setSymptoms] = useState(''); // State for text symptoms
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setResult(null);
      setError('');
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result);
      reader.readAsDataURL(file);
    }
  };

  const handlePredict = async () => {
    if (!selectedFile) {
      setError('Please select an image first.');
      return;
    }
    if (!symptoms) {
      setError('Please describe the symptoms.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('symptoms', symptoms); // Add symptoms to the form data

    try {
      const response = await axios.post('http://127.0.0.1:8000/predict', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResult(response.data);
    } catch (err) {
      setError('Failed to get a prediction. Is the backend server running?');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>🐄 Multi-Modal Cow Disease Detector 🐄</h1>
      <p className="subtitle">Upload a skin image and describe the symptoms for a more accurate diagnosis.</p>
      
      {/* --- Image Uploader --- */}
      <div className="uploader-container">
        <input type="file" accept="image/*" onChange={handleFileChange} className="file-input" id="fileInput" />
        <label htmlFor="fileInput" className="file-label">
          {selectedFile ? selectedFile.name : '1. Choose an Image'}
        </label>
      </div>

      {preview && (
        <div className="preview-container">
          <img src={preview} alt="Selected preview" className="preview-image" />
        </div>
      )}

      {/* --- Symptom Input --- */}
      <div className="symptom-container">
        <label htmlFor="symptoms">2. Describe Symptoms</label>
        <textarea
          id="symptoms"
          value={symptoms}
          onChange={(e) => setSymptoms(e.target.value)}
          placeholder="e.g., high fever, skin nodules, not eating..."
          rows="4"
        ></textarea>
      </div>

      <button onClick={handlePredict} disabled={!selectedFile || loading} className="predict-button">
        {loading ? 'Analyzing...' : 'Get Fused Diagnosis'}
      </button>

      {error && <p className="error-message">{error}</p>}

      {/* --- Results Display --- */}
      {result && (
        <div className={`result-container ${result.fused_prediction.replace(/\s+/g, '-').toLowerCase()}`}>
          <h2>Final Diagnosis</h2>
          <p><strong>Result:</strong> {result.fused_prediction}</p>
          <p><strong>Confidence:</strong> {result.fused_confidence}</p>
          <hr />
          <div className="sub-results">
            <p><strong>Image Analysis:</strong> {result.image_prediction} (Conf: {result.image_confidence})</p>
            <p><strong>Symptom Analysis:</strong> {result.symptom_prediction} (Conf: {result.symptom_confidence})</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

