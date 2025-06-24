import axios from 'axios';

// Dynamic API URL detection with fallback discovery - v2.0 CACHE BUSTER
let API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8504';

// Common backend ports to try (8504 first as it's the standard backend port)
const BACKEND_PORTS = [8504, 8506, 8501, 8502, 8503, 8500, 8505];

console.log('🔄 API.js loaded - trying backend ports:', BACKEND_PORTS);

// Function to test if a backend URL is working
const testBackendUrl = async (url) => {
  try {
    console.log(`🔍 Testing backend URL: ${url}`);
    const response = await fetch(`${url}/status?cache_bust=${Date.now()}`, { 
      method: 'GET',
      signal: AbortSignal.timeout(3000),
      cache: 'no-cache',
      headers: {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
      }
    });
    const isOk = response.ok;
    console.log(`${isOk ? '✅' : '❌'} Backend test result for ${url}: ${isOk}`);
    return isOk;
  } catch (error) {
    console.log(`❌ Backend test failed for ${url}:`, error.message);
    return false;
  }
};

// Auto-discover backend URL
const discoverBackendUrl = async () => {
  const currentHost = window.location.hostname;
  
  // First try environment variable (skip if it's the wrong port)
  if (process.env.REACT_APP_API_URL && process.env.REACT_APP_API_URL !== 'http://localhost:8500') {
    const isWorking = await testBackendUrl(process.env.REACT_APP_API_URL);
    if (isWorking) {
      API_BASE_URL = process.env.REACT_APP_API_URL;
      return API_BASE_URL;
    }
  }
  
  // Try common ports
  for (const port of BACKEND_PORTS) {
    const testUrl = `http://${currentHost}:${port}`;
    const isWorking = await testBackendUrl(testUrl);
    if (isWorking) {
      API_BASE_URL = testUrl;
      console.log(`✅ Auto-discovered backend at: ${API_BASE_URL}`);
      return API_BASE_URL;
    }
  }
  
  // Fallback to default
  console.warn('⚠️ Could not auto-discover backend, using default');
  return API_BASE_URL;
};

// Create dynamic axios instance that updates with discovered URL
const createApiInstance = () => {
  return axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });
};

let api = createApiInstance();

// Track if discovery is complete
let discoveryPromise = null;

// Add request interceptor to include user info
const addInterceptors = (instance) => {
  instance.interceptors.request.use((config) => {
    // Update baseURL with current API_BASE_URL in case it changed
    config.baseURL = API_BASE_URL;
    // Get current Windows user (if available)
    const username = process.env.USERNAME || 'webapp-user';
    config.headers['x-user'] = username;
    return config;
  });
};

addInterceptors(api);

// Update API instance when backend URL is discovered
const updateApiInstance = async () => {
  await discoverBackendUrl();
  api = createApiInstance();
  addInterceptors(api);
};

// Initialize the discovery and update
discoveryPromise = updateApiInstance();


// API functions with dynamic endpoint discovery
export const sendChatMessage = async (message, sessionId = null) => {
  try {
    const payload = { message };
    if (sessionId) {
      payload.session_id = sessionId;
    }
    const response = await api.post('/chat', payload);
    return response.data;
  } catch (error) {
    // If connection fails, try to auto-discover backend
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
      console.warn('Backend connection failed, attempting auto-discovery...');
      // Could implement port scanning here if needed
    }
    
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw new Error('Fout bij versturen van bericht: ' + error.message);
  }
};

export const checkSystemStatus = async () => {
  try {
    // Wait for discovery to complete if still in progress
    if (discoveryPromise) {
      await discoveryPromise;
      discoveryPromise = null;
    }
    const response = await api.get('/status');
    return response.data;
  } catch (error) {
    throw new Error('Kan systeemstatus niet ophalen: ' + error.message);
  }
};

export const testSqlConnection = async () => {
  try {
    const response = await api.get('/test_sql');
    return response.data;
  } catch (error) {
    throw new Error('SQL test gefaald: ' + error.message);
  }
};

export const testAdConnection = async () => {
  try {
    const response = await api.get('/test_ad');
    return response.data;
  } catch (error) {
    throw new Error('AD test gefaald: ' + error.message);
  }
};

export const submitClarification = async (clarificationData) => {
  try {
    const response = await api.post('/submit_clarification', clarificationData);
    return response.data;
  } catch (error) {
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw new Error('Fout bij versturen van verduidelijking: ' + error.message);
  }
};

export const testClaudeConnection = async () => {
  try {
    const response = await api.get('/test_claude');
    return response.data;
  } catch (error) {
    throw new Error('Claude test gefaald: ' + error.message);
  }
};

export const sendFeedback = async (feedbackData) => {
  try {
    const response = await api.post('/feedback', feedbackData);
    return response.data;
  } catch (error) {
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw new Error('Fout bij versturen van feedback: ' + error.message);
  }
};

export const sendClarification = async (originalQuestion, clarificationAnswer) => {
  try {
    const response = await api.post('/clarification', {
      original_question: originalQuestion,
      clarification_answer: clarificationAnswer
    });
    return response.data;
  } catch (error) {
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw new Error('Fout bij verwerken van verduidelijking: ' + error.message);
  }
};

export default api;