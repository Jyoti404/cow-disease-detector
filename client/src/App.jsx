import React, { useState, useEffect } from 'react';

// Translation helper function
const translatePrediction = (prediction, language) => {
  if (language !== 'hi') return prediction;
  
  const translations = {
    'Lumpy Skin Disease': 'लम्पी स्किन डिजीज',
    'lumpy skin disease': 'लम्पी स्किन डिजीज',
    'Lumpy Skin': 'लम्पी स्किन',
    'lumpy skin': 'लम्पी स्किन',
    'Normal Skin': 'सामान्य त्वचा',
    'normal skin': 'सामान्य त्वचा',
    'Normal': 'सामान्य',
    'normal': 'सामान्य',
    'Healthy': 'स्वस्थ',
    'healthy': 'स्वस्थ'
  };
  
  return translations[prediction] || prediction;
};

// TextToSpeech Component
const TextToSpeech = ({ text, language = 'en-US' }) => {
  const [isReading, setIsReading] = useState(false);

  const handleSpeak = () => {
    if (!text) return;
    
    if ("speechSynthesis" in window) {
      // Stop any ongoing speech first
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = language;
      utterance.rate = 0.9; // Slightly slower for better understanding
      utterance.pitch = 1;
      
      // Event listeners for speech status
      utterance.onstart = () => setIsReading(true);
      utterance.onend = () => setIsReading(false);
      utterance.onerror = () => setIsReading(false);
      
      setIsReading(true);
      window.speechSynthesis.speak(utterance);
    } else {
      alert(language === 'hi-IN' 
        ? "क्षमा करें, आपका ब्राउज़र टेक्स्ट-टू-स्पीच का समर्थन नहीं करता।" 
        : "Sorry, your browser does not support Text-to-Speech."
      );
    }
  };

  const handleStop = () => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      setIsReading(false);
    }
  };

  if (!text) return null;

  return (
    <div className="flex gap-2">
      <button 
        onClick={handleSpeak} 
        disabled={isReading}
        className={`flex items-center gap-2 px-4 py-2 text-white rounded-lg transition-colors border border-gray-600 ${
          isReading 
            ? 'bg-gray-700 cursor-not-allowed opacity-50' 
            : 'bg-gray-800 hover:bg-gray-700 hover:border-gray-500'
        }`}
      >
        <span className="text-sm">🔊</span>
        {language === 'hi-IN' ? 'बोलें' : 'Read Aloud'}
      </button>
      
      {isReading && (
        <button 
          onClick={handleStop}
          className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors border border-red-500 hover:border-red-400"
        >
          <span className="text-sm">⏹️</span>
          {language === 'hi-IN' ? 'रोकें' : 'Stop'}
        </button>
      )}
    </div>
  );
};

// Language Switcher Component
const LanguageSwitcher = ({ currentLang, onLanguageChange }) => {
  return (
    <div className="flex items-center gap-2 bg-gray-800 rounded-lg p-1">
      <button
        onClick={() => onLanguageChange('en')}
        className={`px-3 py-1 rounded text-sm transition-colors ${
          currentLang === 'en' 
            ? 'bg-blue-600 text-white' 
            : 'text-gray-300 hover:bg-gray-700'
        }`}
      >
        EN
      </button>
      <button
        onClick={() => onLanguageChange('hi')}
        className={`px-3 py-1 rounded text-sm transition-colors ${
          currentLang === 'hi' 
            ? 'bg-blue-600 text-white' 
            : 'text-gray-300 hover:bg-gray-700'
        }`}
      >
        हिं
      </button>
    </div>
  );
};

// Disease Information Component
const DiseaseInfo = ({ disease, language }) => {
  const diseaseData = {
    'Lumpy Skin Disease': {
      en: {
        description: 'A viral disease affecting cattle and buffalo, characterized by skin nodules and fever.',
        symptoms: ['Skin nodules', 'High fever', 'Loss of appetite', 'Swollen lymph nodes', 'Reduced milk production'],
        treatment: 'Supportive care, isolation, vaccination of healthy animals, consult veterinarian immediately.',
        prevention: 'Regular vaccination, vector control, quarantine of affected animals.'
      },
      hi: {
        description: 'एक वायरल रोग जो मवेशियों और भैंसों को प्रभावित करता है, जिसमें त्वचा की गांठें और बुखार होता है।',
        symptoms: ['त्वचा की गांठें', 'तेज बुखार', 'भूख न लगना', 'सूजी हुई लसीका ग्रंथियां', 'दूध उत्पादन में कमी'],
        treatment: 'सहायक देखभाल, अलगाव, स्वस्थ जानवरों का टीकाकरण, तुरंत पशु चिकित्सक से सलाह लें।',
        prevention: 'नियमित टीकाकरण, वेक्टर नियंत्रण, प्रभावित जानवरों की संगरोध।'
      }
    },
    'लम्पी स्किन डिजीज': {
      en: {
        description: 'A viral disease affecting cattle and buffalo, characterized by skin nodules and fever.',
        symptoms: ['Skin nodules', 'High fever', 'Loss of appetite', 'Swollen lymph nodes', 'Reduced milk production'],
        treatment: 'Supportive care, isolation, vaccination of healthy animals, consult veterinarian immediately.',
        prevention: 'Regular vaccination, vector control, quarantine of affected animals.'
      },
      hi: {
        description: 'एक वायरल रोग जो मवेशियों और भैंसों को प्रभावित करता है, जिसमें त्वचा की गांठें और बुखार होता है।',
        symptoms: ['त्वचा की गांठें', 'तेज बुखार', 'भूख न लगना', 'सूजी हुई लसीका ग्रंथियां', 'दूध उत्पादन में कमी'],
        treatment: 'सहायक देखभाल, अलगाव, स्वस्थ जानवरों का टीकाकरण, तुरंत पशु चिकित्सक से सलाह लें।',
        prevention: 'नियमित टीकाकरण, वेक्टर नियंत्रण, प्रभावित जानवरों की संगरोध।'
      }
    },
    'Normal Skin': {
      en: {
        description: 'Healthy skin condition with no signs of disease or infection.',
        symptoms: ['Smooth skin texture', 'Normal temperature', 'Good appetite', 'Active behavior'],
        treatment: 'No treatment required. Continue regular health monitoring.',
        prevention: 'Maintain good hygiene, balanced nutrition, regular health check-ups.'
      },
      hi: {
        description: 'स्वस्थ त्वचा की स्थिति जिसमें कोई रोग या संक्रमण के संकेत नहीं हैं।',
        symptoms: ['चिकनी त्वचा', 'सामान्य तापमान', 'अच्छी भूख', 'सक्रिय व्यवहार'],
        treatment: 'कोई इलाज की आवश्यकता नहीं। नियमित स्वास्थ्य निगरानी जारी रखें।',
        prevention: 'अच्छी स्वच्छता बनाए रखें, संतुलित पोषण, नियमित स्वास्थ्य जांच।'
      }
    },
    'सामान्य त्वचा': {
      en: {
        description: 'Healthy skin condition with no signs of disease or infection.',
        symptoms: ['Smooth skin texture', 'Normal temperature', 'Good appetite', 'Active behavior'],
        treatment: 'No treatment required. Continue regular health monitoring.',
        prevention: 'Maintain good hygiene, balanced nutrition, regular health check-ups.'
      },
      hi: {
        description: 'स्वस्थ त्वचा की स्थिति जिसमें कोई रोग या संक्रमण के संकेत नहीं हैं।',
        symptoms: ['चिकनी त्वचा', 'सामान्य तापमान', 'अच्छी भूख', 'सक्रिय व्यवहार'],
        treatment: 'कोई इलाज की आवश्यकता नहीं। नियमित स्वास्थ्य निगरानी जारी रखें।',
        prevention: 'अच्छी स्वच्छता बनाए रखें, संतुलित पोषण, नियमित स्वास्थ्य जांच।'
      }
    }
  };

  const info = diseaseData[disease]?.[language] || diseaseData[disease]?.en;
  if (!info) return null;

  const labels = {
    en: {
      about: 'About',
      symptoms: 'Symptoms',
      treatment: 'Treatment',
      prevention: 'Prevention'
    },
    hi: {
      about: 'विवरण',
      symptoms: 'लक्षण',
      treatment: 'इलाज',
      prevention: 'रोकथाम'
    }
  };

  const currentLabels = labels[language];

  return (
    <div className="mt-6 bg-gray-900/50 rounded-lg p-6 border border-gray-700">
      <h3 className="text-lg font-bold text-blue-400 mb-4 flex items-center gap-2">
        <span>📚</span>
        {currentLabels.about} {disease}
      </h3>
      
      <div className="space-y-4">
        <div>
          <p className="text-gray-300">{info.description}</p>
        </div>
        
        <div>
          <h4 className="font-semibold text-yellow-400 mb-2">{currentLabels.symptoms}:</h4>
          <ul className="list-disc list-inside text-gray-300 space-y-1">
            {info.symptoms.map((symptom, index) => (
              <li key={index}>{symptom}</li>
            ))}
          </ul>
        </div>
        
        <div>
          <h4 className="font-semibold text-green-400 mb-2">{currentLabels.treatment}:</h4>
          <p className="text-gray-300">{info.treatment}</p>
        </div>
        
        <div>
          <h4 className="font-semibold text-purple-400 mb-2">{currentLabels.prevention}:</h4>
          <p className="text-gray-300">{info.prevention}</p>
        </div>
      </div>
    </div>
  );
};

// History Log Component
const HistoryLog = ({ language, refreshTrigger }) => {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const savedHistory = JSON.parse(localStorage.getItem('cowDiseaseHistory') || '[]');
    setHistory(savedHistory);
  }, [refreshTrigger]);

  const labels = {
    en: {
      title: 'Recent Predictions',
      noHistory: 'No predictions yet',
      confidence: 'Confidence'
    },
    hi: {
      title: 'हाल की भविष्यवाणियां',
      noHistory: 'अभी तक कोई भविष्यवाणी नहीं',
      confidence: 'विश्वास'
    }
  };

  const currentLabels = labels[language];

  if (history.length === 0) {
    return (
      <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-gray-300 mb-4 flex items-center gap-2">
          <span>📋</span>
          {currentLabels.title}
        </h3>
        <p className="text-gray-500 text-center py-4">{currentLabels.noHistory}</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
      <h3 className="text-lg font-semibold text-gray-300 mb-4 flex items-center gap-2">
        <span>📋</span>
        {currentLabels.title}
      </h3>
      <div className="space-y-3">
        {history.slice(0, 5).map((entry, index) => (
          <div key={index} className="bg-gray-900/50 rounded-lg p-3 border border-gray-700">
            <div className="flex items-center justify-between">
              <span className={`font-medium ${
                entry.result.toLowerCase().includes('normal') ? 'text-green-400' : 'text-red-400'
              }`}>
                {entry.result}
              </span>
              <span className="text-blue-400 text-sm">{entry.confidence}</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">{entry.timestamp}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [symptoms, setSymptoms] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [language, setLanguage] = useState('en');
  const [historyRefresh, setHistoryRefresh] = useState(0);

  const labels = {
    en: {
      title: 'AI Cow Disease Detector',
      subtitle: 'Multi-modal diagnostic analysis system',
      inputData: 'Input Data',
      inputSubtitle: 'Upload image and describe symptoms',
      uploadImage: '1. Upload Skin Image',
      uploadPlaceholder: 'Click to upload an image',
      fileFormat: 'PNG, JPG up to 10MB',
      describeSymptoms: '2. Describe Symptoms',
      symptomsPlaceholder: 'e.g., high fever, skin nodules, not eating, lethargy, swollen lymph nodes...',
      symptomsHelp: 'Provide detailed symptoms for better accuracy',
      analyzeButton: 'Get AI Diagnosis',
      analyzing: 'Analyzing...',
      diagnosisResults: 'Diagnosis Results',
      diagnosisSubtitle: 'AI-powered multi-modal analysis',
      readyForAnalysis: 'Ready for Analysis',
      readyMessage: 'Upload an image and describe symptoms to get started',
      processing: 'Processing...',
      processingMessage: 'Our AI is analyzing the image and symptoms',
      finalDiagnosis: 'Final Diagnosis',
      confidence: 'Confidence',
      imageAnalysis: 'Image Analysis',
      symptomAnalysis: 'Symptom Analysis',
      errorSelectImage: 'Please select an image first.',
      errorDescribeSymptoms: 'Please describe the symptoms.',
      errorPrediction: 'Failed to get a prediction. Is the backend server running?'
    },
    hi: {
      title: 'एआई गाय रोग पहचान',
      subtitle: 'बहु-मोडल निदान विश्लेषण प्रणाली',
      inputData: 'इनपुट डेटा',
      inputSubtitle: 'छवि अपलोड करें और लक्षण बताएं',
      uploadImage: '1. त्वचा की छवि अपलोड करें',
      uploadPlaceholder: 'छवि अपलोड करने के लिए क्लिक करें',
      fileFormat: 'PNG, JPG 10MB तक',
      describeSymptoms: '2. लक्षणों का वर्णन करें',
      symptomsPlaceholder: 'जैसे, तेज बुखार, त्वचा की गांठें, न खाना, सुस्ती, सूजी हुई लसीका ग्रंथियां...',
      symptomsHelp: 'बेहतर सटीकता के लिए विस्तृत लक्षण प्रदान करें',
      analyzeButton: 'एआई निदान प्राप्त करें',
      analyzing: 'विश्लेषण कर रहे हैं...',
      diagnosisResults: 'निदान परिणाम',
      diagnosisSubtitle: 'एआई-संचालित बहु-मोडल विश्लेषण',
      readyForAnalysis: 'विश्लेषण के लिए तैयार',
      readyMessage: 'शुरू करने के लिए एक छवि अपलोड करें और लक्षणों का वर्णन करें',
      processing: 'प्रसंस्करण...',
      processingMessage: 'हमारा एआई छवि और लक्षणों का विश्लेषण कर रहा है',
      finalDiagnosis: 'अंतिम निदान',
      confidence: 'विश्वास',
      imageAnalysis: 'छवि विश्लेषण',
      symptomAnalysis: 'लक्षण विश्लेषण',
      errorSelectImage: 'कृपया पहले एक छवि चुनें।',
      errorDescribeSymptoms: 'कृपया लक्षणों का वर्णन करें।',
      errorPrediction: 'भविष्यवाणी प्राप्त करने में विफल। क्या बैकएंड सर्वर चल रहा है?'
    }
  };

  const currentLabels = labels[language];

  const saveToHistory = (prediction) => {
    const translatedPrediction = translatePrediction(prediction.fused_prediction, language);
    const historyEntry = {
      result: translatedPrediction,
      confidence: prediction.fused_confidence,
      timestamp: new Date().toLocaleString(language === 'hi' ? 'hi-IN' : 'en-US'),
      imageAnalysis: translatePrediction(prediction.image_prediction, language),
      symptomAnalysis: translatePrediction(prediction.symptom_prediction, language)
    };

    const existingHistory = JSON.parse(localStorage.getItem('cowDiseaseHistory') || '[]');
    const newHistory = [historyEntry, ...existingHistory.slice(0, 4)];
    localStorage.setItem('cowDiseaseHistory', JSON.stringify(newHistory));
    
    // Trigger history refresh
    setHistoryRefresh(prev => prev + 1);
  };

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
      setError(currentLabels.errorSelectImage);
      return;
    }
    if (!symptoms) {
      setError(currentLabels.errorDescribeSymptoms);
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('symptoms', symptoms);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/predict`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
      saveToHistory(data);
    } catch (err) {
      setError(currentLabels.errorPrediction);
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-xl">🩺</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  {currentLabels.title}
                </h1>
                <p className="text-gray-400 text-sm">{currentLabels.subtitle}</p>
              </div>
            </div>
            <LanguageSwitcher currentLang={language} onLanguageChange={setLanguage} />
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* History Log - Full width on top */}
        <div className="mb-8">
          <HistoryLog language={language} refreshTrigger={historyRefresh} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-full">
          {/* Input Section */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
            <div className="bg-gradient-to-r from-gray-700 to-gray-800 px-6 py-4 border-b border-gray-700">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <span className="text-blue-400">📤</span>
                {currentLabels.inputData}
              </h2>
              <p className="text-gray-400 text-sm mt-1">{currentLabels.inputSubtitle}</p>
            </div>

            <div className="p-6 space-y-6">
              {/* File Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-3 flex items-center gap-2">
                  <span>📷</span>
                  {currentLabels.uploadImage}
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
                          <span>✅</span>
                          {selectedFile.name}
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        <div className="text-4xl text-gray-500">🖼️</div>
                        <div>
                          <p className="text-gray-300">{currentLabels.uploadPlaceholder}</p>
                          <p className="text-sm text-gray-500">{currentLabels.fileFormat}</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Symptoms Input */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-3 flex items-center gap-2">
                  <span>🩺</span>
                  {currentLabels.describeSymptoms}
                </label>
                <textarea
                  value={symptoms}
                  onChange={(e) => setSymptoms(e.target.value)}
                  placeholder={currentLabels.symptomsPlaceholder}
                  rows="6"
                  className="w-full p-4 bg-gray-900 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-colors resize-none"
                />
                <p className="text-xs text-gray-500 mt-2">
                  {currentLabels.symptomsHelp}
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
                    {currentLabels.analyzing}
                  </>
                ) : (
                  <>
                    <span className="group-hover:scale-110 transition-transform">⚡</span>
                    {currentLabels.analyzeButton}
                  </>
                )}
              </button>

              {/* Error Message */}
              {error && (
                <div className="bg-red-900/30 border border-red-700 rounded-lg p-4 flex items-center gap-3">
                  <span className="text-red-400">⚠️</span>
                  <p className="text-red-400">{error}</p>
                </div>
              )}
            </div>
          </div>

          {/* Output Section */}
          <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
            <div className="bg-gradient-to-r from-gray-700 to-gray-800 px-6 py-4 border-b border-gray-700">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <span className="text-green-400">📊</span>
                {currentLabels.diagnosisResults}
              </h2>
              <p className="text-gray-400 text-sm mt-1">{currentLabels.diagnosisSubtitle}</p>
            </div>

            <div className="p-6">
              {!result && !loading && (
                <div className="text-center py-12">
                  <div className="text-6xl text-gray-600 mb-4">📋</div>
                  <h3 className="text-lg font-medium text-gray-400 mb-2">{currentLabels.readyForAnalysis}</h3>
                  <p className="text-gray-500">{currentLabels.readyMessage}</p>
                </div>
              )}

              {loading && (
                <div className="text-center py-12">
                  <div className="w-16 h-16 border-4 border-gray-700 border-t-blue-500 rounded-full animate-spin mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-300 mb-2">{currentLabels.processing}</h3>
                  <p className="text-gray-500">{currentLabels.processingMessage}</p>
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
                        <span className="text-green-400 text-2xl">✅</span>
                      ) : (
                        <span className="text-red-400 text-2xl">⚠️</span>
                      )}
                      {currentLabels.finalDiagnosis}
                    </h3>
                    <div className="space-y-2">
                      <p className="text-2xl font-bold text-white">{translatePrediction(result.fused_prediction, language)}</p>
                      <p className="text-lg">
                        <span className="text-gray-400">{currentLabels.confidence}:</span>
                        <span className="ml-2 font-semibold text-blue-400">{result.fused_confidence}</span>
                      </p>
                    </div>
                  </div>

                  {/* Sub Results */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-gray-900/50 p-4 rounded-lg border border-gray-700">
                      <h4 className="font-semibold text-blue-400 mb-2 flex items-center gap-2">
                        <span>🖼️</span>
                        {currentLabels.imageAnalysis}
                      </h4>
                      <p className="text-white font-medium">{translatePrediction(result.image_prediction, language)}</p>
                      <p className="text-sm text-gray-400">{currentLabels.confidence}: {result.image_confidence}</p>
                    </div>

                    <div className="bg-gray-900/50 p-4 rounded-lg border border-gray-700">
                      <h4 className="font-semibold text-purple-400 mb-2 flex items-center gap-2">
                        <span>🩺</span>
                        {currentLabels.symptomAnalysis}
                      </h4>
                      <p className="text-white font-medium">{translatePrediction(result.symptom_prediction, language)}</p>
                      <p className="text-sm text-gray-400">{currentLabels.confidence}: {result.symptom_confidence}</p>
                    </div>
                  </div>

                  {/* Disease Information */}
                  <DiseaseInfo disease={translatePrediction(result.fused_prediction, language)} language={language} />

                  {/* Text to Speech */}
                  <div className="pt-4 border-t border-gray-700">
                    <TextToSpeech
                      text={language === 'hi' 
                        ? `अंतिम निदान: ${translatePrediction(result.fused_prediction, language)}। विश्वास स्तर: ${result.fused_confidence}। छवि विश्लेषण से पता चलता है ${translatePrediction(result.image_prediction, language)}। लक्षण विश्लेषण बताता है ${translatePrediction(result.symptom_prediction, language)}।`
                        : `Final Diagnosis: ${translatePrediction(result.fused_prediction, language)}. Confidence level: ${result.fused_confidence}. Image analysis shows ${translatePrediction(result.image_prediction, language)}. Symptom analysis indicates ${translatePrediction(result.symptom_prediction, language)}.`
                      }
                      language={language === 'hi' ? 'hi-IN' : 'en-US'}
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