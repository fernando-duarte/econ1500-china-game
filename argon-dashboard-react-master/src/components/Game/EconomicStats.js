import React from 'react';
import PropTypes from 'prop-types';
import { Card, CardBody, Row, Col } from 'reactstrap';

/**
 * EconomicStats component
 * Displays economic statistics in a specified order and format.
 * Responsive and accessible.
 *
 * @param {object} stats - The stats object
 * @param {string} stats.groupName - Group name
 * @param {number} stats.year - Current year
 * @param {number} stats.gdp - GDP (in billions)
 * @param {number} stats.gdpGrowth - GDP growth last round (%)
 * @param {number} stats.consumption - Consumption (in billions)
 * @param {number} stats.netExports - Net exports (in billions)
 * @param {number} stats.capitalStock - Capital stock (in billions)
 * @param {object} stats.ranking - Ranking object { current, total }
 * @param {boolean} [stats.isHot] - If true, show 🔥 icon
 */
const EconomicStats = ({ stats }) => {
  const {
    groupName,
    year,
    gdp,
    gdpGrowth,
    consumption,
    netExports,
    capitalStock,
    ranking,
    isHot,
  } = stats;

  // Formatters
  const formatBn = (val) => `$${val.toLocaleString()} bn`;
  const formatGrowth = (val) => `${val > 0 ? '+' : ''}${val}%`;
  const formatNetExports = (val) => `${val >= 0 ? '+' : ''}$${val.toLocaleString()} bn`;
  const formatRanking = (r, hot) => `#${r.current} of ${r.total} groups${hot ? ' 🔥' : ''}`;

  return (
    <Card className="mb-3" aria-label="Economic Statistics">
      <CardBody>
        <Row className="align-items-center mb-2">
          <Col xs="12" md="8">
            <span className="font-weight-bold" aria-label="Group Name">{groupName}</span>
          </Col>
          <Col xs="12" md="4" className="text-md-right">
            <span aria-label="Current Year">Year: {year}</span>
          </Col>
        </Row>
        <Row className="mb-2">
          <Col xs="6" md="3">
            <div aria-label="GDP"><strong>GDP:</strong> {formatBn(gdp)}</div>
          </Col>
          <Col xs="6" md="3">
            <div aria-label="GDP Growth"><strong>GDP Growth:</strong> {formatGrowth(gdpGrowth)}</div>
          </Col>
          <Col xs="6" md="3">
            <div aria-label="Consumption"><strong>Consumption:</strong> {formatBn(consumption)}</div>
          </Col>
          <Col xs="6" md="3">
            <div aria-label="Net Exports"><strong>Net Exports:</strong> {formatNetExports(netExports)}</div>
          </Col>
        </Row>
        <Row className="mb-2">
          <Col xs="6" md="3">
            <div aria-label="Capital Stock"><strong>Capital Stock:</strong> {formatBn(capitalStock)}</div>
          </Col>
          <Col xs="6" md="3">
            <div aria-label="Ranking"><strong>Ranking:</strong> {formatRanking(ranking, isHot)}</div>
          </Col>
        </Row>
      </CardBody>
    </Card>
  );
};

EconomicStats.propTypes = {
  stats: PropTypes.shape({
    groupName: PropTypes.string.isRequired,
    year: PropTypes.number.isRequired,
    gdp: PropTypes.number.isRequired,
    gdpGrowth: PropTypes.number.isRequired,
    consumption: PropTypes.number.isRequired,
    netExports: PropTypes.number.isRequired,
    capitalStock: PropTypes.number.isRequired,
    ranking: PropTypes.shape({
      current: PropTypes.number.isRequired,
      total: PropTypes.number.isRequired,
    }).isRequired,
    isHot: PropTypes.bool,
  }).isRequired,
};

export default EconomicStats; 