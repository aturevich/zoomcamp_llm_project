// frontend/src/pages/Home.js
import React from 'react';
import { Container, Typography } from '@mui/material';

function Home() {
  return (
    <Container>
      <Typography variant="h2">Welcome to D&D 5e SRD Assistant</Typography>
      <Typography>
        This is a demo application for searching and browsing the D&D 5e SRD content.
      </Typography>
    </Container>
  );
}

export default Home;
