import React, { useState } from 'react';
import { Container, Row, Col, Button, Card, CardBody } from 'reactstrap';
import BreakingNewsBanner from '../components/Game/BreakingNewsBanner';
import EconomicStats from '../components/Game/EconomicStats';
import CountdownTimer from '../components/Game/CountdownTimer';
import SavingsRateSlider from '../components/Game/SavingsRateSlider';
import ExchangeRateButtons from '../components/Game/ExchangeRateButtons';
import GDPGrowthChart from '../components/Game/GDPGrowthChart';
import TradeBalanceChart from '../components/Game/TradeBalanceChart';
import ConsumptionSavingsChart from '../components/Game/ConsumptionSavingsChart';
import {
  GameStateProvider,
  TimerProvider,
  BreakingNewsProvider,
  DecisionProvider,
} from '../providers';
import { useGameState } from '../hooks/useGameState';
import { useTimer } from '../hooks/useTimer';
import { useBreakingNews } from '../hooks/useBreakingNews';
import { useDecision } from '../hooks/useDecision';

/**
 * DashboardContent: Uses hooks to access context-driven data and renders the dashboard UI.
 */
const DashboardContent = () => {
  // Game state and stats
  const { teamStats } = useGameState();
  // Timer
  const { timeLeft } = useTimer();
  // Breaking news
  const { news, dismiss } = useBreakingNews();
  // Decision submission
  const { submitDecision, submitting, confirmation, reset } = useDecision();

  // Local state for controls
  const [savingsRate, setSavingsRate] = useState(10);
  const [exchangeRate, setExchangeRate] = useState('Market-based');
  const [showConfirm, setShowConfirm] = useState(false);

  // Placeholder chart data (replace with real data from context when available)
  const chartLabels = ['1980', '1985', '1990', '1995', '2000', '2005'];
  const gdpGrowthData = [6, 7, 8, 8, 9, 8];
  const tradeBalanceData = [100, 150, 200, 180, 220, 200];
  const consumption = 1200;
  const savings = 800;

  // Timer: convert timeLeft (seconds) to endTime for CountdownTimer
  const endTime = Date.now() + (timeLeft || 0) * 1000;

  const handleSubmit = () => setShowConfirm(true);
  const handleConfirm = () => {
    setShowConfirm(false);
    submitDecision({ savingsRate, exchangeRate });
  };
  const handleCancel = () => setShowConfirm(false);

  return (
    <Container fluid className="py-4">
      {news && news.message && (
        <BreakingNewsBanner
          message={news.message}
          onDismiss={dismiss}
        />
      )}
      <Row className="mb-3">
        <Col md="8" xs="12">
          <EconomicStats stats={teamStats || {
            groupName: 'The Prosperous Pandas',
            year: 2005,
            gdp: 2500,
            gdpGrowth: 8,
            consumption: 1200,
            netExports: 200,
            capitalStock: 1800,
            ranking: { current: 2, total: 10 },
            isHot: true,
          }} />
        </Col>
        <Col md="4" xs="12" className="d-flex align-items-center justify-content-center">
          <CountdownTimer endTime={endTime} />
        </Col>
      </Row>
      <Row className="mb-4">
        <Col md="6" xs="12" className="mb-3 mb-md-0">
          <Card>
            <CardBody>
              <SavingsRateSlider value={savingsRate} onChange={setSavingsRate} />
            </CardBody>
          </Card>
        </Col>
        <Col md="6" xs="12">
          <Card>
            <CardBody>
              <ExchangeRateButtons selected={exchangeRate} onSelect={setExchangeRate} />
            </CardBody>
          </Card>
        </Col>
      </Row>
      <Row className="mb-4">
        <Col xs="12" className="text-center">
          <Button color="primary" size="lg" onClick={handleSubmit} aria-label="Submit Decisions" disabled={submitting}>
            {submitting ? 'Submitting...' : 'Submit Decisions'}
          </Button>
        </Col>
      </Row>
      {showConfirm && (
        <Row className="mb-4">
          <Col xs="12" className="text-center">
            <Card className="p-3">
              <div className="mb-2">Are you sure you want to submit your decisions?</div>
              <Button color="success" className="mr-2" onClick={handleConfirm} aria-label="Confirm Submit">Confirm</Button>
              <Button color="secondary" onClick={handleCancel} aria-label="Cancel Submit">Cancel</Button>
            </Card>
          </Col>
        </Row>
      )}
      {confirmation && (
        <Row className="mb-4">
          <Col xs="12" className="text-center">
            <Card className="p-3">
              <div className="mb-2">{confirmation.message}</div>
              <Button color="primary" onClick={reset}>OK</Button>
            </Card>
          </Col>
        </Row>
      )}
      <Row>
        <Col md="6" xs="12" className="mb-4">
          <GDPGrowthChart data={gdpGrowthData} labels={chartLabels} />
        </Col>
        <Col md="6" xs="12" className="mb-4">
          <TradeBalanceChart data={tradeBalanceData} labels={chartLabels} />
        </Col>
        <Col md="6" xs="12">
          <ConsumptionSavingsChart consumption={consumption} savings={savings} />
        </Col>
      </Row>
    </Container>
  );
};

/**
 * GameDashboard wraps DashboardContent in all providers.
 */
const GameDashboard = () => (
  <GameStateProvider>
    <TimerProvider>
      <BreakingNewsProvider>
        <DecisionProvider>
          <DashboardContent />
        </DecisionProvider>
      </BreakingNewsProvider>
    </TimerProvider>
  </GameStateProvider>
);

export default GameDashboard; 