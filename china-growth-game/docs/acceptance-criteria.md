# Acceptance Criteria for China Growth Game

This document outlines testable requirements for key game features.

## Group Naming System

### Team Name Generator

| ID | Requirement | Acceptance Criteria | Testing Method |
|----|-------------|---------------------|----------------|
| TN-01 | Auto-generated team names must be unique | No two teams receive the same auto-generated name within a game session | Unit test verifying uniqueness across 100+ generations |
| TN-02 | Names must be pronounceable | Generated names follow common phonetic patterns in English | Manual review of 50 sample names |
| TN-03 | Names must be persistent | Once assigned, a team name cannot change unless explicitly edited by a professor | Integration test across game session |
| TN-04 | Names must be stored in database | Team names must persist across server restarts | Database schema verification & restart test |
| TN-05 | Team name editing by professors | Professors can rename any team with proper validation | UI test with form validation |
| TN-06 | Team name customization by students | Students can customize their team name subject to profanity filtering | Integration test with mock profanity |
| TN-07 | Name validation | Names must be 3-30 alphanumeric characters | Validation test with boundary cases |
| TN-08 | Profanity filtering | Names containing profanity are rejected | Test against profanity wordlist |

### Team Name Customization UI

| ID | Requirement | Acceptance Criteria | Testing Method |
|----|-------------|---------------------|----------------|
| UI-01 | Edit form accessibility | Name editing form must be keyboard navigable and screen reader compatible | WCAG compliance test |
| UI-02 | Real-time validation | Form provides immediate feedback on invalid names | UI test with various inputs |
| UI-03 | Confirmation on save | Users must confirm team name changes | UI flow verification |
| UI-04 | Error display | Validation errors clearly displayed near relevant field | Visual verification |
| UI-05 | Success feedback | Clear indication when name is successfully changed | UI state verification |

## Prize Logic

### Achievement System

| ID | Requirement | Acceptance Criteria | Testing Method |
|----|-------------|---------------------|----------------|
| PZ-01 | GDP growth achievement | Prize awarded when GDP growth exceeds 8% for 3 consecutive rounds | Unit test for condition triggering |
| PZ-02 | Tech leadership prize | Prize for highest TFP growth across all teams | Integration test with multi-team scenario |
| PZ-03 | Sustainable growth prize | Prize for balanced growth with low inequality metrics | Math verification of formula |
| PZ-04 | Crisis management award | Prize for recovering from negative shock events | Event simulation test |
| PZ-05 | Export champion award | Prize for highest cumulative exports | Cumulative value calculation test |
| PZ-06 | Prize idempotency | Each prize type can only be awarded once per team per game | Unit test for duplicate awards |
| PZ-07 | Prize persistence | Awarded prizes must be stored and retrievable after server restart | Database persistence test |
| PZ-08 | Prize notification | Teams must receive real-time notification when awarded a prize | Socket event test |

### Prize Distribution Rules

| ID | Requirement | Acceptance Criteria | Testing Method |
|----|-------------|---------------------|----------------|
| PD-01 | Prize concurrency protection | If multiple teams qualify simultaneously, all receive the prize | Race condition simulation |
| PD-02 | Prize calculation timing | Prizes calculated only at end of round, not mid-round | Timing verification test |
| PD-03 | Prize calculation order | Prizes evaluated in predefined priority order | Order verification test |
| PD-04 | Prize effects | Each prize provides specific in-game bonuses | Effect application test |
| PD-05 | Prize documentation | All prize conditions and effects fully documented in UI | Documentation audit |
| PD-06 | Prize history | Complete history of prizes awarded viewable by professors | Admin panel verification |

## Prize Effects Implementation

| ID | Requirement | Acceptance Criteria | Testing Method |
|----|-------------|---------------------|----------------|
| PE-01 | TFP boost | GDP growth prize provides +5% TFP | Math verification |
| PE-02 | FDI attractiveness | Tech leadership prize improves capital inflow by 10% | Integration test |
| PE-03 | Consumption bonus | Sustainable growth prize increases consumption utility | Effect verification |
| PE-04 | Shock resistance | Crisis management award reduces impact of negative events by 15% | Shock simulation test |
| PE-05 | Trade bonus | Export champion award improves terms of trade | Price calculation test |
| PE-06 | Effect stacking | Multiple prize effects stack properly without errors | Multi-prize test |
| PE-07 | Effect persistence | Prize effects remain active for specified duration | Game state verification |

## Event Triggering Criteria

| ID | Requirement | Acceptance Criteria | Testing Method |
|----|-------------|---------------------|----------------|
| EV-01 | Event randomization | Event occurrence has appropriate probability distribution | Statistical test of 1000 simulations |
| EV-02 | WTO accession event | Triggers based on specific year or condition | Condition verification test |
| EV-03 | Financial crisis event | Can trigger with appropriate probabilities | Probability verification |
| EV-04 | Natural disaster event | Affects specific regions more than others | Regional impact test |
| EV-05 | Technology breakthrough | Occurs with higher probability for teams with high R&D | Conditional probability test |
| EV-06 | Event mutual exclusivity | Cannot have conflicting events in same round | Conflict test |
| EV-07 | Event persistence | Events with duration effects persist properly | Multi-round test |
| EV-08 | Event recovery | Teams can recover from negative events through strategy | Recovery strategy test | 