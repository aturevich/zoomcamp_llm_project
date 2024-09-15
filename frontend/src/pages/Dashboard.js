import React, { useState, useEffect } from 'react';
import { Container, Grid, Paper, Typography } from '@mui/material';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';  // Update this with your backend URL

const Dashboard = () => {
  const [data, setData] = useState({
    feedback: null,
    responseTime: null,
    queryTopics: null,
    usage: null,
    answerMetrics: null
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [feedback, responseTime, queryTopics, usage, answerMetrics] = await Promise.all([
          axios.get(`${API_BASE_URL}/api/dashboard/feedback`),
          axios.get(`${API_BASE_URL}/api/dashboard/response_time`),
          axios.get(`${API_BASE_URL}/api/dashboard/query_topics`),
          axios.get(`${API_BASE_URL}/api/dashboard/usage`),
          axios.get(`${API_BASE_URL}/api/dashboard/answer_metrics`),
        ]);

        setData({
          feedback: feedback.data,
          responseTime: responseTime.data,
          queryTopics: queryTopics.data,
          usage: usage.data,
          answerMetrics: answerMetrics.data
        });
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };

    fetchData();
  }, []);

  const renderFeedbackChart = () => {
    if (!data.feedback) return null;
    
    const chartData = [
      { name: 'Positive', value: data.feedback.positive_feedback, color: '#00C49F' },
      { name: 'Negative', value: data.feedback.negative_feedback, color: '#FF8042' }
    ];

    return (
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie 
            dataKey="value" 
            data={chartData} 
            fill="#8884d8" 
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    );
  };

  const renderUsageChart = () => {
    if (!data.usage) return null;

    const chartData = [
      { name: 'Total Queries', value: data.usage.total_queries },
      { name: 'Queries Last Week', value: data.usage.queries_last_week }
    ];

    return (
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="value" fill="#82ca9d" />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  const renderResponseTimeChart = () => {
    if (!data.responseTime) return null;

    const chartData = [
      { name: 'Min', value: data.responseTime.min_response_time },
      { name: 'Avg', value: data.responseTime.average_response_time },
      { name: 'Max', value: data.responseTime.max_response_time }
    ];

    return (
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="value" stroke="#8884d8" />
        </LineChart>
      </ResponsiveContainer>
    );
  };

  const renderQueryTopicsChart = () => {
    if (!data.queryTopics) return null;

    const chartData = Object.entries(data.queryTopics)
      .map(([key, value]) => ({ name: key, value: value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10);  // Top 10 topics

    return (
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="value" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  const renderTokensChart = () => {
    console.log("Answer Metrics Data:", data.answerMetrics);
    if (!data.answerMetrics || data.answerMetrics.average_tokens === 0) {
      return <Typography>No token data available</Typography>;
    }

    const chartData = [
      { name: 'Average Tokens', value: data.answerMetrics.average_tokens }
    ];

    return (
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="value" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 340 }}>
            <Typography variant="h6">User Feedback</Typography>
            {renderFeedbackChart()}
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 340 }}>
            <Typography variant="h6">System Usage</Typography>
            {renderUsageChart()}
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 340 }}>
            <Typography variant="h6">Response Time</Typography>
            {renderResponseTimeChart()}
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 340 }}>
            <Typography variant="h6">Query Topics</Typography>
            {renderQueryTopicsChart()}
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 340 }}>
            <Typography variant="h6">Average Tokens per Answer</Typography>
            {renderTokensChart()}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
