import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Database, Code, Eye, EyeOff, ThumbsUp, ThumbsDown, MessageSquare, BarChart3, TrendingUp, Cpu, ChevronDown, ChevronUp, Info } from 'lucide-react';
import { sendChatMessage, sendFeedback, sendClarification } from '../services/api';
import ReactMarkdown from 'react-markdown';
import InteractiveClarificationForm from './InteractiveClarificationForm';
import ConfidenceIndicator from './ConfidenceIndicator';
import CSVEnhancementIndicator from './CSVEnhancementIndicator';
import EnterpriseAnalysisIndicator from './EnterpriseAnalysisIndicator';

const ChatInterface = ({ systemStatus }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showSqlQueries, setShowSqlQueries] = useState(false);
  const [feedbackStates, setFeedbackStates] = useState({});
  const [correctionInputs, setCorrectionInputs] = useState({});
  const [sessionId, setSessionId] = useState(Date.now().toString());
  const [expandedTechnicalDetails, setExpandedTechnicalDetails] = useState({});
  const messagesEndRef = useRef(null);

  const exampleQuestions = [
    {
      icon: <BarChart3 className="h-4 w-4" />,
      text: "Hoeveel kranen dit jaar?",
      category: "⚡ Quick",
      shortcut: "K"
    },
    {
      icon: <TrendingUp className="h-4 w-4" />,
      text: "Wat is de omzet dit jaar?", 
      category: "⚡ Quick",
      shortcut: "O"
    },
    {
      icon: <Cpu className="h-4 w-4" />,
      text: "Hoeveel C6 machines dit jaar?",
      category: "⚡ Quick", 
      shortcut: "C"
    },
    {
      icon: <Database className="h-4 w-4" />,
      text: "Maak een executive dashboard",
      category: "📊 Dashboards",
      shortcut: "D"
    },
    {
      icon: <BarChart3 className="h-4 w-4" />,
      text: "Top 5 klanten dit jaar",
      category: "📈 Reports",
      shortcut: "T"
    },
    {
      icon: <TrendingUp className="h-4 w-4" />,
      text: "Vergelijk met vorig jaar",
      category: "📈 Reports", 
      shortcut: "V"
    },
    {
      icon: <Cpu className="h-4 w-4" />,
      text: "ML analyse rapporten",
      category: "🤖 ML & AI",
      shortcut: "M"
    },
    {
      icon: <BarChart3 className="h-4 w-4" />,
      text: "Toon ML statistieken",
      category: "🤖 ML & AI",
      shortcut: "S"
    }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Force enable text selection on mount and message updates
  useEffect(() => {
    const enableTextSelection = () => {
      // Force enable text selection on all elements
      document.body.style.userSelect = 'text';
      document.body.style.webkitUserSelect = 'text';
      document.body.style.mozUserSelect = 'text';
      document.body.style.msUserSelect = 'text';
      
      // Override all CSS that might prevent selection
      const style = document.createElement('style');
      style.textContent = `
        * {
          user-select: text !important;
          -webkit-user-select: text !important;
          -moz-user-select: text !important;
          -ms-user-select: text !important;
        }
        .prose, .prose *, 
        .chat-message, .chat-message *,
        div, span, p, h1, h2, h3, h4, h5, h6,
        pre, code, blockquote, li {
          user-select: text !important;
          -webkit-user-select: text !important;
          -moz-user-select: text !important;
          -ms-user-select: text !important;
          pointer-events: auto !important;
        }
      `;
      document.head.appendChild(style);
      
      // Also force enable on all existing elements
      const allElements = document.querySelectorAll('*');
      allElements.forEach(el => {
        if (el.style) {
          el.style.userSelect = 'text';
          el.style.webkitUserSelect = 'text';
          el.style.mozUserSelect = 'text';
          el.style.msUserSelect = 'text';
          el.style.pointerEvents = 'auto';
        }
      });
    };

    enableTextSelection();
    
    // Run multiple times to override any dynamic styles
    const timer1 = setTimeout(enableTextSelection, 100);
    const timer2 = setTimeout(enableTextSelection, 500);
    const timer3 = setTimeout(enableTextSelection, 1000);
    
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, [messages]);

  // Keyboard shortcuts for Lola's efficiency
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Only trigger shortcuts when not typing in input
      if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') return;
      
      if (event.ctrlKey || event.metaKey) {
        const shortcuts = {
          'k': "Hoeveel kranen dit jaar?",
          'o': "Wat is de omzet dit jaar?", 
          'c': "Hoeveel C6 machines dit jaar?",
          'd': "Maak een executive dashboard",
          't': "Top 5 klanten dit jaar",
          'v': "Vergelijk met vorig jaar",
          'm': "ML analyse rapporten",
          's': "Toon ML statistieken"
        };
        
        const shortcut = shortcuts[event.key.toLowerCase()];
        if (shortcut) {
          event.preventDefault();
          setInputValue(shortcut);
          // Auto-submit if Ctrl+Shift+Key
          if (event.shiftKey) {
            setTimeout(() => {
              document.querySelector('form').dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
            }, 100);
          }
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage(userMessage.content, sessionId);
      
      const aiMessage = {
        id: Date.now() + 1,
        type: response.suggestions && response.suggestions.length > 0 ? 'error' : 'assistant',
        content: response.response || response.antwoord, // Support both response formats
        sqlQuery: response.sql_query,
        results: response.result || response.resultaten, // Support both result formats
        chartData: response.chart_data,
        drillDownSuggestions: response.drill_down_suggestions,
        sessionId: response.session_id,
        csvEnhancement: response.csv_enhancement,
        enterpriseAnalysis: response.enterprise_analysis,
        suggestions: response.suggestions,
        suggestionType: response.suggestion_type,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: `😔 **Sorry, er is iets misgegaan**\n\n**Foutmelding:** ${error.message}\n\n**💡 Wat kunt u proberen:**\n• Herformuleer uw vraag anders\n• Wacht een moment en probeer opnieuw\n• Gebruik eenvoudigere bewoordingen\n\n**📞 Blijft het niet werken?** Neem contact op met support.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExampleClick = (question) => {
    setInputValue(question);
  };

  const toggleTechnicalDetails = (messageId) => {
    setExpandedTechnicalDetails(prev => ({
      ...prev,
      [messageId]: !prev[messageId]
    }));
  };

  const handleDrillDownClick = (suggestion) => {
    setInputValue(suggestion);
    // Auto-submit drill-down request
    setTimeout(() => {
      document.querySelector('form').dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
    }, 100);
  };

  const handleClarificationClick = async (originalQuestion, selectedOption) => {
    setIsLoading(true);
    try {
      const data = await sendClarification(originalQuestion, selectedOption);
      
      const aiMessage = {
        id: Date.now(),
        type: 'assistant',
        content: data.response || data.antwoord, // Support both response formats
        sqlQuery: data.sql_query,
        results: data.resultaten,
        chartData: data.chart_data,
        csvEnhancement: data.csv_enhancement,
        enterpriseAnalysis: data.enterprise_analysis,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now(),
        type: 'error',
        content: error.message,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = async (messageId, userQuestion, isCorrect, correctAnswer = null) => {
    try {
      await sendFeedback({
        messageId,
        question: userQuestion,
        isCorrect,
        correctAnswer
      });

      setFeedbackStates(prev => ({
        ...prev,
        [messageId]: isCorrect ? 'positive' : 'negative'
      }));

      // Clear correction input after sending
      if (!isCorrect && correctAnswer) {
        setCorrectionInputs(prev => ({
          ...prev,
          [messageId]: ''
        }));
      }
    } catch (error) {
      console.error('Feedback error:', error);
    }
  };

  const toggleCorrectionInput = (messageId) => {
    setCorrectionInputs(prev => ({
      ...prev,
      [messageId]: prev[messageId] !== undefined ? undefined : ''
    }));
  };

  const isSystemReady = systemStatus && 
    systemStatus.database?.includes('✅') && 
    systemStatus.schema?.includes('✅') && 
    systemStatus.claude_ai?.includes('✅');

  return (
    <div className="bg-white rounded-lg shadow-hoeflon-lg border border-hoeflon-200 h-[calc(100vh-200px)] flex flex-col overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-hoeflon-600 to-hoeflon-700 p-4 border-b border-hoeflon-300">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white flex items-center space-x-3">
            <div className="p-2 bg-white bg-opacity-20 rounded-lg">
              <Database className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className="block">Ridder ERP AI Assistant</span>
              <span className="text-xs text-hoeflon-100 font-normal">Industriële Data-analyse Platform</span>
            </div>
          </h2>
          <button
            onClick={() => setShowSqlQueries(!showSqlQueries)}
            className="flex items-center space-x-2 text-sm text-hoeflon-100 hover:text-white transition-colors bg-white bg-opacity-10 hover:bg-opacity-20 px-3 py-2 rounded-lg"
          >
            {showSqlQueries ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            <span>SQL Queries</span>
          </button>
        </div>
        
        {!isSystemReady && (
          <div className="mt-3 p-3 bg-yellow-400 bg-opacity-20 border border-yellow-300 rounded-lg backdrop-blur-sm">
            <p className="text-sm text-yellow-100 font-medium">
              ⚠️ Systeem is niet volledig operationeel. Controleer de status in het rechterpaneel.
            </p>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-hoeflon-25 to-white">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-hoeflon-500 to-hoeflon-600 rounded-full mb-6 shadow-hoeflon-lg">
              <Database className="h-10 w-10 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-hoeflon-800 mb-3">
              Welkom bij Ridder ERP AI Assistant
            </h3>
            <p className="text-hoeflon-600 mb-8 text-lg max-w-md mx-auto">
              Stel vragen over je bedrijfsdata en krijg direct antwoorden met grafieken en analyses.
            </p>
            
            <div className="text-left max-w-4xl mx-auto">
              <h4 className="font-semibold text-hoeflon-800 mb-4 text-center">Voorbeeldvragen:</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {exampleQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleExampleClick(question.text)}
                    className="group text-left p-4 bg-gradient-to-r from-hoeflon-50 to-hoeflon-100 hover:from-hoeflon-100 hover:to-hoeflon-200 rounded-lg border border-hoeflon-200 hover:border-hoeflon-300 text-sm transition-all duration-200 hover:shadow-hoeflon"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 p-2 bg-white rounded-md shadow-sm group-hover:bg-hoeflon-orange group-hover:text-white transition-colors">
                        {question.icon}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-medium text-hoeflon-600 bg-hoeflon-100 px-2 py-1 rounded-full">
                            {question.category}
                          </span>
                          <span className="text-xs font-mono text-hoeflon-500 bg-hoeflon-50 px-2 py-1 rounded border">
                            Ctrl+{question.shortcut}
                          </span>
                        </div>
                        <p className="text-hoeflon-800 font-medium group-hover:text-hoeflon-900">
                          {question.text}
                        </p>
                        <p className="text-xs text-hoeflon-500 mt-1">
                          💡 Druk Ctrl+Shift+{question.shortcut} voor direct uitvoeren
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.filter(message => message && message.id && message.content).map((message) => (
          <div
            key={message.id}
            className={`fade-in ${
              message.type === 'user' ? 'ml-auto' : message.type === 'error' ? 'mr-auto' : 'mr-auto'
            } max-w-3xl`}
          >
            <div
              className={`rounded-lg p-4 shadow-hoeflon ${
                message.type === 'user'
                  ? 'bg-gradient-to-r from-hoeflon-600 to-hoeflon-700 text-white'
                  : message.type === 'error'
                  ? 'bg-gradient-to-r from-red-50 to-red-100 text-red-800 border border-red-200'
                  : 'bg-gradient-to-r from-white to-hoeflon-50 text-hoeflon-900 border border-hoeflon-200'
              }`}
            >
              {/* Confidence Indicator - prominently displayed at top */}
              {message.type === 'assistant' && message.results && message.results[0] && (
                message.results[0].confidence_score !== undefined || message.results[0].is_reliable !== undefined
              ) && (
                <div className="mb-4">
                  <ConfidenceIndicator 
                    confidenceScore={message.results[0].confidence_score || 0}
                    isReliable={message.results[0].is_reliable !== false}
                    showDetails={true}
                  />
                </div>
              )}

              {/* CSV Enhancement Indicator */}
              {message.type === 'assistant' && message.csvEnhancement && (
                <CSVEnhancementIndicator
                  csvTables={message.csvEnhancement.relevant_tables}
                  isEnhanced={message.csvEnhancement.is_enhanced}
                />
              )}

              {/* Enterprise Analysis Indicator */}
              {message.type === 'assistant' && message.enterpriseAnalysis && (
                <EnterpriseAnalysisIndicator
                  enterpriseAnalysis={message.enterpriseAnalysis}
                />
              )}

              {/* Interactive Clarification Form */}
              {message.results && message.results[0] && message.results[0].type === 'interactive_clarification' && (
                <div className="mb-4">
                  <InteractiveClarificationForm
                    clarificationData={message.results[0]}
                    originalQuestion={message.results[0].original_question}
                    sessionId={sessionId}
                    confidenceScore={message.results[0].confidence_score || 0}
                    onFormSubmit={(response) => {
                      // Add the response as a new message
                      const newMessage = {
                        id: Date.now(),
                        type: 'assistant',
                        content: response.antwoord,
                        sqlQuery: response.sql_query,
                        results: response.resultaten,
                        chartData: response.chart_data
                      };
                      setMessages(prev => [...prev, newMessage]);
                      scrollToBottom();
                    }}
                  />
                </div>
              )}

              <div className="prose prose-sm max-w-none">
                {/* Simple answer detection for cleaner responses */}
                {message.content && message.content.includes('🎯 **Antwoord**:') ? (
                  <div className="space-y-3">
                    {/* Extract and highlight the main answer */}
                    {(() => {
                      const lines = message.content.split('\n');
                      const answerLine = lines.find(line => line.includes('🎯 **Antwoord**:'));
                      const questionLine = lines.find(line => line.includes('📊 **Uw vraag**:'));
                      const confidenceLine = lines.find(line => line.includes('**Resultaat**'));
                      
                      return (
                        <div>
                          {/* Confidence indicator */}
                          {confidenceLine && (
                            <div className="text-sm text-hoeflon-600 mb-2">
                              {confidenceLine}
                            </div>
                          )}
                          
                          {/* Main answer - large and prominent */}
                          {answerLine && (
                            <div className="bg-gradient-to-r from-hoeflon-50 to-hoeflon-100 p-4 rounded-lg border-l-4 border-hoeflon-500">
                              <div className="text-2xl font-bold text-hoeflon-800">
                                {answerLine.replace('🎯 **Antwoord**: ', '').replace('🎯 **Antwoord**:', '')}
                              </div>
                              {questionLine && (
                                <div className="text-sm text-hoeflon-600 mt-1">
                                  {questionLine.replace('📊 **Uw vraag**: ', '').replace('📊 **Uw vraag**:', '')}
                                </div>
                              )}
                            </div>
                          )}
                          
                          {/* Show follow-up options if available */}
                          {message.content && message.content.includes('🔍 **Interactieve commands**') && (
                            <details className="mt-3">
                              <summary className="cursor-pointer text-sm font-medium text-hoeflon-700 hover:text-hoeflon-800">
                                💡 Meer opties en details...
                              </summary>
                              <div className="mt-2 text-sm text-hoeflon-600">
                                <ReactMarkdown>{message.content}</ReactMarkdown>
                              </div>
                            </details>
                          )}
                        </div>
                      );
                    })()}
                  </div>
                ) : (
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                )}
              </div>

              {/* Chart Display */}
              {message.chartData && (
                <div className="mt-4">
                  <img 
                    src={message.chartData} 
                    alt="Grafiek" 
                    className="w-full max-w-2xl mx-auto rounded-lg border border-gray-200 shadow-sm"
                  />
                </div>
              )}

              {/* Dashboard Link - Open in new tab */}
              {message.sqlQuery && (message.sqlQuery.includes('Dashboard') || (message.content && message.content.toLowerCase().includes('dashboard'))) && (
                <div className="mt-4 p-4 bg-gradient-to-r from-hoeflon-50 to-hoeflon-100 rounded-lg border border-hoeflon-200">
                  <div className="flex items-center space-x-3 mb-3">
                    <BarChart3 className="h-5 w-5 text-hoeflon-600" />
                    <span className="font-medium text-hoeflon-800">🎯 Visueel Dashboard Beschikbaar</span>
                  </div>
                  <p className="text-sm text-hoeflon-600 mb-3">
                    Open dit dashboard in een nieuw tabblad voor volledige visualisaties en interactieve grafieken.
                  </p>
                  <button
                    onClick={() => {
                      const dashboardType = message.sqlQuery.includes('Executive') ? 'executive' : 
                                          message.sqlQuery.includes('Production') ? 'production' : 
                                          message.sqlQuery.includes('Financial') ? 'financial' : 'executive';
                      const url = `/dashboard?type=${dashboardType}&session=${sessionId}`;
                      window.open(url, '_blank');
                    }}
                    className="inline-flex items-center space-x-2 px-4 py-2 bg-hoeflon-600 text-white rounded-lg hover:bg-hoeflon-700 transition-colors"
                  >
                    <BarChart3 className="h-4 w-4" />
                    <span>Open Visueel Dashboard</span>
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </button>
                </div>
              )}

              {/* Error Recovery Suggestions */}
              {message.type === 'error' && message.suggestions && (
                <div className="mt-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                  <div className="flex items-center space-x-2 mb-3">
                    <MessageSquare className="h-5 w-5 text-blue-600" />
                    <span className="text-sm font-semibold text-blue-800">
                      💡 Bedoelde u misschien:
                    </span>
                  </div>
                  <div className="space-y-2">
                    {message.suggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => {
                          setInputValue(suggestion);
                          // Auto-submit the suggestion
                          setTimeout(() => {
                            const form = document.querySelector('form');
                            if (form) {
                              form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
                            }
                          }, 100);
                        }}
                        className="w-full text-left p-3 bg-white hover:bg-blue-50 rounded-lg border border-blue-200 hover:border-blue-300 transition-all duration-200 group shadow-sm"
                        disabled={isLoading}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-700 group-hover:text-blue-700 font-medium">
                            {index + 1}. {suggestion}
                          </span>
                          <span className="text-xs text-blue-400 group-hover:text-blue-600 transition-colors">
                            Probeer deze →
                          </span>
                        </div>
                      </button>
                    ))}
                  </div>
                  <div className="mt-3 text-xs text-blue-600 bg-blue-100 p-2 rounded">
                    💭 <strong>Tip:</strong> Klik op een van de suggesties om automatisch die vraag te stellen
                  </div>
                </div>
              )}

              {/* Clarification Options */}
              {message.results && message.results.length > 0 && (message.results[0].options || message.results[0].clarification_type) && (
                <div className="mt-4">
                  <div className="flex items-center space-x-2 mb-3">
                    <MessageSquare className="h-4 w-4 text-hoeflon-500" />
                    <span className="text-sm font-medium text-gray-700">
                      Kies een optie om door te gaan:
                    </span>
                  </div>
                  <div className="space-y-2">
                    {(message.results[0].options || []).map((option, index) => {
                      // Find the original user question
                      const userMessageIndex = messages.findIndex(m => m.id === message.id) - 1;
                      const originalQuestion = userMessageIndex >= 0 ? messages[userMessageIndex].content : '';
                      
                      return (
                        <button
                          key={index}
                          onClick={() => handleClarificationClick(originalQuestion, option)}
                          className="w-full text-left p-3 bg-hoeflon-50 hover:bg-hoeflon-100 rounded-lg border border-hoeflon-200 transition-colors group"
                          disabled={isLoading}
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-700 group-hover:text-hoeflon-700">
                              {index + 1}. {option}
                            </span>
                            <span className="text-xs text-gray-400 group-hover:text-hoeflon-500">
                              →
                            </span>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Collapsible Technical Details */}
              {message.type === 'assistant' && (message.sqlQuery || (message.results && message.results.length > 0)) && (
                <div className="mt-4 pt-3 border-t border-gray-200">
                  <button
                    onClick={() => toggleTechnicalDetails(message.id)}
                    className="flex items-center justify-between w-full p-3 bg-gradient-to-r from-gray-50 to-gray-100 hover:from-gray-100 hover:to-gray-200 rounded-lg border border-gray-200 transition-all duration-200"
                  >
                    <div className="flex items-center space-x-3">
                      <Info className="h-4 w-4 text-gray-500" />
                      <span className="text-sm font-medium text-gray-700">
                        Technische Details & Database Info
                      </span>
                      <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded-full">
                        SQL, Schema, Debugging
                      </span>
                    </div>
                    {expandedTechnicalDetails[message.id] ? (
                      <ChevronUp className="h-4 w-4 text-gray-500" />
                    ) : (
                      <ChevronDown className="h-4 w-4 text-gray-500" />
                    )}
                  </button>
                  
                  {expandedTechnicalDetails[message.id] && (
                    <div className="mt-3 space-y-4 bg-gray-50 p-4 rounded-lg border border-gray-200">
                      {/* SQL Query Display */}
                      {message.sqlQuery && (
                        <div>
                          <div className="flex items-center space-x-2 mb-2">
                            <Code className="h-4 w-4 text-gray-500" />
                            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                              Gegenereerde SQL Query
                            </span>
                          </div>
                          <pre className="bg-gray-900 text-green-400 p-3 rounded text-xs overflow-x-auto">
                            {message.sqlQuery}
                          </pre>
                        </div>
                      )}

                      {/* Results Data */}
                      {message.results && message.results.length > 0 && (
                        <div>
                          <div className="flex items-center space-x-2 mb-2">
                            <Database className="h-4 w-4 text-gray-500" />
                            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                              Ruwe Database Data ({message.results.length} resultaten)
                            </span>
                          </div>
                          <div className="bg-white border rounded p-3 max-h-40 overflow-y-auto">
                            <pre className="text-xs text-gray-700">
                              {JSON.stringify(message.results, null, 2)}
                            </pre>
                          </div>
                        </div>
                      )}

                      {/* Additional Debug Info */}
                      {message.classification && (
                        <div>
                          <div className="flex items-center space-x-2 mb-2">
                            <Info className="h-4 w-4 text-gray-500" />
                            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                              AI Classificatie & Routing
                            </span>
                          </div>
                          <div className="bg-white border rounded p-3">
                            <pre className="text-xs text-gray-700">
                              {JSON.stringify(message.classification, null, 2)}
                            </pre>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Feedback Buttons - Only for AI responses */}
              {message.type === 'assistant' && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-xs text-gray-500">Was dit antwoord correct?</span>
                      {/* Small confidence badge */}
                      {message.results && message.results[0] && message.results[0].confidence_score !== undefined && (
                        <ConfidenceIndicator 
                          confidenceScore={message.results[0].confidence_score || 0}
                          isReliable={message.results[0].is_reliable !== false}
                          showDetails={false}
                        />
                      )}
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => {
                          const userQuestion = messages[messages.findIndex(m => m.id === message.id) - 1]?.content || '';
                          handleFeedback(message.id, userQuestion, true);
                        }}
                        className={`p-1 rounded text-xs flex items-center space-x-1 transition-colors ${
                          feedbackStates[message.id] === 'positive'
                            ? 'bg-green-100 text-green-700'
                            : 'text-gray-500 hover:text-green-600 hover:bg-green-50'
                        }`}
                        disabled={feedbackStates[message.id]}
                      >
                        <ThumbsUp className="h-3 w-3" />
                        <span>Correct</span>
                      </button>
                      <button
                        onClick={() => toggleCorrectionInput(message.id)}
                        className={`p-1 rounded text-xs flex items-center space-x-1 transition-colors ${
                          feedbackStates[message.id] === 'negative'
                            ? 'bg-red-100 text-red-700'
                            : 'text-gray-500 hover:text-red-600 hover:bg-red-50'
                        }`}
                        disabled={feedbackStates[message.id] === 'positive'}
                      >
                        <ThumbsDown className="h-3 w-3" />
                        <span>Incorrect</span>
                      </button>
                    </div>
                  </div>

                  {/* Correction Input */}
                  {correctionInputs[message.id] !== undefined && (
                    <div className="mt-3 space-y-2">
                      <label className="block text-xs text-gray-600">
                        Wat is het juiste antwoord?
                      </label>
                      <div className="flex space-x-2">
                        <input
                          type="text"
                          value={correctionInputs[message.id]}
                          onChange={(e) => setCorrectionInputs(prev => ({
                            ...prev,
                            [message.id]: e.target.value
                          }))}
                          placeholder="Vul het juiste antwoord in..."
                          className="flex-1 px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-hoeflon-500"
                        />
                        <button
                          onClick={() => {
                            const userQuestion = messages[messages.findIndex(m => m.id === message.id) - 1]?.content || '';
                            handleFeedback(message.id, userQuestion, false, correctionInputs[message.id]);
                          }}
                          disabled={!correctionInputs[message.id]?.trim()}
                          className="px-3 py-1 text-xs bg-hoeflon-600 text-white rounded hover:bg-hoeflon-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          Verstuur
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Drill-Down Suggestions - Only for AI responses with suggestions */}
              {message.type === 'assistant' && message.drillDownSuggestions && message.drillDownSuggestions.length > 0 && (
                <div className="mt-3 pt-3 border-t border-hoeflon-200">
                  <div className="flex items-center space-x-2 mb-3">
                    <BarChart3 className="h-4 w-4 text-hoeflon-500" />
                    <span className="text-sm font-medium text-hoeflon-700">
                      🔍 Meer details beschikbaar:
                    </span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {message.drillDownSuggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => handleDrillDownClick(suggestion)}
                        className="text-left p-3 bg-gradient-to-r from-hoeflon-50 to-hoeflon-100 hover:from-hoeflon-100 hover:to-hoeflon-200 rounded-lg border border-hoeflon-200 hover:border-hoeflon-300 text-sm transition-all duration-200 hover:shadow-hoeflon group"
                      >
                        <div className="flex items-center space-x-2">
                          <div className="flex-shrink-0 p-1 bg-white rounded group-hover:bg-hoeflon-orange group-hover:text-white transition-colors">
                            <BarChart3 className="h-3 w-3" />
                          </div>
                          <span className="text-hoeflon-800 font-medium group-hover:text-hoeflon-900">
                            {suggestion}
                          </span>
                        </div>
                      </button>
                    ))}
                  </div>
                  <p className="text-xs text-hoeflon-500 mt-2">
                    💡 Klik op een optie om dieper in te zoomen op de data
                  </p>
                </div>
              )}

              <div className="text-xs opacity-75 mt-2">
                {message.timestamp ? new Date(message.timestamp).toLocaleTimeString('nl-NL') : new Date().toLocaleTimeString('nl-NL')}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="mr-auto max-w-3xl fade-in">
            <div className="bg-gradient-to-r from-hoeflon-50 to-hoeflon-100 border border-hoeflon-200 rounded-lg p-4 shadow-hoeflon">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <Loader2 className="h-6 w-6 animate-spin text-hoeflon-600" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="text-hoeflon-800 font-medium text-lg">🤖 Bezig met uw vraag</span>
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-hoeflon-600 rounded-full animate-pulse"></div>
                      <div className="w-2 h-2 bg-hoeflon-600 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                      <div className="w-2 h-2 bg-hoeflon-600 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
                    </div>
                  </div>
                  <p className="text-sm text-hoeflon-600 mt-1">📊 Database query uitvoeren • 🧠 AI antwoord genereren</p>
                  <div className="mt-2 w-full bg-hoeflon-200 rounded-full h-1">
                    <div className="bg-hoeflon-600 h-1 rounded-full animate-pulse" style={{width: '75%'}}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="border-t border-hoeflon-200 bg-gradient-to-r from-hoeflon-50 to-white p-4">
        <form onSubmit={handleSubmit} className="flex space-x-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onPaste={(e) => {
                // Allow default paste behavior
                e.stopPropagation();
                // Let the browser handle the paste naturally
              }}
              onCopy={(e) => {
                // Allow default copy behavior
                e.stopPropagation();
              }}
              onCut={(e) => {
                // Allow default cut behavior
                e.stopPropagation();
              }}
              placeholder="Stel je vraag aan de Ridder ERP AI Assistant..."
              className="w-full px-4 py-3 pl-12 border-2 border-hoeflon-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-hoeflon-500 focus:border-hoeflon-500 bg-white shadow-sm text-hoeflon-900 placeholder-hoeflon-400"
              disabled={isLoading || !isSystemReady}
              style={{
                userSelect: 'text',
                WebkitUserSelect: 'text',
                MozUserSelect: 'text',
                msUserSelect: 'text'
              }}
            />
            <Database className="absolute left-4 top-1/2 transform -translate-y-1/2 h-4 w-4 text-hoeflon-400" />
          </div>
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim() || !isSystemReady}
            className="px-6 py-3 bg-gradient-to-r from-hoeflon-600 to-hoeflon-700 text-white rounded-lg hover:from-hoeflon-700 hover:to-hoeflon-800 focus:outline-none focus:ring-2 focus:ring-hoeflon-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 font-semibold shadow-hoeflon transition-all duration-200"
          >
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
            <span>Verstuur</span>
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;