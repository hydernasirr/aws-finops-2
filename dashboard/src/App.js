import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = 'http://localhost:8000/api';

function App() {
  const [configured, setConfigured] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Data states
  const [summary, setSummary] = useState(null);
  const [servicesCosts, setServicesCosts] = useState(null);
  const [dailyCosts, setDailyCosts] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  
  // Configuration states
  const [awsKey, setAwsKey] = useState('');
  const [awsSecret, setAwsSecret] = useState('');
  const [region, setRegion] = useState('us-east-1');

  // Check if configured on load
  useEffect(() => {
    checkHealth();
  }, []);

  // Load data when configured
  useEffect(() => {
    if (configured) {
      loadAllData();
    }
  }, [configured]);

  const checkHealth = async () => {
    try {
      const response = await fetch(`${API_URL}/health`);
      const data = await response.json();
      setConfigured(data.configured);
    } catch (err) {
      console.error('Health check failed:', err);
    }
  };

  const handleConfigure = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/configure`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          aws_access_key: awsKey || null,
          aws_secret_key: awsSecret || null,
          region: region
        })
      });

      if (!response.ok) throw new Error('Configuration failed');
      
      setConfigured(true);
      setAwsKey('');
      setAwsSecret('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadAllData = async () => {
    setLoading(true);
    try {
      // Load summary
      const summaryRes = await fetch(`${API_URL}/costs/summary`);
      const summaryData = await summaryRes.json();
      setSummary(summaryData);

      // Load service costs
      const servicesRes = await fetch(`${API_URL}/costs/by-service`);
      const servicesData = await servicesRes.json();
      setServicesCosts(servicesData);

      // Load daily costs
      const dailyRes = await fetch(`${API_URL}/costs/daily`);
      const dailyData = await dailyRes.json();
      setDailyCosts(dailyData);

      // Load forecast
      const forecastRes = await fetch(`${API_URL}/forecast`);
      const forecastData = await forecastRes.json();
      setForecast(forecastData);

      // Load recommendations
      const recsRes = await fetch(`${API_URL}/optimization/recommendations`);
      const recsData = await recsRes.json();
      setRecommendations(recsData);

    } catch (err) {
      setError('Failed to load data: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!configured) {
    return (
      <div className="App">
        <div className="config-container">
          <h1>AWS FinOps Agent</h1>
          <h2>Configure AWS Credentials</h2>
          <form onSubmit={handleConfigure}>
            <div className="form-group">
              <label>AWS Access Key ID (optional if using IAM role)</label>
              <input
                type="text"
                value={awsKey}
                onChange={(e) => setAwsKey(e.target.value)}
                placeholder="Leave blank to use default credentials"
              />
            </div>
            <div className="form-group">
              <label>AWS Secret Access Key</label>
              <input
                type="password"
                value={awsSecret}
                onChange={(e) => setAwsSecret(e.target.value)}
                placeholder="Leave blank to use default credentials"
              />
            </div>
            <div className="form-group">
              <label>AWS Region</label>
              <select value={region} onChange={(e) => setRegion(e.target.value)}>
                <option value="us-east-1">us-east-1</option>
                <option value="us-west-2">us-west-2</option>
                <option value="eu-west-1">eu-west-1</option>
                <option value="ap-southeast-1">ap-southeast-1</option>
              </select>
            </div>
            {error && <div className="error">{error}</div>}
            <button type="submit" disabled={loading}>
              {loading ? 'Configuring...' : 'Connect to AWS'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header>
        <h1>AWS FinOps Dashboard</h1>
        <button onClick={loadAllData} disabled={loading}>
          {loading ? 'Refreshing...' : '↻ Refresh Data'}
        </button>
      </header>

      {error && <div className="error-banner">{error}</div>}

      {loading && !summary ? (
        <div className="loading">Loading AWS cost data...</div>
      ) : (
        <>
          {/* Summary Cards */}
          {summary && (
            <div className="summary-grid">
              <div className="card">
                <h3>Current Month</h3>
                <div className="value">${summary.current_month.total_cost.toFixed(2)}</div>
                <div className="label">Total Spend</div>
              </div>
              <div className="card">
                <h3>Daily Average</h3>
                <div className="value">${summary.current_month.avg_daily_cost.toFixed(2)}</div>
                <div className="label">Per Day</div>
              </div>
              <div className="card">
                <h3>Next 30 Days</h3>
                <div className="value">${forecast?.total_forecast?.toFixed(2) || 'N/A'}</div>
                <div className="label">Forecasted</div>
              </div>
              <div className="card savings">
                <h3>Potential Savings</h3>
                <div className="value">${summary.optimization.potential_monthly_savings.toFixed(2)}</div>
                <div className="label">Per Month</div>
              </div>
            </div>
          )}

          {/* Cost by Service */}
          {servicesCosts && (
            <div className="card section">
              <h2>Cost Breakdown by Service</h2>
              <div className="service-list">
                {Object.entries(servicesCosts.services).slice(0, 10).map(([service, cost]) => (
                  <div key={service} className="service-item">
                    <div className="service-name">{service}</div>
                    <div className="service-cost">${cost.toFixed(2)}</div>
                    <div className="service-bar">
                      <div 
                        className="service-bar-fill"
                        style={{ width: `${(cost / servicesCosts.total) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
              <div className="service-total">
                <strong>Total:</strong> ${servicesCosts.total.toFixed(2)}
              </div>
            </div>
          )}

          {/* Daily Trend */}
          {dailyCosts && (
            <div className="card section">
              <h2>Last 7 Days Spending</h2>
              <div className="chart">
                {dailyCosts.daily_costs.slice(-7).map((day) => (
                  <div key={day.date} className="chart-bar">
                    <div 
                      className="bar"
                      style={{ 
                        height: `${(day.cost / Math.max(...dailyCosts.daily_costs.map(d => d.cost))) * 100}%` 
                      }}
                      title={`$${day.cost}`}
                    />
                    <div className="bar-label">{new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Optimization Recommendations */}
          {recommendations && recommendations.recommendations.length > 0 && (
            <div className="card section">
              <h2>Cost Optimization Recommendations</h2>
              <div className="recommendations">
                {recommendations.recommendations.map((rec, idx) => (
                  <div key={idx} className={`recommendation ${rec.severity.toLowerCase()}`}>
                    <div className="rec-header">
                      <span className="rec-severity">{rec.severity}</span>
                      <span className="rec-category">{rec.category}</span>
                    </div>
                    <h3>{rec.title}</h3>
                    <p>{rec.description}</p>
                    <div className="rec-action">
                      <strong>Action:</strong> {rec.action}
                    </div>
                    <div className="rec-savings">
                      <strong>Potential Savings:</strong> {rec.potential_savings}
                    </div>
                    {rec.resources && rec.resources.length > 0 && (
                      <div className="rec-resources">
                        <strong>Resources:</strong>
                        <ul>
                          {rec.resources.slice(0, 5).map((res, i) => (
                            <li key={i}>{res}</li>
                          ))}
                          {rec.resources.length > 5 && (
                            <li>...and {rec.resources.length - 5} more</li>
                          )}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {recommendations && recommendations.recommendations.length === 0 && (
            <div className="card section success">
              <h2>✓ All Clear!</h2>
              <p>No immediate cost optimization opportunities found. Your AWS resources are well-managed.</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;
