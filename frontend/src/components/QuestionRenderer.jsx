import React, { useState } from 'react';
import { Send } from 'lucide-react';

const QuestionRenderer = ({ question, onAnswer }) => {
  const [value, setValue] = useState('');
  const [multiValue, setMultiValue] = useState([]);
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (!value && question.required && question.input_type !== 'multi_select') {
      setError('Required field');
      return;
    }
    onAnswer(value);
    setValue('');
  };

  const handleMultiSubmit = () => {
    if (multiValue.length === 0 && question.required) {
      setError('Select at least one');
      return;
    }
    onAnswer(multiValue.join(', '));
    setMultiValue([]);
  };

  return (
    <div className="question-renderer">
      {(question.input_type === 'text' || question.input_type === 'number') && (
        <form onSubmit={handleSubmit} className="chat-input-container">
          <input
            type={question.input_type}
            value={value}
            onChange={(e) => {
              setValue(e.target.value);
              setError('');
            }}
            placeholder="Type your medical symptom or response..."
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleSubmit();
            }}
          />
          <button type="submit" className="chat-send-btn">
            <Send size={18} />
          </button>
        </form>
      )}

      {question.input_type === 'single_select' && (
        <div className="question-options-grid">
          {question.options?.map(option => (
            <button
              key={option}
              onClick={() => onAnswer(option)}
              className="action-btn"
            >
              {option}
            </button>
          ))}
        </div>
      )}

      {question.input_type === 'multi_select' && (
        <div className="multi-select-view">
          <div className="question-options-grid">
            {question.options?.map(option => (
              <button
                key={option}
                onClick={() => {
                  setMultiValue(prev => 
                    prev.includes(option) ? prev.filter(o => o !== option) : [...prev, option]
                  );
                  setError('');
                }}
                className={`action-btn ${multiValue.includes(option) ? 'active' : ''}`}
                style={multiValue.includes(option) ? {borderColor: 'var(--accent-purple)', backgroundColor: 'rgba(157, 122, 255, 0.1)'} : {}}
              >
                {option}
              </button>
            ))}
          </div>
          <button onClick={handleMultiSubmit} className="chat-send-btn mt-4 w-full" style={{borderRadius: 'var(--radius-md)'}}>
            Confirm Selected Symptoms
          </button>
        </div>
      )}

      {error && <p className="text-secondary mt-2" style={{color: 'var(--error)', fontSize: '0.8125rem', paddingLeft: '1rem'}}>{error}</p>}
    </div>
  );
};

export default QuestionRenderer;
