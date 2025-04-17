/**
 * API utility for fetching game state and team stats.
 * Replace endpoint URLs with your backend API routes.
 */

// Example: GET /api/game-state
export async function getGameState() {
  const response = await fetch('/api/game-state'); // TODO: update endpoint
  if (!response.ok) throw new Error('Failed to fetch game state');
  return response.json();
}

// Example: GET /api/team-stats
export async function getTeamStats(teamId) {
  const response = await fetch(`/api/team-stats/${teamId}`); // TODO: update endpoint
  if (!response.ok) throw new Error('Failed to fetch team stats');
  return response.json();
} 