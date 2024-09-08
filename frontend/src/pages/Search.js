import React, { useState } from 'react';
import { Container, TextField, Button, List, ListItem, ListItemText, Typography } from '@mui/material';
import axios from 'axios';

function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/search?q=${query}`);
      setResults(response.data.results);
    } catch (error) {
      console.error('Error searching:', error);
      setResults([]);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Search D&D 5e SRD
      </Typography>
      <TextField
        fullWidth
        label="Search query"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        margin="normal"
      />
      <Button variant="contained" onClick={handleSearch} sx={{ mt: 2, mb: 4 }}>
        Search
      </Button>
      <List>
        {results.map((result, index) => (
          <ListItem key={index} divider>
            <ListItemText
              primary={result.title}
              secondary={result.content.substring(0, 200) + '...'}
            />
          </ListItem>
        ))}
      </List>
    </Container>
  );
}

export default Search;
