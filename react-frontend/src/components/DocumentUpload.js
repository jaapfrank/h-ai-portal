import React, { useState, useCallback } from 'react';
import { Upload, File, CheckCircle, XCircle, Clock, DollarSign, Calendar, MapPin, Briefcase } from 'lucide-react';

const DocumentUpload = () => {
  const [uploadState, setUploadState] = useState({
    isDragOver: false,
    isUploading: false,
    uploadedFiles: [],
    currentProcessing: null,
    results: []
  });

  const [formData, setFormData] = useState({
    project_code: '',
    cost_center: '',
    location: '',
    suggested_category: ''
  });

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setUploadState(prev => ({ ...prev, isDragOver: true }));
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setUploadState(prev => ({ ...prev, isDragOver: false }));
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setUploadState(prev => ({ ...prev, isDragOver: false }));
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  }, []);

  const handleFileSelect = useCallback((e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
  }, []);

  const handleFiles = (files) => {
    const validFiles = files.filter(file => {
      const validTypes = ['image/jpeg', 'image/png', 'image/tiff', 'application/pdf'];
      const maxSize = 10 * 1024 * 1024; // 10MB
      
      if (!validTypes.includes(file.type)) {
        alert(`Bestand ${file.name} heeft een ongeldig type. Ondersteund: JPEG, PNG, TIFF, PDF`);
        return false;
      }
      
      if (file.size > maxSize) {
        alert(`Bestand ${file.name} is te groot. Maximum: 10MB`);
        return false;
      }
      
      return true;
    });

    if (validFiles.length > 0) {
      setUploadState(prev => ({
        ...prev,
        uploadedFiles: [...prev.uploadedFiles, ...validFiles]
      }));
    }
  };

  const processFile = async (file) => {
    setUploadState(prev => ({
      ...prev,
      isUploading: true,
      currentProcessing: file.name
    }));

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('file', file);
      
      // Add metadata if provided
      if (formData.project_code) formDataToSend.append('project_code', formData.project_code);
      if (formData.cost_center) formDataToSend.append('cost_center', formData.cost_center);
      if (formData.location) formDataToSend.append('location', formData.location);
      if (formData.suggested_category) formDataToSend.append('suggested_category', formData.suggested_category);

      const response = await fetch('http://localhost:8504/documents/receipts/upload', {
        method: 'POST',
        headers: {
          'X-User-ID': 'demo_user' // In productie via JWT token
        },
        body: formDataToSend
      });

      const result = await response.json();

      if (response.ok) {
        setUploadState(prev => ({
          ...prev,
          results: [...prev.results, {
            filename: file.name,
            success: true,
            result: result
          }]
        }));
      } else {
        throw new Error(result.detail || 'Upload failed');
      }

    } catch (error) {
      console.error('Upload error:', error);
      setUploadState(prev => ({
        ...prev,
        results: [...prev.results, {
          filename: file.name,
          success: false,
          error: error.message
        }]
      }));
    } finally {
      setUploadState(prev => ({
        ...prev,
        isUploading: false,
        currentProcessing: null
      }));
    }
  };

  const processAllFiles = async () => {
    for (const file of uploadState.uploadedFiles) {
      await processFile(file);
    }
    setUploadState(prev => ({ ...prev, uploadedFiles: [] }));
  };

  const removeFile = (index) => {
    setUploadState(prev => ({
      ...prev,
      uploadedFiles: prev.uploadedFiles.filter((_, i) => i !== index)
    }));
  };

  const clearResults = () => {
    setUploadState(prev => ({ ...prev, results: [] }));
  };

  const getStatusIcon = (result) => {
    if (result.success) {
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    } else {
      return <XCircle className="w-5 h-5 text-red-500" />;
    }
  };

  const formatAmount = (amount) => {
    return new Intl.NumberFormat('nl-NL', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            📄 Document Upload & Verwerking
          </h2>
          <p className="text-gray-600">
            Upload facturen (PDF) of bonnetjes (JPG/PNG) voor automatische verwerking
          </p>
        </div>

        {/* Metadata Form */}
        <div className="p-6 bg-gray-50 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📋 Optional Metadata</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Briefcase className="w-4 h-4 inline mr-1" />
                Project Code
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="PROJ-001"
                value={formData.project_code}
                onChange={(e) => setFormData(prev => ({ ...prev, project_code: e.target.value }))}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <DollarSign className="w-4 h-4 inline mr-1" />
                Cost Center
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="ADMIN"
                value={formData.cost_center}
                onChange={(e) => setFormData(prev => ({ ...prev, cost_center: e.target.value }))}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <MapPin className="w-4 h-4 inline mr-1" />
                Location
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Zwolle"
                value={formData.location}
                onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Calendar className="w-4 h-4 inline mr-1" />
                Category
              </label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                value={formData.suggested_category}
                onChange={(e) => setFormData(prev => ({ ...prev, suggested_category: e.target.value }))}
              >
                <option value="">Auto detect</option>
                <option value="fuel">Brandstof</option>
                <option value="food">Maaltijd/Catering</option>
                <option value="transport">Transport</option>
                <option value="accommodation">Accommodatie</option>
                <option value="supplies">Kantoorbenodigdheden</option>
                <option value="other">Overig</option>
              </select>
            </div>
          </div>
        </div>

        {/* Upload Area */}
        <div className="p-6">
          <div
            className={`
              border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200
              ${uploadState.isDragOver 
                ? 'border-blue-400 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
              }
            `}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-2">
              Sleep bestanden hierheen of klik om te selecteren
            </p>
            <p className="text-sm text-gray-500 mb-4">
              Ondersteund: PDF, JPEG, PNG, TIFF (max 10MB per bestand)
            </p>
            <input
              type="file"
              id="file-upload"
              className="hidden"
              multiple
              accept=".pdf,.jpg,.jpeg,.png,.tiff"
              onChange={handleFileSelect}
            />
            <label
              htmlFor="file-upload"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 cursor-pointer"
            >
              Bestanden Selecteren
            </label>
          </div>

          {/* File List */}
          {uploadState.uploadedFiles.length > 0 && (
            <div className="mt-6">
              <h4 className="text-lg font-medium text-gray-900 mb-4">
                📁 Te Verwerken Bestanden ({uploadState.uploadedFiles.length})
              </h4>
              <div className="space-y-2">
                {uploadState.uploadedFiles.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <File className="w-5 h-5 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{file.name}</p>
                        <p className="text-xs text-gray-500">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <XCircle className="w-5 h-5" />
                    </button>
                  </div>
                ))}
              </div>
              <div className="mt-4 flex justify-between">
                <button
                  onClick={() => setUploadState(prev => ({ ...prev, uploadedFiles: [] }))}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Alles Wissen
                </button>
                <button
                  onClick={processAllFiles}
                  disabled={uploadState.isUploading}
                  className="px-6 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploadState.isUploading ? (
                    <>
                      <Clock className="w-4 h-4 inline mr-2 animate-spin" />
                      Verwerken...
                    </>
                  ) : (
                    'Alle Bestanden Verwerken'
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Processing Status */}
          {uploadState.currentProcessing && (
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center space-x-3">
                <Clock className="w-5 h-5 text-blue-600 animate-spin" />
                <div>
                  <p className="text-sm font-medium text-blue-900">
                    Verwerken: {uploadState.currentProcessing}
                  </p>
                  <p className="text-xs text-blue-700">
                    OCR analyse en data extractie bezig...
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Results */}
          {uploadState.results.length > 0 && (
            <div className="mt-6">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-lg font-medium text-gray-900">
                  📊 Verwerkingsresultaten ({uploadState.results.length})
                </h4>
                <button
                  onClick={clearResults}
                  className="text-sm text-gray-600 hover:text-gray-800"
                >
                  Resultaten Wissen
                </button>
              </div>
              <div className="space-y-4">
                {uploadState.results.map((result, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(result)}
                        <span className="text-sm font-medium text-gray-900">
                          {result.filename}
                        </span>
                      </div>
                      {result.success && result.result?.expense_proposal && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          {result.result.approval_status}
                        </span>
                      )}
                    </div>

                    {result.success && result.result?.expense_proposal ? (
                      <div className="bg-green-50 border border-green-200 rounded p-3">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="font-medium text-gray-700">Bedrag:</span>
                            <p className="text-green-700 font-semibold">
                              {formatAmount(result.result.expense_proposal.amount)}
                            </p>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Categorie:</span>
                            <p className="text-gray-900 capitalize">
                              {result.result.expense_proposal.category}
                            </p>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Merchant:</span>
                            <p className="text-gray-900">
                              {result.result.expense_proposal.merchant}
                            </p>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Datum:</span>
                            <p className="text-gray-900">
                              {result.result.expense_proposal.date}
                            </p>
                          </div>
                        </div>
                        <div className="mt-3">
                          <span className="font-medium text-gray-700">Beschrijving:</span>
                          <p className="text-gray-900">
                            {result.result.expense_proposal.description}
                          </p>
                        </div>
                        {result.result.expense_proposal.compliance && (
                          <div className="mt-3 text-xs">
                            <span className={`inline-flex items-center px-2 py-1 rounded-full font-medium ${
                              result.result.expense_proposal.compliance.within_policy 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {result.result.expense_proposal.compliance.within_policy 
                                ? '✓ Binnen beleid' 
                                : '⚠ Vereist goedkeuring'
                              }
                            </span>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="bg-red-50 border border-red-200 rounded p-3">
                        <p className="text-sm text-red-700">
                          <strong>Error:</strong> {result.error}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentUpload;