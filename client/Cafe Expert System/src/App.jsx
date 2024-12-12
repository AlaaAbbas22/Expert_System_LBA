import React, { useState, useEffect } from "react";
import axios from "axios";
axios.defaults.withCredentials = true;

const App = () => {
  const [question, setQuestion] = useState(null);
  const [options, setOptions] = useState([]);
  const [answers, setAnswers] = useState([]);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);

  const backendURL = "http://localhost:4000"; // Update if hosted elsewhere

  useEffect(() => {
    // Initial request to start the process
    if (hasStarted) {
      startProcess();
    }
  }, [hasStarted]);

  const startProcess = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${backendURL}/`);
      if (response.data.ask) {
        setQuestion(response.data.ask);
        setOptions(response.data.options);
      } else if (response.data.result) {
        setResult(response.data.result);
      }
    } catch (error) {
      console.error("Error starting process:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const sendAnswers = async () => {
    if (answers.length === 0) {
      alert("Please select at least one option.");
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.post(`${backendURL}/ask`, {
        answers: answers,
      },{
        withCredentials:true
      });

      if (response.data.ask) {
        setQuestion(response.data.ask);
        setOptions(response.data.options);
        setAnswers([]); // Reset answers for the new question
      } else if (response.data.result) {
        setResult(response.data.result.X);
      }
    } catch (error) {
      console.error("Error sending answers:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOptionChange = (e) => {
    const selectedValue = e.target.value;
    setAnswers((prev) => {
      if (prev.includes(selectedValue)) {
        return prev.filter((item) => item !== selectedValue); // Deselect option
      } else {
        return [...prev, selectedValue]; // Select option
      }
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-6 px-4 sm:px-6 lg:px-8">
      <div className="max-w-lg w-full bg-white p-8 rounded-lg shadow-lg space-y-6">
        <h1 className="text-3xl font-semibold text-center text-indigo-600">Expert System</h1>
        
        {!hasStarted && (
          <div className="text-center">
            <button
              onClick={() => setHasStarted(true)}
              className="w-full py-2 px-4 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              Start Now
            </button>
          </div>
        )}

        {isLoading && (
          <div className="text-center text-gray-500">Loading...</div>
        )}

        {!isLoading && result && (
          <div className="text-center text-lg text-green-600">
            <h2 className="font-medium">Result:</h2>
            <p>{result}</p>
          </div>
        )}

        {!isLoading && question && !result && (
          <div>
            <h2 className="text-xl font-medium text-gray-700 mb-4">{question}</h2>
            <form className="space-y-4">
              {options.map((option, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    id={option}
                    value={option}
                    checked={answers.includes(option)}
                    onChange={handleOptionChange}
                    className="h-5 w-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                  />
                  <label htmlFor={option} className="text-gray-700">{option}</label>
                </div>
              ))}
            </form>
            <div className="text-center">
              <button
                onClick={sendAnswers}
                className="mt-6 w-full py-2 px-4 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                Submit
              </button>
            </div>
          </div>
        )}

        
      </div>
    </div>
  );
};

export default App;
