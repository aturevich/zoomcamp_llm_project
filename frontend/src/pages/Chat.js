import React, { useState, useRef, useEffect } from 'react';
import { Container, TextField, Button, List, ListItem, Paper, Typography, IconButton } from '@mui/material';
import axios from 'axios';
import '../index.css';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import MarkdownViewer from '../components/MarkdownViewer';

const loadingPhrases = [
  "Rolling for initiative...",
  "Summoning the Dungeon Master...",
  "Consulting the ancient tomes...",
  "Gathering your party...",
  "Sharpening vorpal swords...",
  "Feeding the mimics...",
  "Polishing dragon scales...",
  "Negotiating with goblins...",
  "Deciphering arcane scrolls...",
  "Crafting legendary items...",
  "Appeasing the RNG gods...",
  "Recruiting NPCs...",
  "Mapping unexplored territories...",
  "Preparing fireball spells...",
  "Stocking healing potions...",
];

function LoadingAnimation() {
  const [phrase, setPhrase] = useState(loadingPhrases[Math.floor(Math.random() * loadingPhrases.length)]);

  useEffect(() => {
    const interval = setInterval(() => {
      setPhrase(loadingPhrases[Math.floor(Math.random() * loadingPhrases.length)]);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="loading-animation">
      <div className="loading-phrase">{phrase}</div>
      <div className="book">
        <div className="book-cover"></div>
        <div className="paper left"></div>
        <div className="paper right"></div>
        <div className="flipping-page"></div>
      </div>
    </div>
  );
}

function Chat() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const [openMarkdown, setOpenMarkdown] = useState(false);
  const [selectedFile, setSelectedFile] = useState('');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    console.log('Current messages state:', messages);
  }, [messages]);

  useEffect(() => {
    console.log('Chat component re-rendered');
  });

  useEffect(() => {
    console.log('Messages updated:', messages);
  }, [messages]);

  const handleSend = async () => {
    if (input.trim() === '') return;

    const userMessage = { text: input, sender: 'user' };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/query', { question: input });
      console.log('Full API response:', response.data);
      const botMessage = {
        text: response.data.answer,
        sender: 'bot',
        id: response.data.interaction_id,
        fileReferences: response.data.file_references || [],
        metrics: response.data.retrieval_metrics,
        showMetrics: false
      };
      console.log('Bot message before state update:', botMessage);
      setMessages(prevMessages => {
        const newMessages = [...prevMessages, botMessage];
        console.log('New messages state:', newMessages);
        return newMessages;
      });
    } catch (error) {
      console.error('Error sending message:', error.response ? error.response.data : error);
      const errorMessage = { text: 'An error occurred while processing your request.', sender: 'bot' };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = async (messageId, feedback) => {
    try {
      await axios.post('http://localhost:8000/feedback', {
        interaction_id: messageId,
        rating: feedback === 'positive' ? 1 : -1,
        comment: null
      });
      setMessages(prevMessages =>
        prevMessages.map(msg =>
          msg.id === messageId ? { ...msg, feedback } : msg
        )
      );
    } catch (error) {
      console.error('Error sending feedback:', error);
    }
  };

  const toggleMetrics = (messageId) => {
    setMessages(prevMessages =>
      prevMessages.map(msg =>
        msg.id === messageId ? { ...msg, showMetrics: !msg.showMetrics } : msg
      )
    );
  };

  useEffect(() => {
    const lastMessage = messages[messages.length - 1];
    if (lastMessage && lastMessage.sender === 'bot') {
      console.log('Last bot message file references:', lastMessage.fileReferences);
    }
  }, [messages]);

  const handleOpenMarkdown = (file) => {
    console.log('Opening markdown file:', file);
    setSelectedFile(file);
    setOpenMarkdown(true);
  };

  const handleCloseMarkdown = () => {
    setOpenMarkdown(false);
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
      <Paper elevation={3} sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <List sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
          {messages.map((message, index) => (
            <ListItem key={index} alignItems="flex-start" sx={{ flexDirection: 'column', alignItems: message.sender === 'user' ? 'flex-end' : 'flex-start' }}>
              <Paper
                elevation={1}
                sx={{
                  backgroundColor: message.sender === 'user' ? '#e3f2fd' : '#f5f5f5',
                  borderRadius: '10px',
                  padding: '10px',
                  marginBottom: '5px',
                  maxWidth: '70%',
                }}
              >
                <Typography variant="body1">{message.text}</Typography>
              </Paper>
              {message.sender === 'bot' && (
                <div style={{ display: 'flex', alignItems: 'center', background: 'transparent' }}>
                  <IconButton size="small" onClick={() => handleFeedback(message.id, 'positive')}>
                    👍
                  </IconButton>
                  <IconButton size="small" onClick={() => handleFeedback(message.id, 'negative')}>
                    👎
                  </IconButton>
                  {(message.metrics || (Array.isArray(message.fileReferences) && message.fileReferences.length > 0)) && (
                    <IconButton size="small" onClick={() => toggleMetrics(message.id)}>
                      {message.showMetrics ? '🔼' : '🔽'}
                    </IconButton>
                  )}
                </div>
              )}
              {message.sender === 'bot' && message.showMetrics && (
                <Paper elevation={0} sx={{ mt: 1, p: 1, backgroundColor: 'rgba(245, 245, 245, 0.7)', width: '100%' }}>
                  {message.metrics && (
                    <>
                      <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>Metrics:</Typography>
                      <Typography component="pre" sx={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontSize: '0.8rem' }}>
                        {JSON.stringify(message.metrics, null, 2)}
                      </Typography>
                    </>
                  )}
                  {Array.isArray(message.fileReferences) && message.fileReferences.length > 0 && (
                    <>
                      <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1, mt: 2 }}>Source References:</Typography>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        {message.fileReferences.map((file, fileIndex) => (
                          <Button
                            key={fileIndex}
                            variant="outlined"
                            size="small"
                            sx={{
                              borderColor: '#5f4b32',
                              color: '#5f4b32',
                              '&:hover': {
                                backgroundColor: 'rgba(95, 75, 50, 0.1)',
                                borderColor: '#5f4b32',
                              },
                            }}
                            onClick={() => handleOpenMarkdown(file)}
                          >
                            {file.split('/').pop()}
                          </Button>
                        ))}
                      </div>
                    </>
                  )}
                </Paper>
              )}
            </ListItem>
          ))}
          {isLoading && <LoadingAnimation />}
        </List>
        <div style={{ padding: '20px', borderTop: '1px solid #e0e0e0', display: 'flex', alignItems: 'center' }}>
          <TextField
            fullWidth
            variant="outlined"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about D&D 5e..."
          />
          <Button variant="contained" onClick={handleSend} sx={{ ml: 2, height: '56px' }}>
            Send
          </Button>
        </div>
      </Paper>
      <Dialog
        open={openMarkdown}
        onClose={handleCloseMarkdown}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>{selectedFile.split('/').pop()}</DialogTitle>
        <DialogContent>
          <MarkdownViewer filePath={selectedFile} />
        </DialogContent>
      </Dialog>
    </Container>
  );
}

export default Chat;
