import React, { useState } from 'react';
import { Upload, FileImage, Stethoscope, Zap, AlertCircle, CheckCircle2, Camera, Activity } from 'lucide-react';

// TextToSpeech component
const TextToSpeech = ({ text }) => {
  const speak = () => {
    if ("speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "en-US";
      utterance.rate = 1;
      utterance.pitch = 1;
      window.speechSynthesis.speak(utterance);
    } else {
      alert("Sorry, your browser does not support Text-to-Speech.");
    }
  };

  if (!text) return null;

  return (
    <button 
      onClick={speak} 
      className="mt-4 flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
    >
      <Activity className="w-4 h-4" />
      🔊 Read Aloud
    </button>
  );
};

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [symptoms, setSymptoms] = useState('');
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

    // Simulate API call
    setTimeout(() => {
      setResult({
        fused_prediction: "Lumpy Skin Disease",
        fused_confidence: "87.4%",
        image_prediction: "Lumpy Skin Disease",
        image_confidence: "82.1%",
        symptom_prediction: "Lumpy Skin Disease",
        symptom_confidence: "92.7%"
      });
      setLoading(false);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Stethoscope className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                AI Cow Disease Detector
              </h1>
              <p className="text-gray-400 text-sm">Multi-modal diagnostic analysis system</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-full">
          {/* Input Section */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
            <div className="bg-gradient-to-r from-gray-700 to-gray-800 px-6 py-4 border-b border-gray-700">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <Upload className="w-5 h-5 text-blue-400" />
                Input Data
              </h2>
              <p className="text-gray-400 text-sm mt-1">Upload image and describe symptoms</p>
            </div>

            <div className="p-6 space-y-6">
              {/* File Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-3 flex items-center gap-2">
                  <Camera className="w-4 h-4" />
                  1. Upload Skin Image
                </label>
                <div className="relative">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    id="fileInput"
                  />
                  <div className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                    selectedFile 
                      ? 'border-blue-500 bg-blue-500/10' 
                      : 'border-gray-600 hover:border-gray-500 bg-gray-900/50'
                  }`}>
                    {preview ? (
                      <div className="space-y-3">
                        <img 
                          src={preview} 
                          alt="Preview" 
                          className="max-w-full max-h-48 mx-auto rounded-lg border border-gray-600"
                        />
                        <p className="text-sm text-green-400 flex items-center justify-center gap-2">
                          <CheckCircle2 className="w-4 h-4" />
                          {selectedFile.name}
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        <FileImage className="w-12 h-12 text-gray-500 mx-auto" />
                        <div>
                          <p className="text-gray-300">Click to upload an image</p>
                          <p className="text-sm text-gray-500">PNG, JPG up to 10MB</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Symptoms Input */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-3 flex items-center gap-2">
                  <Stethoscope className="w-4 h-4" />
                  2. Describe Symptoms
                </label>
                <textarea
                  value={symptoms}
                  onChange={(e) => setSymptoms(e.target.value)}
                  placeholder="e.g., high fever, skin nodules, not eating, lethargy, swollen lymph nodes..."
                  rows="6"
                  className="w-full p-4 bg-gray-900 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-colors resize-none"
                />
                <p className="text-xs text-gray-500 mt-2">
                  Provide detailed symptoms for better accuracy
                </p>
              </div>

              {/* Analyze Button */}
              <button
                onClick={handlePredict}
                disabled={!selectedFile || !symptoms.trim() || loading}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-700 disabled:to-gray-700 disabled:cursor-not-allowed text-white font-semibold py-4 px-6 rounded-lg transition-all duration-200 flex items-center justify-center gap-3 group"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Zap className="w-5 h-5 group-hover:scale-110 transition-transform" />
                    Get AI Diagnosis
                  </>
                )}
              </button>

              {/* Error Message */}
              {error && (
                <div className="bg-red-900/30 border border-red-700 rounded-lg p-4 flex items-center gap-3">
                  <AlertCircle className="w-5 h-5 text-red-400" />
                  <p className="text-red-400">{error}</p>
                </div>
              )}
            </div>
          </div>

          {/* Output Section */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
            <div className="bg-gradient-to-r from-gray-700 to-gray-800 px-6 py-4 border-b border-gray-700">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <Activity className="w-5 h-5 text-green-400" />
                Diagnosis Results
              </h2>
              <p className="text-gray-400 text-sm mt-1">AI-powered multi-modal analysis</p>
            </div>

            <div className="p-6">
              {!result && !loading && (
                <div className="text-center py-12">
                  <Activity className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-400 mb-2">Ready for Analysis</h3>
                  <p className="text-gray-500">Upload an image and describe symptoms to get started</p>
                </div>
              )}

              {loading && (
                <div className="text-center py-12">
                  <div className="w-16 h-16 border-4 border-gray-700 border-t-blue-500 rounded-full animate-spin mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-300 mb-2">Processing...</h3>
                  <p className="text-gray-500">Our AI is analyzing the image and symptoms</p>
                </div>
              )}

              {result && (
                <div className="space-y-6">
                  {/* Main Result */}
                  <div className={`p-6 rounded-lg border-l-4 ${
                    result.fused_prediction.toLowerCase().includes('normal') 
                      ? 'bg-green-900/20 border-green-500' 
                      : 'bg-red-900/20 border-red-500'
                  }`}>
                    <h3 className="text-xl font-bold mb-2 flex items-center gap-3">
                      {result.fused_prediction.toLowerCase().includes('normal') ? (
                        <CheckCircle2 className="w-6 h-6 text-green-400" />
                      ) : (
                        <AlertCircle className="w-6 h-6 text-red-400" />
                      )}
                      Final Diagnosis
                    </h3>
                    <div className="space-y-2">
                      <p className="text-2xl font-bold text-white">{result.fused_prediction}</p>
                      <p className="text-lg">
                        <span className="text-gray-400">Confidence:</span>
                        <span className="ml-2 font-semibold text-blue-400">{result.fused_confidence}</span>
                      </p>
                    </div>
                  </div>

                  {/* Sub Results */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-gray-900/50 p-4 rounded-lg border border-gray-700">
                      <h4 className="font-semibold text-blue-400 mb-2 flex items-center gap-2">
                        <FileImage className="w-4 h-4" />
                        Image Analysis
                      </h4>
                      <p className="text-white font-medium">{result.image_prediction}</p>
                      <p className="text-sm text-gray-400">Confidence: {result.image_confidence}</p>
                    </div>

                    <div className="bg-gray-900/50 p-4 rounded-lg border border-gray-700">
                      <h4 className="font-semibold text-purple-400 mb-2 flex items-center gap-2">
                        <Stethoscope className="w-4 h-4" />
                        Symptom Analysis
                      </h4>
                      <p className="text-white font-medium">{result.symptom_prediction}</p>
                      <p className="text-sm text-gray-400">Confidence: {result.symptom_confidence}</p>
                    </div>
                  </div>

                  {/* Text to Speech */}
                  <div className="pt-4 border-t border-gray-700">
                    <TextToSpeech
                      text={`Final Diagnosis: ${result.fused_prediction}. 
                            Confidence: ${result.fused_confidence}. 
                            Image analysis shows ${result.image_prediction}. 
                            Symptom analysis indicates ${result.symptom_prediction}.`}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;