import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, ChevronRight } from 'lucide-react';
import { submitClarification } from '../services/api';

const InteractiveClarificationForm = ({ 
  clarificationData, 
  originalQuestion, 
  sessionId, 
  onFormSubmit,
  confidenceScore = 0 
}) => {
  const [formData, setFormData] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const clarificationForm = clarificationData?.clarification_form;
  
  if (!clarificationForm) {
    return null;
  }

  // Handle checkbox group changes
  const handleCheckboxGroupChange = (fieldName, value, checked) => {
    setFormData(prev => {
      const currentValues = prev[fieldName] || [];
      if (checked) {
        return {
          ...prev,
          [fieldName]: [...currentValues, value]
        };
      } else {
        return {
          ...prev,
          [fieldName]: currentValues.filter(v => v !== value)
        };
      }
    });
  };

  // Handle radio group changes
  const handleRadioGroupChange = (fieldName, value) => {
    setFormData(prev => ({
      ...prev,
      [fieldName]: value
    }));
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const clarificationRequest = {
        original_question: originalQuestion,
        form_responses: formData,
        session_id: sessionId
      };

      const response = await submitClarification(clarificationRequest);
      
      // Call the parent callback with the response
      onFormSubmit(response);
      
    } catch (error) {
      console.error('Error submitting clarification:', error);
      // Could show an error message here
    } finally {
      setIsSubmitting(false);
    }
  };

  // Get confidence color and text
  const getConfidenceDisplay = (score) => {
    if (score >= 0.9) {
      return { color: 'text-green-600', bg: 'bg-green-50', text: 'Hoge betrouwbaarheid', icon: '🟢' };
    } else if (score >= 0.75) {
      return { color: 'text-yellow-600', bg: 'bg-yellow-50', text: 'Gemiddelde betrouwbaarheid', icon: '🟡' };
    } else if (score >= 0.6) {
      return { color: 'text-orange-600', bg: 'bg-orange-50', text: 'Lage betrouwbaarheid', icon: '🟠' };
    } else {
      return { color: 'text-red-600', bg: 'bg-red-50', text: 'Onbetrouwbaar', icon: '🔴' };
    }
  };

  const confidenceDisplay = getConfidenceDisplay(confidenceScore);

  return (
    <div className="bg-white rounded-lg border border-hoeflon-200 p-6 space-y-6">
      {/* Confidence Score Header */}
      <div className={`${confidenceDisplay.bg} ${confidenceDisplay.color} p-4 rounded-lg border-l-4 border-l-current`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="h-5 w-5" />
            <div>
              <h3 className="font-bold text-sm">Betrouwbaarheid van huidige resultaat</h3>
              <p className="text-xs mt-1">
                {confidenceDisplay.icon} {confidenceDisplay.text} ({Math.round(confidenceScore * 100)}%)
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Form Title */}
      <div className="text-center">
        <h3 className="text-lg font-bold text-hoeflon-900 mb-2">
          {clarificationForm.title}
        </h3>
        <p className="text-sm text-hoeflon-600">
          Verduidelijk uw vraag om een betrouwbaarder antwoord te krijgen
        </p>
      </div>

      {/* Form Sections */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {clarificationForm.sections.map((section, sectionIndex) => (
          <div key={sectionIndex} className="space-y-3">
            <h4 className="font-semibold text-hoeflon-800 text-sm flex items-center space-x-2">
              <span>{section.title}</span>
              {section.required && <span className="text-red-500">*</span>}
            </h4>

            {section.type === 'checkbox_group' && (
              <div className="space-y-2">
                {section.options.map((option, optionIndex) => (
                  <label
                    key={optionIndex}
                    className="flex items-center space-x-3 p-3 bg-hoeflon-25 rounded-lg border border-hoeflon-100 hover:bg-hoeflon-50 cursor-pointer transition-colors"
                  >
                    <input
                      type="checkbox"
                      checked={formData[section.field_name]?.includes(option.value) || option.checked}
                      onChange={(e) => handleCheckboxGroupChange(section.field_name, option.value, e.target.checked)}
                      className="h-4 w-4 text-hoeflon-600 focus:ring-hoeflon-500 border-hoeflon-300 rounded"
                    />
                    <span className="text-sm text-hoeflon-700 flex-1">{option.label}</span>
                  </label>
                ))}
              </div>
            )}

            {section.type === 'radio_group' && (
              <div className="space-y-2">
                {section.options.map((option, optionIndex) => (
                  <label
                    key={optionIndex}
                    className="flex items-center space-x-3 p-3 bg-hoeflon-25 rounded-lg border border-hoeflon-100 hover:bg-hoeflon-50 cursor-pointer transition-colors"
                  >
                    <input
                      type="radio"
                      name={section.field_name}
                      value={option.value}
                      checked={formData[section.field_name] === option.value || option.checked}
                      onChange={(e) => handleRadioGroupChange(section.field_name, e.target.value)}
                      className="h-4 w-4 text-hoeflon-600 focus:ring-hoeflon-500 border-hoeflon-300"
                    />
                    <span className="text-sm text-hoeflon-700 flex-1">{option.label}</span>
                  </label>
                ))}
              </div>
            )}
          </div>
        ))}

        {/* Submit Button */}
        <div className="pt-4 border-t border-hoeflon-200">
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full btn-hoeflon-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {isSubmitting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Verwerken...</span>
              </>
            ) : (
              <>
                <span>{clarificationForm.submit_button?.text || '🔍 Stel verfijnde vraag'}</span>
                <ChevronRight className="h-4 w-4" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default InteractiveClarificationForm;