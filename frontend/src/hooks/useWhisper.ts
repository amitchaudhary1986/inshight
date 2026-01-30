import { useState, useCallback, useRef } from 'react';

export function useWhisper() {
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [transcript, setTranscript] = useState('');
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const pipelineRef = useRef<any>(null);

  const initPipeline = useCallback(async () => {
    if (pipelineRef.current) return pipelineRef.current;

    const { pipeline, env } = await import('@xenova/transformers');

    // Configure environment
    env.allowLocalModels = false;
    env.useBrowserCache = true;

    // Load model - tiny.en is fast and lightweight for WASM
    pipelineRef.current = await pipeline('automatic-speech-recognition', 'openai/whisper-tiny.en');
    return pipelineRef.current;
  }, []);

  const transcribe = useCallback(async (audioData: Float32Array) => {
    setIsTranscribing(true);
    try {
      const transcriber = await initPipeline();
      const output = await transcriber(audioData, {
        chunk_length_s: 30,
        stride_length_s: 5,
        task: 'transcribe',
        language: 'english',
      });
      setTranscript(output.text);
      return output.text;
    } catch (error) {
      console.error('Transcription error:', error);
    } finally {
      setIsTranscribing(false);
    }
  }, [initPipeline]);

  return { transcribe, isTranscribing, transcript };
}
