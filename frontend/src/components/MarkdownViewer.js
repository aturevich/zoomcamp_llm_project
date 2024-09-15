import React, { useState, useEffect, Suspense } from 'react';
import ReactMarkdown from 'react-markdown';
import { Paper, Typography, CircularProgress, Alert } from '@mui/material';
import axios from 'axios';


function MarkdownViewer({ filePath }) {
  const [content, setContent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMarkdown = async () => {
      try {
        console.log('Original file path:', filePath);
        const cleanedPath = filePath.replace(/^\.?\/?(data\/dnd_srd\/)?/, '');
        console.log('Cleaned file path:', cleanedPath);
        const response = await axios.get(`http://localhost:8000/render-markdown/${encodeURIComponent(cleanedPath)}`, {
          responseType: 'text'
        });
        console.log('Markdown content received:', response.data.substring(0, 100) + '...');
        setContent(response.data);
        setError(null);
      } catch (error) {
        console.error('Error fetching markdown:', error);
        setError(`Error loading markdown content: ${error.response?.status} ${error.response?.statusText}`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMarkdown();
  }, [filePath]);

  if (isLoading) {
    return <CircularProgress />;
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 2, maxHeight: '80vh', overflow: 'auto' }}>
      <Typography variant="h6" gutterBottom>
        {filePath.split('/').pop()}
      </Typography>
      <Suspense fallback={<CircularProgress />}>
        <ReactMarkdown>{content}</ReactMarkdown>
      </Suspense>
    </Paper>
  );
}

export default MarkdownViewer;
