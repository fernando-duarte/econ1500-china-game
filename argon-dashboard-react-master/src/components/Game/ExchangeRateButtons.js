import React from 'react';
import PropTypes from 'prop-types';
import { Button, ButtonGroup } from 'reactstrap';

/**
 * ExchangeRateButtons component
 * Renders a group of buttons for exchange rate selection.
 * Only one can be selected at a time.
 *
 * @param {string} selected - The currently selected option
 * @param {function} onSelect - Callback when an option is selected
 * @param {string[]} [options] - The button labels (default: Undervalue, Market-based, Overvalued)
 */
const DEFAULT_OPTIONS = ['Undervalue', 'Market-based', 'Overvalued'];

const ExchangeRateButtons = ({ selected, onSelect, options = DEFAULT_OPTIONS }) => {
  return (
    <ButtonGroup role="group" aria-label="Exchange Rate Selection" className="w-100">
      {options.map((option) => (
        <Button
          key={option}
          color={selected === option ? 'primary' : 'secondary'}
          onClick={() => onSelect(option)}
          active={selected === option}
          aria-pressed={selected === option}
          aria-label={option}
          className="flex-fill"
        >
          {option}
        </Button>
      ))}
    </ButtonGroup>
  );
};

ExchangeRateButtons.propTypes = {
  selected: PropTypes.string.isRequired,
  onSelect: PropTypes.func.isRequired,
  options: PropTypes.arrayOf(PropTypes.string),
};

export default ExchangeRateButtons; 