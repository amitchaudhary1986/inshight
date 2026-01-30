'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useWhisper } from '../hooks/useWhisper';

export const InterviewRecorder: React.FC = () => {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const { transcribe, isTranscribing, transcript } = useWhisper();
  const [tabFocusLost, setTabFocusLost] = useState(0);

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'hidden') {
        setTabFocusLost((prev) => prev + 1);
        console.warn('Tab focus lost!');
      }
    };

    const handleWindowBlur = () => {
      setTabFocusLost((prev) => prev + 1);
      console.warn('Window focus lost!');
    };

    const handlePaste = (e: ClipboardEvent) => {
      e.preventDefault();
      console.warn('Paste detected!');
      alert('Pasting is not allowed during the interview.');
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleWindowBlur);
    document.addEventListener('paste', handlePaste);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleWindowBlur);
      document.removeEventListener('paste', handlePaste);
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const audioContext = new (window.AudioContext || (window as (typeof window & { webkitAudioContext: typeof AudioContext })).webkitAudioContext)({ sampleRate: 16000 });
        const arrayBuffer = await audioBlob.arrayBuffer();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

        // Convert to Float32Array
        const float32Array = audioBuffer.getChannelData(0);
        await transcribe(float32Array);

        // Stop all tracks to release the microphone
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Error accessing microphone:', err);
      alert('Microphone access is required for the interview.');
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
  };

  return (
    <div className="p-6 border rounded-lg shadow-lg bg-white max-w-2xl mx-auto my-8">
      <h2 className="text-2xl font-bold mb-6 text-gray-800 border-bottom pb-2">AI Interview Session</h2>

      <div className="bg-blue-50 p-4 rounded-md mb-6">
        <p className="text-blue-800">
          <strong>Instructions:</strong> Please click &quot;Start Recording&quot;, answer the question verbally, and then click &quot;Stop Recording&quot;.
          Your answer will be transcribed and evaluated automatically.
        </p>
      </div>

      <div className="flex items-center justify-center gap-4 mb-8">
        {!isRecording ? (
          <button
            onClick={startRecording}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white font-semibold rounded-full hover:bg-blue-700 transition-colors shadow-md"
          >
            <span className="w-3 h-3 bg-white rounded-full"></span>
            Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="flex items-center gap-2 px-6 py-3 bg-red-600 text-white font-semibold rounded-full animate-pulse hover:bg-red-700 transition-colors shadow-md"
          >
            <span className="w-3 h-3 bg-white rounded-full"></span>
            Stop Recording
          </button>
        )}
      </div>

      <div className="space-y-6">
        {isTranscribing && (
          <div className="flex items-center gap-2 text-gray-600 italic">
            <svg className="animate-spin h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Processing transcription via Whisper WASM...
          </div>
        )}

        {transcript && (
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <h3 className="font-semibold text-gray-700 mb-2">Transcribed Answer:</h3>
            <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">{transcript}</p>
          </div>
        )}

        {tabFocusLost > 0 && (
          <div className="p-3 bg-red-100 text-red-700 rounded-md flex items-center gap-2 text-sm border border-red-200">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span>Anti-Cheating Warning: {tabFocusLost} tab switch{tabFocusLost > 1 ? 'es' : ''} detected. This will be reported.</span>
          </div>
        )}
      </div>
    </div>
  );
};
