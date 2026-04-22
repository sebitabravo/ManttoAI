import { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Loader2, Bot } from 'lucide-react';
import client from '../../api/client';

export default function ChatBot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: '¡Hola! Soy tu Asistente de Mantenimiento. ¿En qué te puedo ayudar hoy?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await client.post('/chat', {
        mensaje: userMessage.content,
        historial: messages.map(m => ({ rol: m.role, contenido: m.content }))
      }, { timeout: 75000 }); // 75s: backend tarda máximo 60s en Ollama + buffer pequeño
      
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: response.data.respuesta
      }]);
    } catch (error) {
      console.error('Error al enviar mensaje:', error);
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: 'Lo siento, ocurrió un error al procesar tu solicitud. Por favor intenta de nuevo.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-6 right-6 z-[100] flex h-14 w-14 items-center justify-center rounded-full bg-primary-600 text-white shadow-lg transition-all hover:bg-primary-700 hover:scale-105 active:scale-95 ${isOpen ? 'scale-0 opacity-0' : 'scale-100 opacity-100'}`}
        aria-label="Abrir asistente de mantenimiento"
      >
        <MessageSquare size={24} />
      </button>

      <div
        className={`fixed bottom-6 right-6 z-[100] flex h-[500px] w-[350px] flex-col overflow-hidden rounded-2xl bg-white shadow-2xl transition-all sm:w-[400px] origin-bottom-right ${isOpen ? 'scale-100 opacity-100' : 'pointer-events-none scale-95 opacity-0'}`}
      >
        <div className="flex items-center justify-between bg-primary-600 px-4 py-3 text-white">
          <div className="flex items-center gap-2">
            <Bot size={20} />
            <h3 className="font-semibold">Asistente IA</h3>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="rounded-lg p-1 transition-colors hover:bg-primary-700"
            aria-label="Cerrar chat"
          >
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 bg-neutral-50 space-y-4">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`relative max-w-[85%] rounded-2xl px-4 py-2 text-sm shadow-sm ${msg.role === 'user' ? 'bg-primary-600 text-white rounded-br-none' : 'bg-white text-neutral-800 rounded-bl-none border border-neutral-100'}`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex w-full justify-start">
              <div className="flex max-w-[85%] items-center gap-2 rounded-2xl rounded-bl-none border border-neutral-100 bg-white px-4 py-3 shadow-sm">
                <Loader2 size={16} className="animate-spin text-primary-500" />
                <span className="text-xs text-neutral-500">Escribiendo...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="border-t border-neutral-100 bg-white p-3">
          <div className="flex items-center gap-2 rounded-xl border border-neutral-200 bg-neutral-50 p-1 pl-3 focus-within:border-primary-500 focus-within:bg-white focus-within:ring-1 focus-within:ring-primary-500 transition-all">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Pregunta sobre mantenimiento..."
              className="flex-1 bg-transparent py-2 text-sm outline-none placeholder:text-neutral-400"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-600 text-white transition-colors disabled:bg-neutral-300 disabled:text-neutral-500 hover:bg-primary-700"
            >
              <Send size={16} className={input.trim() && !isLoading ? 'ml-1' : ''} />
            </button>
          </div>
        </form>
      </div>
    </>
  );
}
