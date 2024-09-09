import React, { useState } from 'react';
import { Container, TextField, Button, List, ListItem, ListItemText, Paper, Typography } from '@mui/material';
import axios from 'axios';
import '../index.css';

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

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const LoadingAnimation = () => {
    const randomPhrase = loadingPhrases[Math.floor(Math.random() * loadingPhrases.length)];
    
    return (
      <div className="loading-animation">
        <div className="loading-phrase">{randomPhrase}</div>
        <div className="book">
          <div className="book-cover"></div>
          <div className="paper left"></div>
          <div className="paper right"></div>
          <div className="flipping-page"></div>
        </div>
      </div>
    );
  };

  const handleSend = async () => {
    if (input.trim() === '') return;

    const newMessage = { text: input, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/query', 
        { question: input },
        {
          headers: { 'Content-Type': 'application/json' }
        }
      );

      if (response.data && response.data.answer) {
        const botMessage = { 
          text: response.data.answer, 
          sender: 'bot',
          metrics: response.data.retrieval_metrics
        };
        setMessages((prevMessages) => [...prevMessages, botMessage]);
      } else {
        console.error('Unexpected response format:', response.data);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = { text: 'Sorry, there was an error processing your request.', sender: 'bot' };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = async (answer, rating) => {
    try {
      await axios.post('http://localhost:8000/feedback', {
        question: messages[messages.length - 2].text,
        answer: answer,
        rating: rating === 1 ? "Yes" : "No"
      });
      console.log('Feedback sent successfully');
    } catch (error) {
      console.error('Error sending feedback:', error);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ height: '70vh', display: 'flex', flexDirection: 'column' }}>
        <List sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
          {messages.map((message, index) => (
            <ListItem key={index} alignItems="flex-start" sx={{ flexDirection: 'column' }}>
              <ListItemText
                primary={message.sender === 'user' ? 'You' : 'D&D Assistant'}
                secondary={message.text}
                sx={{
                  backgroundColor: message.sender === 'user' ? '#e3f2fd' : '#f5f5f5',
                  borderRadius: '10px',
                  padding: '10px',
                  marginBottom: '10px',
                  width: '100%',
                }}
              />
              {message.sender === 'bot' && (
                <>
                  <div>
                    <button onClick={() => handleFeedback(message.text, 1)}>👍</button>
                    <button onClick={() => handleFeedback(message.text, 0)}>👎</button>
                  </div>
                  {message.metrics && (
                    <details style={{ marginTop: '10px', width: '100%' }}>
                      <summary>Show Metrics</summary>
                      <Typography component="pre" sx={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                        {JSON.stringify(message.metrics, null, 2)}
                      </Typography>
                    </details>
                  )}
                </>
              )}
            </ListItem>
          ))}
          {isLoading && <LoadingAnimation />}
        </List>
        <div style={{ display: 'flex', padding: '20px' }}>
          <TextField
            fullWidth
            variant="outlined"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about D&D 5e..."
          />
          <Button variant="contained" onClick={handleSend} sx={{ ml: 1 }}>
            Send
          </Button>
        </div>
      </Paper>
    </Container>
  );
}

export default Chat;
